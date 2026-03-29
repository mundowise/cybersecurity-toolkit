"""
WiFiNetScanner - ARP Packet Module
Author: WiFiNetScanner Team

This module provides:
    - Construction of ARP request and reply packets
    - Parsing of raw ARP packets (for sniffer, IDS, forensics)
    - Detection hooks for ARP spoofing and anomalies

Implements RFC 826.
"""

import struct
from utils.net_helpers import mac_str_to_bytes, ip_to_int, int_to_ip, mac_bytes_to_str

class ARPPacket:
    """
    Represents an ARP packet and provides methods for building and parsing.
    """

    def __init__(self, hw_type=1, proto_type=0x0800, hw_size=6, proto_size=4,
                 opcode=1, src_mac=None, src_ip=None, dst_mac=None, dst_ip=None):
        """
        Args:
            hw_type (int): Hardware type (1 for Ethernet)
            proto_type (int): Protocol type (0x0800 for IPv4)
            hw_size (int): Hardware address length (6 for MAC)
            proto_size (int): Protocol address length (4 for IPv4)
            opcode (int): 1=request, 2=reply
            src_mac (str): Source MAC address (xx:xx:xx:xx:xx:xx)
            src_ip (str): Source IP address
            dst_mac (str): Destination MAC address
            dst_ip (str): Destination IP address
        """
        self.hw_type = hw_type
        self.proto_type = proto_type
        self.hw_size = hw_size
        self.proto_size = proto_size
        self.opcode = opcode
        self.src_mac = src_mac
        self.src_ip = src_ip
        self.dst_mac = dst_mac
        self.dst_ip = dst_ip

    def build(self) -> bytes:
        """
        Build the ARP packet (without Ethernet header).
        Returns:
            bytes: Raw ARP packet.
        """
        return struct.pack(
            "!HHBBH6s4s6s4s",
            self.hw_type,
            self.proto_type,
            self.hw_size,
            self.proto_size,
            self.opcode,
            mac_str_to_bytes(self.src_mac),
            struct.pack("!I", ip_to_int(self.src_ip)),
            mac_str_to_bytes(self.dst_mac),
            struct.pack("!I", ip_to_int(self.dst_ip))
        )

    @staticmethod
    def parse(raw: bytes):
        """
        Parse a raw ARP packet.
        Args:
            raw (bytes): Raw ARP payload (28 bytes, excluding Ethernet header).
        Returns:
            dict: Parsed ARP fields.
        """
        fields = struct.unpack("!HHBBH6s4s6s4s", raw[:28])
        return {
            "hw_type": fields[0],
            "proto_type": fields[1],
            "hw_size": fields[2],
            "proto_size": fields[3],
            "opcode": fields[4],
            "src_mac": mac_bytes_to_str(fields[5]),
            "src_ip": int_to_ip(struct.unpack("!I", fields[6])[0]),
            "dst_mac": mac_bytes_to_str(fields[7]),
            "dst_ip": int_to_ip(struct.unpack("!I", fields[8])[0]),
        }

    @staticmethod
    def is_arp_spoofing(pkt1: dict, pkt2: dict) -> bool:
        """
        Detects possible ARP spoofing by comparing two ARP packets.
        Args:
            pkt1, pkt2 (dict): Parsed ARP packets.
        Returns:
            bool: True if possible spoofing detected, False otherwise.
        """
        # Classic heuristic: Same IP, different MAC = possible spoof
        return pkt1["src_ip"] == pkt2["src_ip"] and pkt1["src_mac"] != pkt2["src_mac"]

# Example usage (build and parse):
# arp_req = ARPPacket(opcode=1, src_mac="aa:bb:cc:dd:ee:ff", src_ip="192.168.1.2",
#                     dst_mac="00:00:00:00:00:00", dst_ip="192.168.1.1")
# raw = arp_req.build()
# parsed = ARPPacket.parse(raw)
