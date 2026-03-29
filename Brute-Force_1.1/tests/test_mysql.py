import unittest
from src.modules.mysql import login_mysql

class TestMySQL(unittest.TestCase):
    def test_import(self):
        self.assertTrue(callable(login_mysql))
    def test_invalid_connection(self):
        self.assertFalse(login_mysql('127.0.0.1', 'user', 'pass', puerto=3306, timeout=2))
