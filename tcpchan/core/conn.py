import logging
from io import BytesIO
from random import randint

from tcpchan.core.chan import Channel
from tcpchan.core.evt import (ChannelClosed, ChannelCreated, DataTransmit,
                              HandshakeFailed, HandshakeSuccess)
from tcpchan.core.msg import (ChannelPayload, CloseChannelRequest,
                              CreateChannelRequest, HandshakeReply,
                              HandshakeRequest, TCPChanMessage)

CONN_STATE_IDLE = 0
CONN_STATE_SETUP = 1
CONN_STATE_ESTABLISHED = 2
CONN_STATE_HANDSHAKE = 3
CONN_STATE_HANDSHAKE_SUCCESS = 4
CONN_STATE_HANDSHAKE_FAIL = 5

HANDSHAKE_MAGIC = 0xFEEDBACC


class BaseConnection:
    """ Base class for connection
    """

    def __init__(self, logger=None, event_callback=None):
        self._channels = {}
        self._buf = BytesIO()
        self._events = []
        self._state = CONN_STATE_IDLE
        self._event_callback = event_callback

        if self._event_callback and not callable(self._event_callback):
            raise ValueError("Expect callable event_callback.")

        if logger is not None:
            self._logger = logger
        else:
            self._logger = logging.getLogger(self.__class__.__name__)

    def connection_established(self):
        """ Called when underlying connection is established
        """
        raise NotImplementedError

    def connection_closed(self, exc):
        """ Called when underlying connection is closed

            Arguements:
                exc (Exception): exception indicating what happend
        """
        raise NotImplementedError

    def create_channel(self, channel_id=None):
        raise NotImplementedError

    def close_channel(self, channel_id=0):
        raise NotImplementedError

    def data_received(self, data):
        """ Called when underlying connection recevied new packet
            
            Arguments:
                data (bytes, memoryview): new data
        """
        raise NotImplementedError

    def next_event(self):
        """ Get next event from event queue
        """
        try:
            return self._events.pop(0)
        except IndexError:
            return None

    def add_events(self, events=[]):
        """ Add a list of events to event queue
        """
        self._events += events
        self.event_notify()

    def event_notify(self):
        """ Called when event is enqueued
        """
        if self._event_callback:
            self._event_callback()

    def close(self):
        raise NotImplementedError


