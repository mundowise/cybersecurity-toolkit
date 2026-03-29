# src/core/config.py

MAX_REINTENTOS = 3
TIMEOUT_GLOBAL = 6
BLACKLIST_TIME = 600

BLOCK_COOLDOWN_SECONDS = 10
BLOCK_COOLDOWN_MAX = 120
BLOCK_COOLDOWN_CURRENT = BLOCK_COOLDOWN_SECONDS

PROXY_TYPE_MAP = {
    "SOCKS5":  2,  # socks.SOCKS5
    "SOCKS4":  1,  # socks.SOCKS4
    "HTTP":    3,  # socks.HTTP
    "TOR":     2   # socks.SOCKS5
}

SERVICIOS = {
    "FTP": {"func": "login_ftp", "requiere_usuario": True, "puerto": 21},
    "SSH": {"func": "login_ssh", "requiere_usuario": True, "puerto": 22},
    "MYSQL": {"func": "login_mysql", "requiere_usuario": True, "puerto": 3306},
    "POSTGRESQL": {"func": "login_postgresql", "requiere_usuario": True, "puerto": 5432},
    "MSSQL": {"func": "login_mssql", "requiere_usuario": True, "puerto": 1433},
    "SMTP": {"func": "login_smtp", "requiere_usuario": True, "puerto": 25},
    "IMAP": {"func": "login_imap", "requiere_usuario": True, "puerto": 143},
    "POP3": {"func": "login_pop3", "requiere_usuario": True, "puerto": 110},
    "SMB": {"func": "login_smb", "requiere_usuario": True, "puerto": 445},
    "VNC": {"func": "login_vnc", "requiere_usuario": True, "puerto": 5900},
    "REDIS": {"func": "login_redis", "requiere_usuario": True, "puerto": 6379},
    "MONGODB": {"func": "login_mongodb", "requiere_usuario": True, "puerto": 27017},
    "TELNET": {"func": "login_telnet", "requiere_usuario": True, "puerto": 23},
    "WINRM": {"func": "login_winrm", "requiere_usuario": True, "puerto": 5985},
    "NMAP": {"func": "login_nmap", "requiere_usuario": True, "puerto": 80},
    "ZIP": {"func": "login_zip", "requiere_usuario": False, "puerto": None},
    "RAR": {"func": "login_rar", "requiere_usuario": False, "puerto": None},
    "HTTP_POST": {"func": "login_web_post", "requiere_usuario": True, "puerto": 80},
    "HTTP_BASIC": {"func": "login_web_basic", "requiere_usuario": True, "puerto": 80},
}
