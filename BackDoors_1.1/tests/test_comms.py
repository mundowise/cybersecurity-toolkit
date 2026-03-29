import socket
from core.comms import encrypt_data, decrypt_data

def test_encrypt_decrypt():
    data = b"test123"
    enc = encrypt_data(data)
    assert decrypt_data(enc) == data
