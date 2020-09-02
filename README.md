TCPChan
====

***TCPChan*** is a TCP connection multiplexing library that enables working with multiple *channels* in a single TCP connection. TCPChan can boost the efficiency of the short-lived connections by eliminating the overhead of connection setup, especially in high-latency links (e.g. cross-continental links).

The core part of the library is decoupled from I/O libraries so it's possible to bring your own I/O library. For convenience, an Asyncio-based protocol implementation is provided for easy integration with Asyncio applications.

Warning: TCPChan is built for fun and educational purpose, it is not fully tested, and neither is it widely deployed. Use it at your own risk.

## Guide
WIP

### Installation
WIP

#### Dependencies
1. python >= 3.7
1. fpack >= 1.0.0

### Usage
WIP

#### Channel
Inherit `tcpchan.core.chan.Channel` and implements `data_received` callback.
```python
from tcpchan.core.chan import Channel

class CustomChannel(Channel):
    def data_received(self, data):
        # Do stuff upon data reception
```

#### Connection
Create `ServerConnection` or `ClientConnection` instance upon connection establishment in server/client. And pass the channel factory to the Connection.

##### Server connection creation
```python
from tcpchan.core.conn import ServerConnection

conn = ServerConnection(lambda: CustomChannel())
```

##### Client connection creation
```python
from tcpchan.core.conn import ClientConnection

conn = ClientConnection(lambda: CustomChannel())
```

#### Events
```python
from tcpchan.core import (
    HandshakeSuccess, DataTransmit,
    ChannelCreated, ChannelClosed
)
```

#### Asyncio
TCPChan provides an Asyncio-based protocol implementation so that one can easily integrate TCPChan in their Asyncio applications.

For server-side application, `TCPChanServerProtocol` can be used, likewise, for client-side application, `TCPChanClientProtocol` can be used.

```python
import asyncio
from tcpchan.asyncio import TCPChanServerProtocol
from tcpchan.core.chan import Channel


class CustomChannel(Channel):
    def data_received(self, data):
        # Do stuff upon data reception
        ...


class MyProtocol(TCPChanServerProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._channels = {}  # Mapping for channels

    def handshake_success(self):
        # Do something on handshake success
        ...

    def handshake_failed(self, reason):
        # Do something on handshake failure
        ...

    def channel_created(self, channel):
        # Do something on channel creation
        self._channels[channel.channel_id] = channel

    def channel_closed(self, channel_id):
        # Do something when a channel is closed
        del self._channels[channel_id]


loop = asyncio.get_event_loop()


# To initialize `Protocol`, channel factory function is required.
server = await loop.create_server(
    lambda: MyProtocol(lambda: CustomChannel()),
    host="localhost",
    port=9487,
    start_serving=True,
)
loop.run_forever()
```

## LICENSE
BSD
