# core/anti_vm.py

import psutil
from core.config import BLACKLIST_PROCESOS_VM

def is_vm():
    for proc in psutil.process_iter(['name']):
        try:
            nombre = proc.info['name'].lower()
            for blacklist in BLACKLIST_PROCESOS_VM:
                if blacklist.lower() in nombre:
                    return True
        except Exception:
            continue
    return False

def kill_if_vm():
    if is_vm():
        exit(0)
