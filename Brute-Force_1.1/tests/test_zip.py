import unittest
from src.modules.zip import login_zip

class TestZIP(unittest.TestCase):
    def test_import(self):
        self.assertTrue(callable(login_zip))
    def test_invalid_file(self):
        self.assertFalse(login_zip('no-existe.zip', 'pass', timeout=2))
