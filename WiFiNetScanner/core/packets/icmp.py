"""
WiFiNetScanner - ICMP Packet Module
Author: WiFiNetScanner Team

This module provides:
    - Construction of ICMP Echo Request and Reply packets
    - Parsing of raw ICMP packets (sniffer, IDS, forensics)
    - Utility methods for advanced ping and fingerprinting

Implements RFC 792.
"""

import struct
import os
import time

from utils.net_helpers import checksum

class ICMPPacket:
    """
    Represents an ICMP packet (Echo Request/Reply) and provides methods to build and parse.
    """

    def __init__(self, type_: int = 8, code: int = 0, identifier: int = None, seq: int = 1, payload: bytes = None):
        """
        Args:
            type_ (int): ICMP type (8 = Echo Request, 0 = Echo Reply)
            code (int): ICMP code (0 for most common cases)
            identifier (int): Identifier (unique per session, default: random)
            seq (int): Sequence number (incremented per packet)
            payload (bytes): Payload data (default: timestamp + random)
        """
        self.type_ = type_
        self.code = code
        self.identifier = identifier if identifier is not None else os.getpid() & 0xFFFF
        self.seq = seq
        if payload is None:
            ts = struct.pack("d", time.time())
            rand = os.urandom(16)
            payload = ts + rand
        self.payload = payload

    def build(self) -> bytes:
        """
        Build the ICMP packet (including header and payload).
        Returns:
            bytes: Raw ICMP packet.
        """
        header = struct.pack("!BBHHH", self.type_, self.code, 0, self.identifier, self.seq)
        chksum = checksum(header + self.payload)
        header = struct.pack("!BBHHH", self.type_, self.code, chksum, self.identifier, self.seq)
        return header + self.payload

    @staticmethod
    def parse(raw: bytes):
        """
        Parse a raw ICMP packet.
        Args:
            raw (bytes): Raw ICMP payload (minimum 8 bytes).
        Returns:
            dict: Parsed ICMP fields.
        """
        if len(raw) < 8:
            raise ValueError("ICMP packet too short")
        fields = struct.unpack("!BBHHH", raw[:8])
        return {
            "type": fields[0],
            "code": fields[1],
            "checksum": fields[2],
            "identifier": fields[3],
            "sequence": fields[4],
            "payload": raw[8:]
        }

    @staticmethod
    def is_echo_request(pkt: dict) -> bool:
        """Check if a parsed ICMP packet is an Echo Request."""
        return pkt["type"] == 8 and pkt["code"] == 0

    @staticmethod
    def is_echo_reply(pkt: dict) -> bool:
        """Check if a parsed ICMP packet is an Echo Reply."""
        return pkt["type"] == 0 and pkt["code"] == 0

# Example usage:
# icmp_req = ICMPPacket(type_=8, seq=1)
# raw = icmp_req.build()
# parsed = ICMPPacket.parse(raw)
