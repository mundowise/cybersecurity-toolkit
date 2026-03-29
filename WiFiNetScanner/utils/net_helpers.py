import ipaddress
import logging

log = logging.getLogger(__name__)


def expand_hosts(cidr: str):
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        for addr in network.hosts():
            yield str(addr)
    except ValueError as e:
        log.error(f"Invalid network '{cidr}': {e}")


def load_oui(oui_path: str) -> dict:
    from pathlib import Path
    import urllib.request
    path = Path(oui_path)
    if not path.exists():
        url = 'http://standards-oui.ieee.org/oui/oui.txt'
        urllib.request.urlretrieve(url, str(path))
    oui = {}
    for line in path.read_text().splitlines():
        if '(hex)' in line:
            parts = line.split()
            pref = parts[0].replace('-', ':').upper()
            oui[pref] = ' '.join(parts[2:]).strip()
    return oui


def get_vendor(mac: str, oui: dict) -> str:
    pref = mac.upper()[:8]
    return oui.get(pref, 'Unknown')


def guess_device_type(mac: str, ssid: str, vendor: str) -> str:
    ssid_lc = ssid.lower()
    v_lc = vendor.lower()
    if 'cisco' in v_lc or 'ap' in ssid_lc:
        return 'Enterprise AP'
    if 'tplink' in v_lc or 'tp-link' in ssid_lc:
        return 'SoHo AP/Router'
    if 'raspberry' in v_lc:
        return 'Raspberry Pi'
    if any(x in ssid_lc for x in ['iphone', 'android', 'ios']):
        return 'Smartphone'
    if any(x in v_lc for x in ['amazon', 'google', 'echo']):
        return 'IoT Device'
    return vendor


def parse_security(payload: bytes) -> str:
    # identical logic from wifi_scanner.py
    rsn = wpa = wep = wps = False
    security = []
    idx = 0
    while idx + 2 < len(payload):
        tag = payload[idx]
        length = payload[idx+1]
        data = payload[idx+2:idx+2+length]
        if tag == 48:
            rsn = True
            security.append('WPA2' if b'\x0c\x00' in data else 'WPA3')
        elif tag == 221 and b"\x00\x50\xF2\x01" in data:
            wpa = True
            security.append('WPA')
        elif tag == 61:
            wep = True
        elif tag == 221 and b"\x00\x50\xF2\x04" in data:
            wps = True
            security.append('WPS')
        idx += 2 + length
    if wep:
        security.insert(0, 'WEP')
    if not security:
        security.append('Open')
    return '/'.join(security)


def check_vuln(security: str) -> str:
    vulns = []
    if 'WEP' in security: vulns.append('WEP CRACKABLE')
    if 'WPA' in security and 'WPA2' not in security: vulns.append('WPA Weak')
    if 'WPS' in security: vulns.append('WPS Enabled')
    if 'Open' in security: vulns.append('OPEN')
    return ', '.join(vulns)