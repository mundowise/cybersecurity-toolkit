"""
WiFiNetScanner - Packet Processing Submodule

This subpackage contains all low-level protocol definitions,
packet structures, builders, and parsers for:
- IEEE 802.11 (WiFi) frames
- Ethernet II frames
- ARP, ICMP, TCP, UDP headers
- Protocol-specific utilities and constants

New protocols or extensions (e.g. custom attacks, fuzzers) should
be implemented here for maximum performance and code clarity.
"""
