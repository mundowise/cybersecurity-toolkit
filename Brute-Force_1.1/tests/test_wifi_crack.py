import unittest
from src.modules.wifi_crack import crack_handshake_aircrack, crack_handshake_hashcat

class TestWifiCrack(unittest.TestCase):
    def test_import(self):
        self.assertTrue(callable(crack_handshake_aircrack))
        self.assertTrue(callable(crack_handshake_hashcat))
    def test_fake_inputs(self):
        self.assertIsNone(crack_handshake_aircrack('no-file.cap', 'no-wordlist.txt'))
        self.assertIsNone(crack_handshake_hashcat('no-file.hccapx', 'no-wordlist.txt'))
