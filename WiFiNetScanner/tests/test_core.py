"""
WiFiNetScanner - Core Module Tests
Author: WiFiNetScanner Team

Unit and integration tests for core modules:
    - PacketSniffer
    - WiFiDriver
    - NetworkScanner
    - PacketParser

Run with: pytest tests/
"""

import pytest

# Example test for PacketSniffer (mocked, as real sniffing requires root/hardware)
def test_packet_sniffer_initialization():
    from core.packet_sniffer import PacketSniffer
    sniffer = PacketSniffer(interface="lo", mode="managed")
    assert sniffer.interface == "lo"
    assert sniffer.mode == "managed"
    assert not sniffer.is_running()

# Example test for WiFiDriver (mocked, real mode switching requires privileges)
def test_wifi_driver_initialization():
    from core.wifi_driver import WiFiDriver
    driver = WiFiDriver(interface="lo")
    assert driver.interface == "lo"

# Example test for NetworkScanner (mocked targets)
def test_network_scanner_tcp_scan():
    from core.network_scanner import NetworkScanner
    scanner = NetworkScanner(targets=["127.0.0.1"], scan_type="tcp", tcp_ports=[80], max_threads=1, timeout=0.1)
    scanner.scan()
    results = scanner.get_results()
    assert isinstance(results, list)

# Example test for PacketParser (with dummy Ethernet frame)
def test_packet_parser_ethernet_ipv4():
    from core.packet_parser import PacketParser
    # Minimal Ethernet + IPv4 header (dummy data)
    dummy_packet = b"\x01\x02\x03\x04\x05\x06" + b"\x11\x12\x13\x14\x15\x16" + b"\x08\x00" + b"\x45" + b"\x00"*31
    parser = PacketParser(dummy_packet)
    parsed = parser.parse()
    assert "link_layer" in parsed
    assert "network_layer" in parsed

# Add further tests for edge cases, error handling, and integrations
