from PyQt6.QtWidgets import QApplication
from gui import GodFatherApp
import sys
import logging

# Configurar logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    logging.info("Iniciando aplicación")
    app = QApplication(sys.argv)
    window = GodFatherApp()
    window.show()
    sys.exit(app.exec())