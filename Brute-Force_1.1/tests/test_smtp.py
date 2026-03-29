import unittest
from src.modules.smtp import login_smtp

class TestSMTP(unittest.TestCase):
    def test_import(self):
        self.assertTrue(callable(login_smtp))
    def test_invalid_connection(self):
        self.assertFalse(login_smtp('127.0.0.1', 'user', 'pass', puerto=25, timeout=2))
