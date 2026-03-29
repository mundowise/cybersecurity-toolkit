# src/modules/mssql.py

import pymssql

def login_mssql(ip, usuario, password, puerto=1433, timeout=6):
    try:
        conn = pymssql.connect(server=ip, user=usuario, password=password, port=puerto, timeout=timeout)
        conn.close()
        return True
    except Exception:
        return False
