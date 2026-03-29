# src/modules/winrm.py

import winrm

def login_winrm(ip, usuario, password, puerto=5985, timeout=6):
    try:
        session = winrm.Session(f'http://{ip}:{puerto}/wsman', auth=(usuario, password))
        r = session.run_cmd('whoami')
        return r.status_code == 0
    except Exception:
        return False
