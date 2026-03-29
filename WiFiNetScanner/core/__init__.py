"""
WiFiNetScanner - Core Package

This package contains the core engine of WiFiNetScanner, including:
- Packet sniffing and processing
- Interface drivers (WiFi, Ethernet)
- Network scanning logic
- Protocol handling and parsers

All security-critical logic, high-performance networking routines,
and extensibility hooks for advanced modules are implemented here.

Modules:
    - packet_sniffer: High-performance raw packet capture
    - wifi_driver: Native WiFi interface management and mode control
    - network_scanner: Multi-method network scanner (ARP, ICMP, TCP, UDP)
    - packet_parser: 802.11, TCP/IP, and application protocol dissection

Do not import or initialize external plugins here. Only the core engine.
"""

# Optionally, pre-import key classes for top-level access:
# from .packet_sniffer import PacketSniffer
# from .wifi_driver import WiFiDriver
# from .network_scanner import NetworkScanner
# from .packet_parser import PacketParser
