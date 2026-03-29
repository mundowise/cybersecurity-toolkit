import unittest
from src.modules.winrm import login_winrm

class TestWinRM(unittest.TestCase):
    def test_import(self):
        self.assertTrue(callable(login_winrm))
    def test_invalid_connection(self):
        self.assertFalse(login_winrm('127.0.0.1', 'user', 'pass', puerto=5985, timeout=2))
