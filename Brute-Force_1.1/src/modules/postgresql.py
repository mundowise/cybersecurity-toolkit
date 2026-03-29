# src/modules/postgresql.py

import psycopg2

def login_postgresql(ip, usuario, password, puerto=5432, timeout=6):
    try:
        conn = psycopg2.connect(host=ip, user=usuario, password=password, port=puerto, connect_timeout=timeout)
        conn.close()
        return True
    except Exception:
        return False
