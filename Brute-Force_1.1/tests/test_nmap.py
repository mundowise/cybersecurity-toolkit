import unittest
from src.modules.nmap import scan_nmap

class TestNmap(unittest.TestCase):
    def test_import(self):
        self.assertTrue(callable(scan_nmap))
    def test_invalid_scan(self):
        self.assertIn(scan_nmap('127.0.0.1', 9999), ["closed", "error", "filtered"])
