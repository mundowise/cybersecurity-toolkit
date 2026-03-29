import unittest
import importlib

class TestGUI(unittest.TestCase):
    def test_import_main_gui(self):
        gui = importlib.import_module('src.gui.main_gui')
        self.assertIsNotNone(gui)
