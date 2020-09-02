import logging


class Channel:
    """ TCPChan Channel

        The channel instance is responsible for maintaining the logical
        channels in TCPChan connection.

        Attributes:
            connection (TCPChan.core.Connection): associated TCPChan connection
            channel_id (int): id of the channel
            logger (logging.Logger): logging utility
    """

    def __init__(self, connection=None, channel_id=0, logger=None):
        self._channel_id = channel_id
        self._conn = connection
        self._closed = False

        if logger:
            self._logger = logger
        else:
            self._logger = logging.getLogger(self.__class__.__name__)

    @property
    def channel_id(self):
        return self._channel_id

    @property
    def connection(self):
        return self._conn

    def set_connection(self, connection):
        """ Associate the channel with given connection
        """
        self._conn = connection

    def set_channel_id(self, channel_id):
        """ Set the id of the channel
        """
        self._channel_id = channel_id

    def channel_created(self):
        """ Called when channel is created
        """
        self._logger.debug("Channel %d is created.", self._channel_id)

    def write_data(self, data):
        """ Send channel data to connection

            Arguments:
                data (bytes): data to send to the other end of channel
        """
        if self._closed:
            self._logger.warn("Writing data to a closed channel.")
            return

        self._conn.channel_transmit_data(self._channel_id, data)

    def data_received(self, data):
        """ Called on reception of data
            
            Arguments:
                data (bytes): received data
        """
        raise NotImplementedError

    @property
    def is_closed(self):
        """ Tell whether channel is close or not
        """
        return self._closed

    def close(self):
        """ Close the channel
        """
        if not self._closed:
            self._closed = True

            if self._conn.get_channel(self.channel_id):
                self._conn.close_channel(self.channel_id)


__all__ = ["Channel"]
