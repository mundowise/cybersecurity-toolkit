import unittest
from src.modules.redis import login_redis

class TestRedis(unittest.TestCase):
    def test_import(self):
        self.assertTrue(callable(login_redis))
    def test_invalid_connection(self):
        self.assertFalse(login_redis('127.0.0.1', 'pass', puerto=6379, timeout=2))
