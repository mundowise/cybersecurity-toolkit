# src/modules/ftp.py

import ftplib

def login_ftp(ip, usuario, password, puerto=21, timeout=6):
    try:
        ftp = ftplib.FTP()
        ftp.connect(ip, puerto, timeout=timeout)
        ftp.login(usuario, password)
        ftp.quit()
        return True
    except Exception:
        return False
