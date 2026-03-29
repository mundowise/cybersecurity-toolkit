"""
WiFiNetScanner - UDP Packet Module
Author: WiFiNetScanner Team

This module provides:
    - Construction of UDP datagrams (for scanning, fuzzing, etc.)
    - Parsing of raw UDP segments (from sniffer or raw sockets)
    - Checksum support and payload analysis

Implements RFC 768 and common extensions.
"""

import struct
from utils.net_helpers import checksum

class UDPPacket:
    """
    Represents a UDP datagram and provides methods to build and parse.
    """

    def __init__(self, src_port: int, dst_port: int, payload: bytes = b"",
                 src_ip: str = None, dst_ip: str = None):
        """
        Args:
            src_port (int): Source port
            dst_port (int): Destination port
            payload (bytes): Data to send
            src_ip (str): For checksum (required for raw, can be None for basic)
            dst_ip (str): For checksum (required for raw, can be None for basic)
        """
        self.src_port = src_port
        self.dst_port = dst_port
        self.length = 8 + len(payload)  # UDP header is 8 bytes
        self.payload = payload
        self.src_ip = src_ip
        self.dst_ip = dst_ip

    def build(self) -> bytes:
        """
        Build the raw UDP datagram, including header and payload.
        Returns:
            bytes: Raw UDP datagram.
        """
        header = struct.pack("!HHHH",
                             self.src_port,
                             self.dst_port,
                             self.length,
                             0)  # Checksum placeholder
        udp_segment = header + self.payload
        # Pseudo-header for checksum (RFC 768)
        if self.src_ip and self.dst_ip:
            pseudo_header = self._build_pseudo_header(len(udp_segment))
            chksum = checksum(pseudo_header + udp_segment)
            header = struct.pack("!HHHH",
                                 self.src_port,
                                 self.dst_port,
                                 self.length,
                                 chksum)
            udp_segment = header + self.payload
        return udp_segment

    def _build_pseudo_header(self, udp_length: int) -> bytes:
        """Build IPv4 pseudo-header for UDP checksum."""
        import socket
        return struct.pack("!4s4sBBH",
                           socket.inet_aton(self.src_ip),
                           socket.inet_aton(self.dst_ip),
                           0, 17, udp_length)

    @staticmethod
    def parse(raw: bytes):
        """
        Parse a raw UDP datagram.
        Args:
            raw (bytes): Raw UDP datagram (min 8 bytes).
        Returns:
            dict: Parsed UDP fields.
        """
        if len(raw) < 8:
            raise ValueError("UDP datagram too short")
        header = struct.unpack("!HHHH", raw[:8])
        payload = raw[8:]
        return {
            "src_port": header[0],
            "dst_port": header[1],
            "length": header[2],
            "checksum": header[3],
            "payload": payload
        }

# Example usage:
# udp_pkt = UDPPacket(src_port=55555, dst_port=53, payload=b"\x00\x01...", src_ip="10.0.0.1", dst_ip="10.0.0.2")
# raw = udp_pkt.build()
# parsed = UDPPacket.parse(raw)
