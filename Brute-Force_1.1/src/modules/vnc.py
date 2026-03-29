# src/modules/vnc.py

import vncdotool.api

def login_vnc(ip, usuario, password, puerto=5900, timeout=6):
    try:
        client = vncdotool.api.connect(f"{ip}::{puerto}", password=password)
        client.disconnect()
        return True
    except Exception:
        return False
