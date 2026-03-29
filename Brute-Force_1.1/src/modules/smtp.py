# src/modules/smtp.py

import smtplib

def login_smtp(ip, usuario, password, puerto=25, timeout=6):
    try:
        server = smtplib.SMTP(ip, puerto, timeout=timeout)
        server.login(usuario, password)
        server.quit()
        return True
    except Exception:
        return False
