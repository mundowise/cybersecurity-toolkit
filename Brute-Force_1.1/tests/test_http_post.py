import unittest
from src.modules.http_post import login_http_post

class TestHTTPPost(unittest.TestCase):
    def test_import(self):
        self.assertTrue(callable(login_http_post))
    def test_invalid_connection(self):
        self.assertFalse(login_http_post('http://127.0.0.1', 'user', 'pass', timeout=2))
