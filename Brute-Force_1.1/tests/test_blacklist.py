import unittest
from src.core.blacklist import add_blacklist_cred, is_blacklist_cred

class TestBlacklist(unittest.TestCase):
    def test_add_and_check(self):
        add_blacklist_cred('prueba', 'usuario', 'pass')
        self.assertTrue(is_blacklist_cred('prueba', 'usuario', 'pass'))
