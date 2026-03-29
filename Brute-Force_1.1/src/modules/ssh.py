# src/modules/ssh.py

import paramiko

def login_ssh(ip, usuario, password, puerto=22, timeout=6):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, port=puerto, username=usuario, password=password, timeout=timeout)
        client.close()
        return True
    except Exception:
        return False
