from fpack import Bytes, Message, Uint8, Uint32, field_factory

TCPCHAN_OP_HANDSHAKE_REQUEST = 1
TCPCHAN_OP_HANDSHAKE_REPLY = 2
TCPCHAN_OP_CREATE_CHANNEL_REQUEST = 3
TCPCHAN_OP_CLOSE_CHANNEL_REQUEST = 4
TCPCHAN_OP_CHANNEL_PAYLOAD = 5


class BaseTCPChanMessage(Message):
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
    opcode = TCPCHAN_OP_HANDSHAKE_REQUEST
    Fields = TCPChanMessage.Fields + [
        field_factory("Magic", Uint32),
    ]


class HandshakeReply(BaseTCPChanMessage):
    opcode = TCPCHAN_OP_HANDSHAKE_REPLY
    Fields = TCPChanMessage.Fields + [
        field_factory("Magic", Uint32),
    ]


class ChannelMessage(Message):
    Fields = TCPChanMessage.Fields + [
        field_factory("Channel", Uint32),
    ]


class CreateChannelRequest(BaseTCPChanMessage):
    opcode = TCPCHAN_OP_CREATE_CHANNEL_REQUEST
    Fields = ChannelMessage.Fields


class CloseChannelRequest(BaseTCPChanMessage):
    opcode = TCPCHAN_OP_CLOSE_CHANNEL_REQUEST
    Fields = ChannelMessage.Fields


class ChannelPayload(BaseTCPChanMessage):
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
