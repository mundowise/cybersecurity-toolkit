import unittest
from src.modules.postgresql import login_postgresql

class TestPostgreSQL(unittest.TestCase):
    def test_import(self):
        self.assertTrue(callable(login_postgresql))
    def test_invalid_connection(self):
        self.assertFalse(login_postgresql('127.0.0.1', 'user', 'pass', puerto=5432, timeout=2))
