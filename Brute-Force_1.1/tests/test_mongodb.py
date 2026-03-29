import unittest
from src.modules.mongodb import login_mongodb

class TestMongoDB(unittest.TestCase):
    def test_import(self):
        self.assertTrue(callable(login_mongodb))
    def test_invalid_connection(self):
        self.assertFalse(login_mongodb('127.0.0.1', 'user', 'pass', puerto=27017, timeout=2))
