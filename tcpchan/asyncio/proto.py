#!/usr/bin/env python

import asyncio
import logging

from ..core.conn import ClientConnection, ServerConnection
from ..core.evt import (ChannelClosed, ChannelCreated, DataTransmit,
                        HandshakeFailed, HandshakeSuccess)


class TCPChanBaseProtocol(asyncio.Protocol):
    """ TCP Channel Base Protocol

        Base protocol for the TCPChannelServerProtocol and TCPChannelClientProtocol
    
        Attributes:
            channel_factory (callable): a factory function to create new channel.
            logger (logging.Logger): optional, logging utility
            handshake_magic (int): optional, magic number to use during handshake
    """

    def __init__(
        self, channel_factory, logger=None, handshake_magic=None, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

        if logger:
            self._logger = logger
        else:
            self._logger = logging.getLogger(type(self).__name__)

        if not callable(channel_factory):
            raise TypeError("channel factory must be a callable.")

        self._handshake_magic = handshake_magic
        self._channel_factory = channel_factory

    def _event_handler(self):
        while True:
            ev = self._tcpchan.next_event()
            self._logger.debug("Event %s received.", ev)

            if ev is None:
                break

            if type(ev) == DataTransmit:
                self._transport.write(ev.payload)

            elif type(ev) == ChannelCreated:
                self.channel_created(ev.channel)

            elif type(ev) == HandshakeSuccess:
                self.handshake_success()

            elif type(ev) == ChannelClosed:
                self.channel_closed(ev.channel_id)

            elif type(ev) == HandshakeFailed:
                self.handshake_failed(self, reason=ev.reason)

    def connection_made(self, transport):
        self._transport = transport
        self._tcpchan.connection_established()

    def data_received(self, data):
        data = memoryview(data)
        self._tcpchan.data_received(data)

    def create_channel(self):
        """ Create new channel
        
            Calling this method creates a logical transmssion channel, and
            send a channel creation request to the other end of the connection.

            Returns:
                new_channel (Channel): Newly created channel
        """
        new_channel = self._tcpchan.create_channel()
        self._logger.debug("Channel %d is created.", new_channel.channel_id)

        return new_channel

    def handshake_success(self):
        """ Called when handshake success
        """

    def handshake_failed(self, reason):
        """ Called when handshake failed

            Arguments:
                reason (str): reason of handshake failure
        """

    def channel_created(self, channel):
        """ Called when channel is created from the other end of the connection

            Arguments:
                channel (Channel): newly created channel.
        """

    def channel_closed(self, channel_id):
        """ Called when channel is closed from the other end of the connection.

            Arguments:
                channel_id (int): the id of the closed channel
        """


class TCPChanServerProtocol(TCPChanBaseProtocol):
    """ TCPChan Server Protocol
        
        TCPChan protocol for server side.

        Attributes:
            channel_factory (callable): a factory function to create new channel.
            logger (logging.Logger): optional, logging utility
            handshake_magic (int): optional, magic number to use during handshake
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tcpchan = ServerConnection(
            self._channel_factory,
            event_callback=self._event_handler,
            handshake_magic=self._handshake_magic,
        )


class TCPChanClientProtocol(TCPChanBaseProtocol):
    """ TCPChan Server Protocol

        TCPChan protocol for client side.

        Attributes:
            channel_factory (callable): a factory function to create new channel.
            logger (logging.Logger): optional, logging utility
            handshake_magic (int): optional, magic number to use during handshake
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tcpchan = ClientConnection(
            self._channel_factory,
            event_callback=self._event_handler,
            handshake_magic=self._handshake_magic,
        )


__all__ = ["TCPChanClientProtocol", "TCPChanServerProtocol"]
