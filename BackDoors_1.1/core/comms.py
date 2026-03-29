# core/comms.py

import socket
from core.aes_crypto import encrypt_data, decrypt_data
from core.config import SOCKET_TIMEOUT, BUFFER_SIZE, USE_TOR_SOCKS, TOR_SOCKS_HOST, TOR_SOCKS_PORT

try:
    import socks  # PySocks, para soporte de proxy TOR
except ImportError:
    socks = None  # Si no está instalado, se puede usar solo conexión directa

def send_encrypted(sock, data: bytes):
    enc = encrypt_data(data)
    sock.sendall(len(enc).to_bytes(4, "big") + enc)

def recv_encrypted(sock):
    rawlen = recv_n(sock, 4)
    if not rawlen:
        return None
    size = int.from_bytes(rawlen, "big")
    enc = recv_n(sock, size)
    if enc is None:
        return None
    return decrypt_data(enc)

def recv_n(sock, n):
    data = b""
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def setup_socket_server(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(10)
    return s

def setup_socket_client(host, port, use_socks=USE_TOR_SOCKS):
    """
    Si use_socks es True (por defecto), conecta usando el proxy SOCKS5 de TOR embebido.
    Si es False, conecta directo (para debug/desarrollo).
    """
    if use_socks:
        if not socks:
            raise ImportError("PySocks no está instalado. Ejecuta: pip install pysocks")
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS5, TOR_SOCKS_HOST, TOR_SOCKS_PORT)
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(SOCKET_TIMEOUT)
    s.connect((host, port))
    return s


