import unittest
from src.modules.telnet import login_telnet

class TestTelnet(unittest.TestCase):
    def test_import(self):
        self.assertTrue(callable(login_telnet))
    def test_invalid_connection(self):
        self.assertFalse(login_telnet('127.0.0.1', 'user', 'pass', puerto=23, timeout=2))
