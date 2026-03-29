from modules.camouflage import camufla_nombre_proceso, randomize_bin_name

def test_camufla_nombre_proceso_runs():
    camufla_nombre_proceso("explorer.exe")  # Solo validamos que no arroje excepción

def test_randomize_bin_name_runs(monkeypatch):
    import sys
    monkeypatch.setattr("os.execv", lambda *a, **k: None)
    randomize_bin_name()  # No debería romper
