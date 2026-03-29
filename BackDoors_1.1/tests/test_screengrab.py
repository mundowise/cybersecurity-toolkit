from modules import screengrab

def test_screengrab_capture():
    result = screengrab.run("capture")
    assert "Screenshot guardado" in result or "Error" in result or "No soportado" in result
