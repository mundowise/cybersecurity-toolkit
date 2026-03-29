import os
from core import config, utils, aes_crypto, anti_vm, logger

def test_config_constants():
    assert isinstance(config.C2_HOST, str)
    assert isinstance(config.AES_KEY, bytes)
    assert len(config.AES_KEY) == 32

def test_utils_system_info():
    info = utils.system_info()
    assert isinstance(info, str)
    assert len(info) > 0

def test_admin():
    assert isinstance(utils.is_admin(), bool)

def test_logger():
    logger.log_event("TEST", "Data de test")
    fname = os.path.expanduser("~/.bd_logs/backdoors.log")
    assert os.path.exists(fname)
    with open(fname) as f:
        lines = f.readlines()
    assert any("TEST" in l for l in lines)

def test_aes_crypto():
    data = b"prueba secreta"
    enc = aes_crypto.encrypt_data(data)
    assert isinstance(enc, bytes) and len(enc) > 16
    dec = aes_crypto.decrypt_data(enc)
    assert dec == data

def test_vm_detection():
    assert isinstance(anti_vm.is_vm(), bool)
