import os
import sys
import time
from modules.watcher import start_watcher
from modules.persistence import persist_multicopy, get_system_paths

def test_watcher_recovers_deleted_file(tmp_path):
    # Simula persistencia
    persist_multicopy()
    paths = get_system_paths()
    bin_path = os.path.abspath(sys.argv[0])
    start_watcher()  # Lanza watcher
    # Borra una copia
    for p in paths:
        if os.path.exists(p):
            os.remove(p)
            break
    time.sleep(15)  # Espera al watcher
    restored = any(os.path.exists(p) for p in paths)
    assert restored
