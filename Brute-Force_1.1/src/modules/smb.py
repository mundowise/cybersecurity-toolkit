# src/modules/smb.py

from smb.SMBConnection import SMBConnection

def login_smb(ip, usuario, password, puerto=445, timeout=6):
    try:
        conn = SMBConnection(usuario, password, "brute_force", "SMB_SERVER", use_ntlm_v2=True)
        conn.connect(ip, puerto, timeout=timeout)
        conn.close()
        return True
    except Exception:
        return False
