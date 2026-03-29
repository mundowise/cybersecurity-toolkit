# src/modules/nmap.py

import nmap

def login_nmap(ip, usuario, password, puerto=80, timeout=6):
    try:
        nm = nmap.PortScanner()
        nm.scan(ip, str(puerto))
        return nm[ip].has_tcp(puerto)
    except Exception:
        return False
