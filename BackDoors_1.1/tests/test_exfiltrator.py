from modules import exfiltrator
import os

def test_upload_download():
    src = __file__  # Este mismo archivo
    dest = os.path.expanduser("~/.bd_logs/copy_test.py")
    res_up = exfiltrator.run("upload", src, dest)
    assert "subido" in res_up or "Error" in res_up
    res_down = exfiltrator.run("download", dest, src + ".bak")
    assert "descargado" in res_down or "Error" in res_down
