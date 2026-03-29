# src/modules/zip.py

import zipfile

def login_zip(archivo, password, timeout=6, **kwargs):
    try:
        with zipfile.ZipFile(archivo) as zf:
            zf.extractall(pwd=password.encode())
        return True
    except Exception:
        return False
