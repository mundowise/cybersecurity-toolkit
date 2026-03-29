import unittest
from src.modules.pop3 import login_pop3

class TestPOP3(unittest.TestCase):
    def test_import(self):
        self.assertTrue(callable(login_pop3))
    def test_invalid_connection(self):
        self.assertFalse(login_pop3('127.0.0.1', 'user', 'pass', puerto=110, timeout=2))
