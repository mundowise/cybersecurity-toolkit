import os
import tempfile
from modules.file_protect import proteger_archivo_extremo, quitar_proteccion

def test_file_protection_and_removal():
    fd, test_file = tempfile.mkstemp()
    os.close(fd)
    proteger_archivo_extremo(test_file)
    quitar_proteccion(test_file)
    os.remove(test_file)
    assert not os.path.exists(test_file)
