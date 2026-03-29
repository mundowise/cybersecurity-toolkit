import unittest
import importlib

MODS = [
    'ftp', 'http_basic', 'http_post', 'imap', 'mongodb', 'mssql', 'mysql', 'nmap',
    'password_ai', 'pop3', 'postgresql', 'rar', 'redis', 'smb', 'smtp', 'ssh', 
    'telnet', 'vnc', 'wifi_crack', 'winrm', 'zip'
]

class TestModulesIntegration(unittest.TestCase):
    def test_import_all_modules(self):
        for mod in MODS:
            full = f"src.modules.{mod}"
            self.assertIsNotNone(importlib.import_module(full))
