import logging
from scapy.all import RadioTap
from core.packets.dot11 import Dot11Frame


class PacketParser:
    """
    Parses raw 802.11 frames into structured events.
    """

    def __init__(self):
        self.log = logging.getLogger(self.__class__.__name__)

    def _parse_elements(self, payload: bytes) -> tuple[str, int | None]:
        ssid = ''
        channel = None
        idx = 0
        while idx + 2 <= len(payload):
            eid = payload[idx]
            length = payload[idx + 1]
            if idx + 2 + length > len(payload):
                break
            data = payload[idx + 2: idx + 2 + length]
            if eid == 0:
                ssid = data.decode('utf-8', errors='ignore') or ''
            elif eid == 3 and length >= 1:
                channel = data[0]
            idx += 2 + length
        return ssid, channel

    def parse(self, pkt) -> dict | None:
        try:
            signal = getattr(pkt, 'dBm_AntSignal', None)
            raw = bytes(pkt[RadioTap].payload) if pkt.haslayer(RadioTap) else bytes(pkt)
            frame = Dot11Frame.parse(raw)
            ftype = frame['type']
            subtype = frame['subtype']
            payload = frame.get('payload', b'')
            if ftype == 'Management' and subtype in ('Beacon', 'Probe Response'):
                ssid, channel = self._parse_elements(payload)
                return {
                    'protocol': 'beacon',
                    'bssid': frame['addr2'],
                    'ssid': ssid,
                    'channel': channel,
                    'signal': signal,
                    'payload': payload
                }
            if ftype == 'Data':
                return {
                    'protocol': 'data',
                    'src': frame['addr2'],
                    'dst': frame['addr1'],
                    'bssid': frame['addr3'],
                    'payload': payload
                }
        except Exception as e:
            self.log.debug(f"PacketParser error: {e}")
        return None


    
