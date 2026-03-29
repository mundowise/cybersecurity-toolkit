import unittest
from src.modules.mssql import login_mssql

class TestMSSQL(unittest.TestCase):
    def test_import(self):
        self.assertTrue(callable(login_mssql))
    def test_invalid_connection(self):
        self.assertFalse(login_mssql('127.0.0.1', 'user', 'pass', puerto=1433, timeout=2))
