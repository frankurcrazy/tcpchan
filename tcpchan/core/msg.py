from fpack import Bytes, Message, Uint8, Uint32, field_factory

TCPCHAN_OP_HANDSHAKE_REQUEST = 1
TCPCHAN_OP_HANDSHAKE_REPLY = 2
TCPCHAN_OP_CREATE_CHANNEL_REQUEST = 3
TCPCHAN_OP_CLOSE_CHANNEL_REQUEST = 4
TCPCHAN_OP_CHANNEL_PAYLOAD = 5


class BaseTCPChanMessage(Message):
    """ Base class for TCPChan messages

        Attributes:
            Fields (list): list of field
            version (int): protocol version (0)
    """

    Fields = [
        field_factory("Version", Uint8),
        field_factory("Op", Uint8),
    ]
    version = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Op = self.opcode
        self.Version = self.version


class TCPChanMessage(BaseTCPChanMessage):
    @classmethod
    def from_bytes(self, data):
        msg, processed = super().from_bytes(data)

        if msg is None:
            return None, 0

        if msg.Op == TCPCHAN_OP_HANDSHAKE_REQUEST:
            return HandshakeRequest.from_bytes(data)

        if msg.Op == TCPCHAN_OP_HANDSHAKE_REPLY:
            return HandshakeReply.from_bytes(data)

        if msg.Op == TCPCHAN_OP_CREATE_CHANNEL_REQUEST:
            return CreateChannelRequest.from_bytes(data)

        if msg.Op == TCPCHAN_OP_CLOSE_CHANNEL_REQUEST:
            return CloseChannelRequest.from_bytes(data)

        if msg.Op == TCPCHAN_OP_CHANNEL_PAYLOAD:
            return ChannelPayload.from_bytes(data)


class HandshakeRequest(BaseTCPChanMessage):
    """ Handshake Request Message

        Handshake request message is sent as the first message to start the handshake procedure.
    """

    opcode = TCPCHAN_OP_HANDSHAKE_REQUEST
    Fields = TCPChanMessage.Fields + [
        field_factory("Magic", Uint32),
    ]


class HandshakeReply(BaseTCPChanMessage):
    """ Handshake Reply Message

        Handshake reply message is sent upon reception of handshake request.
    """

    opcode = TCPCHAN_OP_HANDSHAKE_REPLY
    Fields = TCPChanMessage.Fields + [
        field_factory("Magic", Uint32),
    ]


class ChannelMessage(Message):
    Fields = TCPChanMessage.Fields + [
        field_factory("Channel", Uint32),
    ]


class CreateChannelRequest(BaseTCPChanMessage):
    """ Create Channel Request Message

        Create channel request message is sent to request channel creation at the other end of the connection
    """

    opcode = TCPCHAN_OP_CREATE_CHANNEL_REQUEST
    Fields = ChannelMessage.Fields


class CloseChannelRequest(BaseTCPChanMessage):
    """ Close Channel Request Message

        Close channel request is sent to notify the other end of the connection a closed channel.
    """

    opcode = TCPCHAN_OP_CLOSE_CHANNEL_REQUEST
    Fields = ChannelMessage.Fields


class ChannelPayload(BaseTCPChanMessage):
    """ Channel Payload Message

        Channel payload message is used for delivery of payload to a specific channel.
    """

    opcode = TCPCHAN_OP_CHANNEL_PAYLOAD
    Fields = ChannelMessage.Fields + [
        field_factory("Payload", Bytes),
    ]


__all__ = [
    "TCPChanMessage",
    "HandshakeRequest",
    "HandshakeReply",
    "CreateChannelRequest",
    "CloseChannelRequest",
    "ChannelPayload",
]
