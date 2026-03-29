import unittest
from src.modules.ftp import login_ftp

class TestFTP(unittest.TestCase):
    def test_import(self):
        self.assertTrue(callable(login_ftp))
    def test_invalid_connection(self):
        self.assertFalse(login_ftp('127.0.0.1', 'user', 'pass', puerto=21, timeout=2))
