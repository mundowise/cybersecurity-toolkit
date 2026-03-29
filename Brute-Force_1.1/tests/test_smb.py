import unittest
from src.modules.smb import login_smb

class TestSMB(unittest.TestCase):
    def test_import(self):
        self.assertTrue(callable(login_smb))
    def test_invalid_connection(self):
        self.assertFalse(login_smb('127.0.0.1', 'user', 'pass', puerto=445, timeout=2))
