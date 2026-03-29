import unittest
from src.brute_manager import FuerzaBrutaManager
from threading import Event

class TestBruteManager(unittest.TestCase):
    def test_instance(self):
        self.assertTrue(callable(FuerzaBrutaManager))
    def test_create(self):
        manager = FuerzaBrutaManager(
            servicio='ftp',
            objetivo='127.0.0.1',
            usuarios=['admin'],
            passwords=['admin'],
            hilos=1,
            aleatorio=False,
            usar_ia=False,
            puerto=21,
            evento_pausa=Event(),
            evento_parar=Event(),
            stats_vars={},
            update_stats_callback=lambda *a, **kw: None
        )
        self.assertIsNotNone(manager)
