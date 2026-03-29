import unittest
from src.core.logger import log_exito, log_error, log_resultado_general
import os

class TestLogger(unittest.TestCase):
    def test_log_exito(self):
        log_exito('prueba', 'host', 'usuario', 'pass')
        self.assertTrue(os.path.isfile('resultados_exitos.csv'))
    def test_log_error(self):
        log_error('prueba', 'host', 'usuario', 'pass', 'error')
        self.assertTrue(os.path.isfile('resultados_errores.csv'))
    def test_log_resultado_general(self):
        log_resultado_general('prueba', 'host', 'usuario', 'pass', 'resultado')
        self.assertTrue(os.path.isfile('resultados_general.csv'))

