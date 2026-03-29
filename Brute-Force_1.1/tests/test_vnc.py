import unittest
from src.modules.vnc import login_vnc

class TestVNC(unittest.TestCase):
    def test_import(self):
        self.assertTrue(callable(login_vnc))
    def test_invalid_connection(self):
        self.assertFalse(login_vnc('127.0.0.1', 'pass', puerto=5900, timeout=2))
