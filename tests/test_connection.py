#!/usr/bin/env python

import unittest

try:
    from tcpchan.core.chan import Channel
    from tcpchan.core.conn import Connection
    from tcpchan.core.evt import ChannelClosed, ChannelCreated, DataTransmit
    from tcpchan.core.msg import CloseChannelRequest, CreateChannelRequest
except ImportError:
    import os
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))

    from tcpchan.core.chan import Channel
    from tcpchan.core.conn import Connection
    from tcpchan.core.evt import ChannelClosed, ChannelCreated, DataTransmit
    from tcpchan.core.msg import CloseChannelRequest, CreateChannelRequest


class TestTCPChanConnection(unittest.TestCase):
    def test_create_connection(self):
        try:
            conn = Connection(Channel)
        except Exception:
            self.fail("Failed creating connection instance with builtin channel.")

    def test_create_channel(self):
        conn = Connection(Channel)
        conn.connection_established()

        # CreateChanelRequest
        msg = CreateChannelRequest(Channel=1234)
        conn.data_received(msg.pack())

        ev = conn.next_event()

        self.assertEqual(ev.__class__, ChannelCreated)
        self.assertEqual(ev.channel_id, 1234)
        self.assertEqual(ev.channel.channel_id, 1234)

    def test_create_duplicated_channel(self):
        conn = Connection(Channel)
        conn.connection_established()

        # CreateChannelRequest
        msg = CreateChannelRequest(Channel=1234)
        conn.data_received(msg.pack())

        with self.assertRaises(Exception):
            conn.data_received(msg.pack())

    def test_close_channel_passive(self):
        conn = Connection(Channel)
        conn.connection_established()

        # CreateChannelRequest
        msg = CreateChannelRequest(Channel=1234)
        conn.data_received(msg.pack())

        # CloseChannelRequest
        msg = CloseChannelRequest(Channel=1234)
        conn.data_received(msg.pack())

        self.assertEqual(conn.get_channel(1234), None)

    def test_close_channel_active(self):
        conn = Connection(Channel)
        conn.connection_established()

        # CreateChannelRequest
        msg = CreateChannelRequest(Channel=1234)
        conn.data_received(msg.pack())
        ev = conn.next_event()  # Channel created event

        channel = ev.channel
        conn.close_channel(1234)
        ev = conn.next_event()  # Data transmission
        self.assertEqual(type(ev), DataTransmit)

        ev = conn.next_event()  # Channel Closed event
        self.assertEqual(type(ev), ChannelClosed)
        self.assertTrue(channel.is_closed)
