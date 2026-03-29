import pytest
from scapy.all import RadioTap, Dot11, Dot11Beacon, Dot11Elt
from core.packet_parser import PacketParser

@pytest.fixture
def parser():
    return PacketParser()

def create_beacon(ssid: str, channel: int):
    pkt = RadioTap()/Dot11(type=0, subtype=8, addr2="00:11:22:33:44:55")
    pkt = pkt/\
        Dot11Beacon()/\
        Dot11Elt(ID=0, info=ssid.encode())/\
        Dot11Elt(ID=3, info=bytes([channel]))
    pkt.dBm_AntSignal = -40
    return pkt

def test_parse_beacon(parser):
    ssid = "TestSSID"
    channel = 6
    pkt = create_beacon(ssid, channel)
    info = parser.parse(pkt)
    assert info['protocol'] == 'beacon'
    assert info['ssid'] == ssid
    assert info['channel'] == channel
    assert info['signal'] == -40

def test_parse_data_frame(parser):
    pkt = RadioTap()/Dot11(type=2, addr1="AA:BB:CC:DD:EE:FF", addr2="11:22:33:44:55:66", addr3="00:11:22:33:44:55")
    info = parser.parse(pkt)
    assert info['protocol'] == 'data'
    assert info['src'] == "11:22:33:44:55:66"
    assert info['dst'] == "AA:BB:CC:DD:EE:FF"
    assert info['bssid'] == "00:11:22:33:44:55"