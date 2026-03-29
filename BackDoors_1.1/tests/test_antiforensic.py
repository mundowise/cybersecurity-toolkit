import os
import tempfile
from modules.antiforensic import limpiar_evidencia

def test_limpiar_evidencia_removes_files():
    # Crea archivo simulado de evidencia
    fd, test_file = tempfile.mkstemp(prefix="keylog_test")
    os.close(fd)
    assert os.path.exists(test_file)
    limpiar_evidencia()
    # El archivo debería ser eliminado
    assert not os.path.exists(test_file)
