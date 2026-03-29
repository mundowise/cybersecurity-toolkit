# src/modules/rar.py

import rarfile

def login_rar(archivo, password, timeout=6, **kwargs):
    try:
        with rarfile.RarFile(archivo) as rf:
            rf.extractall(pwd=password)
        return True
    except Exception:
        return False
