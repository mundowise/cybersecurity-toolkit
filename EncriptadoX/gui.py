import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QComboBox, QTextEdit, QProgressBar, QWidget, QCheckBox)
from PyQt6.QtGui import QPixmap, QFont, QFontDatabase
from PyQt6.QtCore import Qt, QPropertyAnimation, QTimer, QEasingCurve
from crypto import encrypt_data, decrypt_data, generate_password, save_password, load_password
from stego import load_cover_text, hide_message, extract_message
import logging
from PyQt6.QtWidgets import QInputDialog, QMessageBox

# Configurar logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

MAX_MESSAGE_LENGTH = 1000
SUPPORTED_LANGUAGES = {'en': 'English', 'es': 'Spanish', 'fr': 'French'}

class GodFatherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_dark_theme = True
        self.current_lang = 'es'
        self.translations = self.load_translations()
        self.cover_texts = self.load_cover_texts()
        self.init_ui()

    def load_translations(self):
        """Carga los archivos de traducción JSON."""
        translations = {}
        for lang_code in SUPPORTED_LANGUAGES:
            try:
                with open(f"locales/{lang_code}.json", 'r', encoding='utf-8') as f:
                    translations[lang_code] = json.load(f)
            except FileNotFoundError:
                logging.error(f"Archivo de traducción no encontrado para el idioma {lang_code}")
                translations[lang_code] = {}
        return translations

    def load_cover_texts(self):
        """Carga los textos de cobertura para todos los idiomas soportados."""
        cover_texts = {}
        for lang_code in SUPPORTED_LANGUAGES:
            try:
                cover_texts[lang_code] = load_cover_text(lang_code)
            except ValueError as e:
                logging.error(str(e))
                cover_texts[lang_code] = ["Backup cover text"]
        return cover_texts

    def translate(self, key):
        """Obtiene el texto traducido para el idioma actual."""
        return self.translations.get(self.current_lang, {}).get(key, key)

    def init_ui(self):
        """Inicializa la interfaz gráfica."""
        self.setWindowTitle(self.translate("title"))
        self.setMinimumSize(400, 600)

        # Cargar fuente Roboto Mono
        font_path = os.path.join(os.path.dirname(__file__), 'RobotoMono-Regular.ttf')
        font_family = "Courier New"
        if os.path.exists(font_path):
            try:
                db = QFontDatabase()
                font_id = db.addApplicationFont(font_path)
                if font_id != -1:
                    font_family = QFontDatabase().applicationFontFamilies(font_id)[0]
                else:
                    logging.warning("No se pudo cargar la fuente RobotoMono-Regular.ttf, usando Courier New")
            except Exception as e:
                logging.error(f"Error al cargar la fuente: {str(e)}")
                font_family = "Courier New"
        else:
            logging.warning("Fuente RobotoMono-Regular.ttf no encontrada, usando Courier New")

        # Widget central y layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Logo
        logo_layout = QHBoxLayout()
        logo_path = "logo.png"
        if os.path.exists(logo_path):
            self.logo_label = QLabel()
            pixmap = QPixmap(logo_path).scaledToHeight(100, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
            self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_layout.addWidget(self.logo_label)
        else:
            self.logo_label = QLabel(self.translate("title"))
            self.logo_label.setFont(QFont(font_family, 12, QFont.Weight.Bold))
            self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_layout.addWidget(self.logo_label)
        main_layout.addLayout(logo_layout)

        # Idioma
        lang_layout = QHBoxLayout()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(SUPPORTED_LANGUAGES.values())
        self.lang_combo.setCurrentText('Spanish')
        self.lang_combo.currentTextChanged.connect(self.on_lang_change)
        lang_layout.addWidget(self.lang_combo)
        main_layout.addLayout(lang_layout)

        # Modo
        mode_layout = QHBoxLayout()
        self.encrypt_button = QCheckBox(self.translate("encrypt"))
        self.encrypt_button.setChecked(True)
        self.decrypt_button = QCheckBox(self.translate("decrypt"))
        self.encrypt_button.toggled.connect(lambda: self.decrypt_button.setChecked(not self.encrypt_button.isChecked()))
        self.decrypt_button.toggled.connect(lambda: self.encrypt_button.setChecked(not self.decrypt_button.isChecked()))
        mode_layout.addWidget(self.encrypt_button)
        mode_layout.addWidget(self.decrypt_button)
        main_layout.addLayout(mode_layout)

        # Contraseña
        password_layout = QVBoxLayout()
        self.password_label = QLabel(self.translate("password"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(self.password_label)
        password_layout.addWidget(self.password_input)

        password_btn_layout = QHBoxLayout()
        password_btn_layout.setSpacing(5)
        self.generate_password_btn = QPushButton(self.translate("generate_password"))
        self.generate_password_btn.clicked.connect(self.generate_and_show_password)
        self.copy_password_btn = QPushButton(self.translate("copy_password"))
        self.copy_password_btn.clicked.connect(self.copy_password)
        self.copy_password_btn.setEnabled(False)
        self.load_password_btn = QPushButton(self.translate("load_password"))
        self.load_password_btn.clicked.connect(self.load_and_show_password)
        password_btn_layout.addWidget(self.generate_password_btn)
        password_btn_layout.addWidget(self.copy_password_btn)
        password_btn_layout.addWidget(self.load_password_btn)
        password_layout.addLayout(password_btn_layout)
        main_layout.addLayout(password_layout)

        # Tiempo de limpieza
        timeout_layout = QVBoxLayout()
        self.timeout_label = QLabel(self.translate("timeout"))
        self.timeout_input = QLineEdit("300000")
        timeout_layout.addWidget(self.timeout_label)
        timeout_layout.addWidget(self.timeout_input)
        main_layout.addLayout(timeout_layout)

        # Mensaje
        message_layout = QVBoxLayout()
        self.message_label = QLabel(self.translate("message"))
        self.message_input = QTextEdit()
        self.message_input.setMinimumHeight(50)
        message_layout.addWidget(self.message_label)
        message_layout.addWidget(self.message_input)
        main_layout.addLayout(message_layout)

        # Procesar
        self.process_btn = QPushButton(self.translate("process"))
        self.process_btn.clicked.connect(self.process)
        main_layout.addWidget(self.process_btn)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Salida
        output_layout = QVBoxLayout()
        self.output_label = QLabel(self.translate("result"))
        self.output_text = QTextEdit()
        self.output_text.setMinimumHeight(50)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_text)

        output_btn_layout = QHBoxLayout()
        output_btn_layout.setSpacing(5)
        self.copy_btn = QPushButton(self.translate("copy"))
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.clear_output_btn = QPushButton(self.translate("clear_output"))
        self.clear_output_btn.clicked.connect(self.clear_output)
        output_btn_layout.addWidget(self.copy_btn)
        output_btn_layout.addWidget(self.clear_output_btn)
        output_layout.addLayout(output_btn_layout)
        main_layout.addLayout(output_layout)

        # Tema
        self.theme_btn = QPushButton(self.translate("toggle_theme"))
        self.theme_btn.clicked.connect(self.toggle_theme)
        main_layout.addWidget(self.theme_btn)

        # Aplicar tema inicial y programar limpieza
        self.apply_theme()
        self.schedule_clear()

    def apply_theme(self):
        """Aplica el tema oscuro o claro con estilo hacking, sin grises."""
        if self.is_dark_theme:
            bg_color = "#000000"  # Negro
            text_color = "#FFFFFF"  # Blanco
            button_color = "#FF0000"  # Rojo
            button_text_color = "#FFFFFF"  # Blanco
            hover_color = "#CC0000"  # Rojo oscuro
        else:
            bg_color = "#FFFFFF"  # Blanco
            text_color = "#000000"  # Negro
            button_color = "#FF0000"  # Rojo
            button_text_color = "#000000"  # Negro
            hover_color = "#CC0000"  # Rojo oscuro

        # Estilo general
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {bg_color};
            }}
            QLabel, QCheckBox {{
                color: {text_color};
                font-family: 'RobotoMono', 'Courier New';
                font-size: 10pt;
                font-weight: bold;
            }}
            QLineEdit, QTextEdit {{
                background-color: {bg_color};
                color: {text_color};
                border: 2px solid {button_color};
                border-radius: 6px;
                padding: 3px;
                font-family: 'RobotoMono', 'Courier New';
                font-size: 8pt;
            }}
            QPushButton {{
                background-color: {button_color};
                color: {button_text_color};
                border: 2px solid {button_text_color};
                border-radius: 6px;
                padding: 3px;
                font-family: 'RobotoMono', 'Courier New';
                font-size: 8pt;
                font-weight: bold;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QComboBox {{
                background-color: {bg_color};
                color: {text_color};
                border: 2px solid {button_color};
                border-radius: 6px;
                padding: 3px;
                font-family: 'RobotoMono', 'Courier New';
                font-size: 8pt;
            }}
            QProgressBar {{
                background-color: {bg_color};
                border: 2px solid {button_color};
                border-radius: 6px;
                text-align: center;
                color: {text_color};
                font-family: 'RobotoMono', 'Courier New';
                font-size: 8pt;
            }}
            QProgressBar::chunk {{
                background-color: {button_color};
            }}
        """)
        
        # Borde rojo for logo in tema oscuro
        self.logo_label.setStyleSheet(f"border: {'3px solid #FF0000' if self.is_dark_theme else 'none'};")

        # Animación for botones
        for btn in [self.generate_password_btn, self.copy_password_btn, self.load_password_btn, 
                    self.process_btn, self.copy_btn, self.clear_output_btn, self.theme_btn]:
            btn.setProperty("normal_color", button_color)
            btn.setProperty("hover_color", hover_color)
            btn.animation = QPropertyAnimation(btn, b"styleSheet")
            btn.animation.setDuration(300)
            btn.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            btn.clicked.connect(lambda: self.animate_button(btn))

    def animate_button(self, button):
        """Anima el botón al pulsarlo."""
        normal_style = f"""
            background-color: {button.property("normal_color")};
            color: {button.property("normal_color")};
            border: 2px solid {button.property("normal_color")};
            border-radius: 6px;
            padding: 3px;
            font-family: 'RobotoMono', 'Courier New';
            font-size: 8pt;
            font-weight: bold;
            min-height: 20px;
        """
        hover_style = f"""
            background-color: {button.property("hover_color")};
            color: {button.property("normal_color")};
            border: 2px solid {button.property("normal_color")};
            border-radius: 6px;
            padding: 3px;
            font-family: 'RobotoMono', 'Courier New';
            font-size: 8pt;
            font-weight: bold;
            min-height: 20px;
        """
        button.animation.setStartValue(normal_style)
        button.animation.setEndValue(hover_style)
        button.animation.start()

    def on_lang_change(self, text):
        """Actualiza la interfaz al cambiar de idioma."""
        for lang_code, lang_name in SUPPORTED_LANGUAGES.items():
            if text == lang_name:
                self.current_lang = lang_code
                break
        self.setWindowTitle(self.translate("title"))
        self.logo_label.setText(self.translate("title") if not os.path.exists("logo.png") else "")
        self.encrypt_button.setText(self.translate("encrypt"))
        self.decrypt_button.setText(self.translate("decrypt"))
        self.password_label.setText(self.translate("password"))
        self.generate_password_btn.setText(self.translate("generate_password"))
        self.copy_password_btn.setText(self.translate("copy_password"))
        self.load_password_btn.setText(self.translate("load_password"))
        self.timeout_label.setText(self.translate("timeout"))
        self.message_label.setText(self.translate("message"))
        self.process_btn.setText(self.translate("process"))
        self.output_label.setText(self.translate("result"))
        self.copy_btn.setText(self.translate("copy"))
        self.clear_output_btn.setText(self.translate("clear_output"))
        self.theme_btn.setText(self.translate("toggle_theme"))
        logging.debug(f"Idioma cambiado a {self.current_lang}")

    def toggle_theme(self):
        """Alterna entre temas oscuro y claro."""
        self.is_dark_theme = not self.is_dark_theme
        self.apply_theme()
        logging.debug(f"Aplicado tema {'oscuro' if self.is_dark_theme else 'claro'}")

    def generate_and_show_password(self):
        """Genera una contraseña y la muestra brevemente."""
        password = generate_password()
        self.password_input.setText(password)
        self.copy_password_btn.setEnabled(True)
        QTimer.singleShot(5000, self.clear_password)
        logging.debug("Contraseña generada y mostrada")
        
        master_key, ok = QInputDialog.getText(self, self.translate("save_password"), self.translate("save_password_prompt"))
        if ok and master_key:
            try:
                save_password(password, master_key)
                QMessageBox.information(self, self.translate("success"), self.translate("password_saved"))
                logging.debug("Contraseña guardada en archivo")
            except Exception as e:
                QMessageBox.critical(self, self.translate("error"), f"{self.translate('error_saving_password')}: {str(e)}")
                logging.error(f"Fallo al guardar contraseña: {str(e)}")

    def load_and_show_password(self):
        """Carga una contraseña desde el archivo encriptado."""
        master_key, ok = QInputDialog.getText(self, self.translate("master_key"), self.translate("enter_master_key"), QLineEdit.EchoMode.Password)
        if ok and master_key:
            try:
                password = load_password(master_key)
                self.password_input.setText(password)
                self.copy_password_btn.setEnabled(True)
                QTimer.singleShot(5000, self.clear_password)
                QMessageBox.information(self, self.translate("success"), self.translate("password_loaded"))
                logging.debug("Contraseña cargada y mostrada")
            except Exception as e:
                QMessageBox.critical(self, self.translate("error"), f"{self.translate('error_loading_password')}: {str(e)}")
                logging.error(f"Fallo al cargar contraseña: {str(e)}")

    def clear_password(self):
        """Limpia el campo de contraseña y desactiva el botón de copiar."""
        self.password_input.clear()
        self.copy_password_btn.setEnabled(False)
        logging.debug("Contraseña limpiada de la interfaz")

    def copy_password(self):
        """Copia la contraseña actual al portapapeles."""
        password = self.password_input.text()
        if password:
            QApplication.clipboard().setText(password)
            QMessageBox.information(self, self.translate("success"), self.translate("password_copied"))
            logging.debug("Contraseña copiada al portapapeles")
        else:
            QMessageBox.critical(self, self.translate("error"), self.translate("no_password"))
            logging.error("No hay contraseña para copiar")

    def schedule_clear(self):
        """Programa la limpieza automática de entradas."""
        try:
            timeout = int(self.timeout_input.text())
            if timeout > 0:
                QTimer.singleShot(timeout, self.clear_all)
                logging.debug(f"Programada limpieza automática en {timeout/1000}s")
        except ValueError:
            QMessageBox.critical(self, self.translate("error"), self.translate("invalid_timeout"))
            logging.error("Valor de tiempo inválido ingresado")

    def process(self):
        """Procesa la encriptación o desencriptación."""
        input_data = self.message_input.toPlainText().strip()
        password = self.password_input.text()
        
        if not input_data:
            QMessageBox.critical(self, self.translate("error"), self.translate("empty_input"))
            logging.error("Entrada vacía proporcionada")
            return
        
        self.progress_bar.setVisible(True)
        try:
            if self.encrypt_button.isChecked():
                if len(input_data) > MAX_MESSAGE_LENGTH:
                    raise ValueError(self.translate("message_too_long").format(MAX_MESSAGE_LENGTH))
                if not password:
                    raise ValueError(self.translate("empty_password"))
                encrypted, _ = encrypt_data(input_data, password)
                hidden_text = hide_message(encrypted, password, self.cover_texts[self.current_lang])
                self.output_text.setText(hidden_text)
                logging.debug("Encriptación y esteganografía completadas")
            else:
                if not password:
                    raise ValueError(self.translate("empty_password"))
                encrypted = extract_message(input_data)
                decrypted = decrypt_data(encrypted, password)
                self.output_text.setText(decrypted)
                logging.debug("Desencriptación completada")
        except Exception as e:
            QMessageBox.critical(self, self.translate("error"), f"{self.translate('operation_failed')}: {str(e)}")
            logging.error(f"Operación fallida: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)

    def copy_to_clipboard(self):
        """Copia la salida al portapapeles."""
        output = self.output_text.toPlainText().strip()
        if output:
            QApplication.clipboard().setText(output)
            QMessageBox.information(self, self.translate("success"), self.translate("copied"))
            logging.debug("Salida copiada al portapapeles")
        else:
            QMessageBox.critical(self, self.translate("error"), self.translate("no_output"))
            logging.error("No hay salida para copiar")

    def clear_output(self):
        """Limpia el texto de salida."""
        self.output_text.clear()
        logging.debug("Salida limpiada manualmente")

    def clear_all(self):
        """Limpia todos los campos de entrada y salida."""
        self.password_input.clear()
        self.copy_password_btn.setEnabled(False)
        self.message_input.clear()
        self.output_text.clear()
        QMessageBox.information(self, self.translate("security"), self.translate("data_cleared"))
        self.schedule_clear()
        logging.debug("Todos los campos limpiados por inactividad")