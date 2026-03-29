# src/modules/redis.py

import redis

def login_redis(ip, usuario, password, puerto=6379, timeout=6):
    try:
        client = redis.Redis(host=ip, port=puerto, password=password, socket_timeout=timeout)
        client.ping()
        return True
    except Exception:
        return False
