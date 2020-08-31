import typing
from dataclasses import dataclass


@dataclass
class BaseEvent:
    """ Base class for TCPChan events
    """


@dataclass
class HandshakeSuccess(BaseEvent):
    """ Handshake Success Event

        On handshake success event, client and server connection
        can start creating channel and tranmitting application data.
    """


@dataclass
class HandshakeFailed(BaseEvent):
    """ Handshake Failed Event

        When hanshake failed event is received, the connection should be
        shutdown immediately, the failure reason is indicated in ```reason``` field.
    """

    reason: str


@dataclass
class DataTransmit(BaseEvent):
    """ Data Transmit Event

        Data transmit event indicate the need for TX operation. The payload to be
        transmitted is indicated in the ```payload``` field.
    """

    payload: bytes


@dataclass
class ChannelClosed(BaseEvent):
    """ Channel Closed Event
        
        The event is received when a specific channel is closed. The id of the closed
        channel is indicated in the ```channel_id``` field.
    """

    channel_id: int


@dataclass
class ChannelCreated(BaseEvent):
    """ Channel Created Event
        
        The event is received upon successful creation of a channel. The id of the created
        channel and the channel instance itself are indicated in the ```channel_id``` and ```channel``` field
        respectively..
    """

    channel_id: int
    channel: typing.Any
