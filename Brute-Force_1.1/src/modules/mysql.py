# src/modules/mysql.py

import pymysql

def login_mysql(ip, usuario, password, puerto=3306, timeout=6):
    try:
        conn = pymysql.connect(host=ip, user=usuario, password=password, port=puerto, connect_timeout=timeout)
        conn.close()
        return True
    except Exception:
        return False
