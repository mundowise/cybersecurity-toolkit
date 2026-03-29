import unittest
from src.modules.imap import login_imap

class TestIMAP(unittest.TestCase):
    def test_import(self):
        self.assertTrue(callable(login_imap))
    def test_invalid_connection(self):
        self.assertFalse(login_imap('127.0.0.1', 'user', 'pass', puerto=143, timeout=2))
