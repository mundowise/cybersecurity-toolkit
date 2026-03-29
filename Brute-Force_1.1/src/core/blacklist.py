# src/core/blacklist.py

import time
from .config import BLACKLIST_TIME

blacklist_cred = {}
blacklist_ip = {}

def en_blacklist_cred(usuario, password):
    clave = (usuario or "", password or "")
    expira = blacklist_cred.get(clave, 0)
    if time.time() < expira:
        return True
    elif clave in blacklist_cred:
        del blacklist_cred[clave]
    return False

def en_blacklist_ip(ip):
    expira = blacklist_ip.get(ip, 0)
    if time.time() < expira:
        return True
    elif ip in blacklist_ip:
        del blacklist_ip[ip]
    return False

def agregar_blacklist_cred(usuario, password):
    clave = (usuario or "", password or "")
    blacklist_cred[clave] = time.time() + BLACKLIST_TIME

def agregar_blacklist_ip(ip):
    blacklist_ip[ip] = time.time() + BLACKLIST_TIME
