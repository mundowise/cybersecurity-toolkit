"""
WiFiNetScanner - Real-Time Analyzer Pipeline
Author: WiFiNetScanner Team

Pipeline for real-time protocol analysis, reporting, and alerting.
- Identifies packet type/protocol (Ethernet, ARP, IP, TCP, UDP, 802.11, DNS, HTTP, TLS)
- Parses using core protocol modules
- Generates structured events for logging, reporting, UI or SIEM
- Ready for plugins, heuristics, AI/ML integration
"""

import logging

from core.packet_parser import PacketParser
from core.packets.arp import ARPPacket
from core.packets.icmp import ICMPPacket
from core.packets.tcp import TCPPacket
from core.packets.udp import UDPPacket
from core.packets.dot11 import Dot11Frame
from core.packets.dns import DNSPacket
from core.packets.http import HTTPPacket
from core.packets.tls import TLSPacket
from core.alerts import AlertEngine, AlertRule, arp_spoofing_rule, icmp_scan_rule, suspicious_http_rule

class Analyzer:
    """
    Real-time analyzer for parsed packets.
    Can be used as a callback from the sniffer.
    """

    def __init__(self):
        self.log = logging.getLogger("WiFiNetScanner.Analyzer")

    def process(self, packet_data: bytes, metadata: dict) -> dict:
        """
        Analyze a raw packet and generate a structured event.
        Args:
            packet_data (bytes): Raw packet from sniffer.
            metadata (dict): Sniffer-provided metadata (interface, timestamp, etc.)
        Returns:
            dict: Structured event for reporting/logging.
        """
        report = {
            "timestamp": metadata.get("timestamp"),
            "interface": metadata.get("interface"),
            "src_addr": metadata.get("src_addr"),
            "layers": {},
            "alerts": [],
        }
        try:
            parser = PacketParser(packet_data)
            parsed = parser.parse()
            report["layers"].update(parsed)

            # Protocol-based analysis
            net = parsed.get("network_layer")
            trans = parsed.get("transport_layer")

            # ARP analysis
            if net and net.get("type") == "arp":
                arp = ARPPacket.parse(packet_data[14:42])  # Ethernet + ARP
                report["layers"]["arp"] = arp
                # Simple ARP spoofing detection can be added here

            # ICMP analysis
            if trans and trans.get("type") == "icmp":
                icmp = ICMPPacket.parse(packet_data[34:])  # Ethernet + IP header
                report["layers"]["icmp"] = icmp
                if ICMPPacket.is_echo_request(icmp):
                    report["alerts"].append("ICMP Echo Request detected")
                if ICMPPacket.is_echo_reply(icmp):
                    report["alerts"].append("ICMP Echo Reply detected")

            # TCP/UDP analysis
            if trans and trans.get("type") == "tcp":
                tcp = TCPPacket.parse(packet_data[34:])  # Ethernet + IP
                report["layers"]["tcp"] = tcp
                # HTTP/TLS detection (basic)
                payload = tcp.get("payload", b"")
                if payload.startswith(b"GET ") or payload.startswith(b"POST ") or payload.startswith(b"HTTP/"):
                    http = HTTPPacket(payload)
                    report["layers"]["http"] = http.summary()
                elif payload.startswith(b"\x16\x03"):  # TLS handshake
                    tls = TLSPacket(payload)
                    report["layers"]["tls"] = tls.summary()
            if trans and trans.get("type") == "udp":
                udp = UDPPacket.parse(packet_data[34:])  # Ethernet + IP
                report["layers"]["udp"] = udp
                payload = udp.get("payload", b"")
                # DNS detection
                if len(payload) > 10 and (udp["src_port"] == 53 or udp["dst_port"] == 53):
                    dns = DNSPacket(payload)
                    report["layers"]["dns"] = dns.summary()
            # 802.11 analysis (if interface is monitor)
            if parsed["link_layer"] and parsed["link_layer"].get("type") == "802.11":
                dot11 = Dot11Frame.parse(packet_data)
                report["layers"]["dot11"] = dot11

            # Place for custom plugins/AI/heuristics

        except Exception as e:
            self.log.error(f"Analyzer error: {e}")
            report["alerts"].append(f"Parsing error: {e}")

        return report

# Ejemplo de integración en sniffer:
# analyzer = Analyzer()
# sniffer.set_packet_handler(analyzer.process)
