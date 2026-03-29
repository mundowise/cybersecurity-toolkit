# main.py
import ttkbootstrap
import tkinter as tk
from src.gui.main_gui import FuerzaBrutaGUI
from ttkbootstrap import Style


def main():
    root = ttkbootstrap.Window(themename="darkly")
    app = FuerzaBrutaGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
