#!/usr/bin/env python

import logging
import unittest

try:
    import tcpchan
except ImportError:
    import os
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))
    import tcpchan

from tcpchan.core.chan import Channel
from tcpchan.core.conn import ClientConnection, Connection, ServerConnection
from tcpchan.core.evt import (ChannelClosed, ChannelCreated, DataTransmit,
                              HandshakeFailed, HandshakeSuccess)
from tcpchan.core.msg import (CloseChannelRequest, CreateChannelRequest,
                              HandshakeReply, HandshakeRequest, TCPChanMessage)


class TestTCPChanConnection(unittest.TestCase):
    def setUp(self):
        logging.root.handlers = []
        logging.basicConfig(
            format="[%(asctime)s][%(name)s][%(levelname)s] %(message)s",
            level=logging.DEBUG,
        )

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


class TestTCPChanServerClientConnection(unittest.TestCase):
    def setUp(self):
        logging.root.handlers = []
        logging.basicConfig(
            format="[%(asctime)s][%(name)s][%(levelname)s] %(message)s",
            level=logging.DEBUG,
        )

    def test_create_connection(self):
        server_conn = ServerConnection(Channel)
        client_conn = ClientConnection(Channel)

        server_conn.connection_established()
        client_conn.connection_established()

        ev = server_conn.next_event()
        self.assertEqual(ev, None)

        # Transmission of Handshake request
        ev = client_conn.next_event()
        self.assertEqual(type(ev), DataTransmit)

        msg, _ = TCPChanMessage.from_bytes(ev.payload)
        self.assertEqual(type(msg), HandshakeRequest)

        # Transmnission of Handshake reply
        server_conn.data_received(ev.payload)
        ev = server_conn.next_event()
        self.assertEqual(type(ev), DataTransmit)

        msg, _ = TCPChanMessage.from_bytes(ev.payload)
        self.assertEqual(type(msg), HandshakeReply)
        client_conn.data_received(ev.payload)

        ev = client_conn.next_event()
        self.assertEqual(type(ev), HandshakeSuccess)
        ev = server_conn.next_event()
        self.assertEqual(type(ev), HandshakeSuccess)

    def test_create_connection_handshake_failed(self):
        server_conn = ServerConnection(Channel, handshake_magic=0x12341234)
        client_conn = ClientConnection(Channel)

        server_conn.connection_established()
        client_conn.connection_established()

        ev = server_conn.next_event()
        self.assertEqual(ev, None)

        # Transmission of Handshake request
        ev = client_conn.next_event()
        self.assertEqual(type(ev), DataTransmit)

        msg, _ = TCPChanMessage.from_bytes(ev.payload)
        self.assertEqual(type(msg), HandshakeRequest)

        # Transmnission of Handshake reply
        server_conn.data_received(ev.payload)
        ev = server_conn.next_event()
        self.assertEqual(type(ev), HandshakeFailed)
