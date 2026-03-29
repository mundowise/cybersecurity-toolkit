from modules import propagator

def test_propagator_usb():
    assert "ejecutada" in propagator.run("usb") or "Propagación" in propagator.run("usb")
