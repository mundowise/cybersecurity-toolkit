import unittest
from src.brute_manager import FuerzaBrutaManager
from threading import Event

class TestFullRunMock(unittest.TestCase):
    def test_mock_run(self):
        stats = {}
        def fake_callback(*args, **kwargs): pass
        manager = FuerzaBrutaManager(
            servicio='ftp',
            objetivo='127.0.0.1',
            usuarios=['fake'],
            passwords=['fake'],
            hilos=1,
            aleatorio=False,
            usar_ia=False,
            puerto=21,
            evento_pausa=Event(),
            evento_parar=Event(),
            stats_vars=stats,
            update_stats_callback=fake_callback
        )
        # Simula el arranque de threads, pero no espera resultado real
        manager.run()
        self.assertIsInstance(manager, FuerzaBrutaManager)
