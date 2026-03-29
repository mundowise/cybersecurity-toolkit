# src/modules/imap.py

import imaplib

def login_imap(ip, usuario, password, puerto=143, timeout=6):
    try:
        mail = imaplib.IMAP4(ip, puerto)
        mail.login(usuario, password)
        mail.logout()
        return True
    except Exception:
        return False
