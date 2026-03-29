# src/modules/pop3.py

import poplib

def login_pop3(ip, usuario, password, puerto=110, timeout=6):
    try:
        pop = poplib.POP3(ip, puerto, timeout=timeout)
        pop.user(usuario)
        pop.pass_(password)
        pop.quit()
        return True
    except Exception:
        return False
