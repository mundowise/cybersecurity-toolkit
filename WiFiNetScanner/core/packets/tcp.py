"""
WiFiNetScanner - TCP Packet Module
Author: WiFiNetScanner Team

This module provides:
    - Construction of custom TCP packets (SYN, FIN, XMAS, etc.)
    - Parsing of raw TCP segments (from sniffer or custom sockets)
    - Checksum and option field handling for advanced attacks/defenses

Implements RFC 793 and common extensions.
"""

import struct
from utils.net_helpers import checksum

class TCPPacket:
    """
    Represents a TCP packet/segment with methods to build and parse.
    """

    def __init__(self, src_port: int, dst_port: int, seq: int = 0, ack: int = 0,
                 data_offset: int = 5, reserved: int = 0, flags: int = 0x02,  # SYN
                 window: int = 8192, urgent_ptr: int = 0, payload: bytes = b"",
                 options: bytes = b"", src_ip: str = None, dst_ip: str = None):
        """
        Args:
            src_port (int): Source port
            dst_port (int): Destination port
            seq (int): Sequence number
            ack (int): Acknowledgement number
            data_offset (int): Header length (in 32-bit words)
            reserved (int): Reserved (must be 0)
            flags (int): TCP flags (bitmask)
            window (int): Window size
            urgent_ptr (int): Urgent pointer
            payload (bytes): Data to send
            options (bytes): TCP options (raw)
            src_ip (str): For checksum (required for raw)
            dst_ip (str): For checksum (required for raw)
        """
        self.src_port = src_port
        self.dst_port = dst_port
        self.seq = seq
        self.ack = ack
        self.data_offset = data_offset  # default: 5 (no options)
        self.reserved = reserved
        self.flags = flags
        self.window = window
        self.urgent_ptr = urgent_ptr
        self.payload = payload
        self.options = options
        self.src_ip = src_ip
        self.dst_ip = dst_ip

    def build(self) -> bytes:
        """
        Build the raw TCP segment, including header, options and payload.
        Returns:
            bytes: Raw TCP segment.
        """
        offset_res_flags = (self.data_offset << 12) | (self.reserved << 6) | self.flags
        # TCP header (without checksum)
        header = struct.pack("!HHLLHHHH",
                             self.src_port,
                             self.dst_port,
                             self.seq,
                             self.ack,
                             offset_res_flags,
                             self.window,
                             0,  # Checksum placeholder
                             self.urgent_ptr)
        tcp_segment = header + self.options + self.payload
        # Pseudo-header for checksum
        if self.src_ip and self.dst_ip:
            pseudo_header = self._build_pseudo_header(len(tcp_segment))
            chksum = checksum(pseudo_header + tcp_segment)
            # Insert checksum
            header = struct.pack("!HHLLHHHH",
                                 self.src_port,
                                 self.dst_port,
                                 self.seq,
                                 self.ack,
                                 offset_res_flags,
                                 self.window,
                                 chksum,
                                 self.urgent_ptr)
            tcp_segment = header + self.options + self.payload
        return tcp_segment

    def _build_pseudo_header(self, tcp_length: int) -> bytes:
        """Build the IPv4 pseudo-header for TCP checksum calculation."""
        import socket
        return struct.pack("!4s4sBBH",
                           socket.inet_aton(self.src_ip),
                           socket.inet_aton(self.dst_ip),
                           0, 6, tcp_length)

    @staticmethod
    def parse(raw: bytes):
        """
        Parse a raw TCP segment.
        Args:
            raw (bytes): Raw TCP segment (min 20 bytes).
        Returns:
            dict: Parsed TCP fields.
        """
        if len(raw) < 20:
            raise ValueError("TCP segment too short")
        header = struct.unpack("!HHLLHHHH", raw[:20])
        data_offset = (header[4] >> 12) & 0xF
        flags = header[4] & 0x3F
        options = raw[20:data_offset*4] if data_offset > 5 else b""
        payload = raw[data_offset*4:]
        return {
            "src_port": header[0],
            "dst_port": header[1],
            "seq": header[2],
            "ack": header[3],
            "data_offset": data_offset,
            "flags": flags,
            "window": header[5],
            "checksum": header[6],
            "urgent_ptr": header[7],
            "options": options,
            "payload": payload
        }

    @staticmethod
    def flags_to_str(flags: int) -> str:
        """Convert flag bits to string (e.g., 'SYN,ACK')."""
        flag_names = ["FIN", "SYN", "RST", "PSH", "ACK", "URG"]
        return ",".join([name for i, name in enumerate(flag_names) if flags & (1 << i)])

# Example usage:
# tcp_syn = TCPPacket(src_port=40000, dst_port=80, seq=0, flags=0x02, src_ip="10.0.0.1", dst_ip="10.0.0.2")
# raw = tcp_syn.build()
# parsed = TCPPacket.parse(raw)
