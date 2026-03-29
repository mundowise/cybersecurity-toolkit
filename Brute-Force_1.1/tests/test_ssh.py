import unittest
from src.modules.ssh import login_ssh

class TestSSH(unittest.TestCase):
    def test_import(self):
        self.assertTrue(callable(login_ssh))
    def test_invalid_connection(self):
        self.assertFalse(login_ssh('127.0.0.1', 'user', 'pass', puerto=22, timeout=2))
