import unittest
import tkinter as tk
from src.gui.main_gui import FuerzaBrutaGUI

class TestHashCrackerGUI(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = FuerzaBrutaGUI(self.root)

    def test_hash_crack_tab_created(self):
        self.assertIn('hash_crack', self.app.tabs)
        tab = self.app.tabs['hash_crack']
        self.assertIsNotNone(tab)
        # Verifica que existan los widgets críticos:
        self.assertTrue(hasattr(self.app, 'hash_file'))
        self.assertTrue(hasattr(self.app, 'hash_dict_file'))
        self.assertTrue(hasattr(self.app, 'hash_type'))
        self.assertTrue(hasattr(self.app, 'hash_motor'))
        self.assertTrue(hasattr(self.app, 'text_hash_result'))

    def tearDown(self):
        self.root.destroy()

if __name__ == '__main__':
    unittest.main()
