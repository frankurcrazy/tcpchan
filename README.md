TCPChan
====

***TCPChan*** is a TCP connection multiplexing library that multiplexes multiple *channels* in a single TCP connection. TCPChan can boost the efficiency of the short-lived connections by eliminating the overhead of connection setup, especially in high-latency links (e.g. cross-continental links).

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
from tcpchan.core imoprt (
    HandshakeSuccess, DataTransmit,
    ChannelCreated, ChannelClosed
)
```

## LICENSE
BSD