class Connection(BaseConnection):
    """ TCPChan connection

        Attributes:
            channel_factory (callable): Factory function for channel creation.
            handshake_magic (int): Magic number to use during handshake
    """

    def __init__(self, channel_factory, handshake_magic=None, *arg, **kwargs):
        super().__init__(*arg, **kwargs)

        self._handlers = {
            CreateChannelRequest: self._handle_create_channel_request,
            CloseChannelRequest: self._handle_close_channel_request,
            ChannelPayload: self._handle_channel_payload,
            HandshakeRequest: self._handle_handshake_request,
            HandshakeReply: self._handle_handshake_reply,
        }

        if handshake_magic is None:
            self._magic = HANDSHAKE_MAGIC
        else:
            self._magic = handshake_magic

        self._channel_factory = channel_factory
        if not callable(self._channel_factory):
            raise ValueError("channel_factory must be callable.")

    def connection_established(self):
        """ Called on connection establishment
        """
        self._logger.debug("connection established.")
        self._state = CONN_STATE_ESTABLISHED

    def data_received(self, data):
        """ Called on data reception from network 
        """
        self._buf.write(data)

        offset = 0
        while True:
            try:
                msg, processed = TCPChanMessage.from_bytes(
                    self._buf.getbuffer()[offset:]
                )
            except ValueError:
                break

            try:
                self._handlers[msg.__class__](msg)
            except KeyError:
                self._logger.error('Unhandled message type "%s".', type(msg).__name__)
                self.close()

            offset += processed

        if offset > 0:
            newbuf = BytesIO()
            newbuf.write(self._buf.getbuffer()[offset:])
            self._buf = newbuf

    def channel_transmit_data(self, channel_id, data):
        payload = ChannelPayload(Channel=channel_id, Payload=data)

        self.add_events([DataTransmit(payload=payload.pack())])
        self._logger.debug("Scheduled data transmission from channel %d.", channel_id)

    def get_channel(self, channel_id):
        return self._channels.get(channel_id, None)

    def create_channel(self, channel_id=None):
        if not channel_id:
            channel_id = randint(0, 2 ** 32)

        while channel_id in self._channels:
            channel_id += 1

        msg = CreateChannelRequest(Channel=channel_id)
        self.add_events([DataTransmit(payload=msg.pack())])

        return self._create_channel(channel_id)

    def _create_channel(self, channel_id):
        if channel_id in self._channels:
            raise Exception(f"Duplicated channel id {channel_id}.")

        new_channel = self._channel_factory()
        new_channel.set_channel_id(channel_id)
        new_channel.set_connection(self)
        new_channel.channel_created()
        self._channels[channel_id] = new_channel

        self.add_events([ChannelCreated(channel_id=channel_id, channel=new_channel)])

        return new_channel

    def close_channel(self, channel_id):
        if self._delete_channel(channel_id):
            msg = CloseChannelRequest(Channel=channel_id)
            self.add_events(
                [
                    DataTransmit(payload=msg.pack()),
                    ChannelClosed(channel_id=channel_id),
                ]
            )

    def _delete_channel(self, channel_id):
        try:
            channel = self._channels[channel_id]
            del self._channels[channel_id]

            channel.close()
            return True
        except KeyError:
            self._logger.error("Deleting a non-existed channel %d.", channel_id)
            return False

    def _handle_create_channel_request(self, msg):
        self._logger.debug("handling create channel request.")
        self._create_channel(msg.Channel)

    def _handle_close_channel_request(self, msg):
        self._logger.debug("handling close channel request.")
        self._delete_channel(msg.Channel)

    def _handle_channel_payload(self, msg):
        self._logger.debug("handling channel payload.")
        try:
            self._channels[msg.Channel].data_received(msg.Payload)
        except KeyError:
            self._logger.error("Non-existed channel %d.", msg.Channel)

    def _handle_handshake_request(self, msg):
        self._logger.debug("handling handshake request.")

        if msg.Magic != self._magic:
            self._logger.debug("handshake failed due to mismatched magic.")
            self._state = CONN_STATE_HANDSHAKE_FAIL
            self.add_events([HandshakeFailed(reason="Mismatched magic.")])
            return

        self._logger.debug("handshake succeeded, sending reply.")
        msg = HandshakeReply(Magic=self._magic)
        self.add_events(
            [DataTransmit(payload=msg.pack()), HandshakeSuccess(),]
        )
        self._state = CONN_STATE_HANDSHAKE_SUCCESS

    def _handle_handshake_reply(self, msg):
        self._logger.debug("handling handshake reply.")

        if msg.Magic == self._magic:
            self._logger.debug("hanshake succeeded.")
            self._state = CONN_STATE_HANDSHAKE_SUCCESS
            evt = HandshakeSuccess()
        else:
            self._logger.debug("handshake failed due to mismatched magic.")
            self._state = CONN_STATE_HANDSHAKE_FAIL
            evt = HandshakeFailed(reason="Mismatched magic.")

        self.add_events([evt])


class ClientConnection(Connection):
    def connection_established(self):
        super().connection_established()
        msg = HandshakeRequest(Magic=self._magic)
        self.add_events([DataTransmit(payload=msg.pack())])
        self._state = CONN_STATE_HANDSHAKE


class ServerConnection(Connection):
    def connection_established(self):
        super().connection_established()
        self._state = CONN_STATE_HANDSHAKE


__all__ = ["Connection", "ClientConnection", "ServerConnection"]
