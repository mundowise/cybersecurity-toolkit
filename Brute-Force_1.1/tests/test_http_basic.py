import unittest
from src.modules.http_basic import login_http_basic

class TestHTTPBasic(unittest.TestCase):
    def test_import(self):
        self.assertTrue(callable(login_http_basic))
    def test_invalid_connection(self):
        self.assertFalse(login_http_basic('http://127.0.0.1', 'user', 'pass', timeout=2))
