import unittest
import os
from crypto import encrypt_data, decrypt_data, generate_password, save_password, load_password
from stego import load_cover_text, hide_message, extract_message
import logging

# Configurar logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class TestCrypto(unittest.TestCase):
    def setUp(self):
        self.cover_texts = load_cover_text("es")
        self.message = "Test message"
        self.password = "SecurePass123"
        self.master_key = "MasterKey1234"

    def test_encrypt_decrypt(self):
        """Prueba la consistencia de encriptación y desencriptación."""
        logging.debug("Probando ciclo de encriptación/desencriptación")
        encrypted, _ = encrypt_data(self.message, self.password)
        decrypted = decrypt_data(encrypted, self.password)
        self.assertEqual(self.message, decrypted)

    def test_stego_roundtrip(self):
        """Prueba la codificación y decodificación de esteganografía."""
        logging.debug("Probando ciclo de esteganografía")
        encrypted, _ = encrypt_data(self.message, self.password)
        hidden_text = hide_message(encrypted, self.password, self.cover_texts)
        extracted = extract_message(hidden_text)
        decrypted = decrypt_data(extracted, self.password)
        self.assertEqual(self.message, decrypted)

    def test_invalid_password(self):
        """Prueba la desencriptación con contraseña incorrecta."""
        logging.debug("Probando contraseña inválida")
        encrypted, _ = encrypt_data(self.message, self.password)
        with self.assertRaises(ValueError):
            decrypt_data(encrypted, "WrongPass123")

    def test_weak_password(self):
        """Prueba la encriptación con contraseña débil."""
        logging.debug("Probando contraseña débil")
        with self.assertRaises(ValueError):
            encrypt_data(self.message, "weak")

    def test_generate_password(self):
        """Prueba el generador de contraseñas."""
        logging.debug("Probando generador de contraseñas")
        password = generate_password()
        self.assertTrue(len(password) == 16)
        self.assertTrue(any(c.isupper() for c in password))
        self.assertTrue(any(c.isdigit() for c in password))
        self.assertTrue(any(c in "!@#$%^&*()" for c in password))

    def test_save_load_password(self):
        """Prueba el guardado y carga de contraseña."""
        logging.debug("Probando guardado y carga de contraseña")
        password = generate_password()
        save_password(password, self.master_key, "test_password.enc")
        loaded_password = load_password(self.master_key, "test_password.enc")
        self.assertEqual(password, loaded_password)
        os.remove("test_password.enc")  # Limpieza

    def test_single_use_password(self):
        """Prueba que la contraseña sea de un solo uso."""
        logging.debug("Probando contraseña de un solo uso")
        encrypted, _ = encrypt_data(self.message, self.password)
        decrypted = decrypt_data(encrypted, self.password)
        self.assertEqual(self.message, decrypted)
        with self.assertRaises(ValueError):
            decrypt_data(encrypted, self.password)  # Debería fallar por nonce usado
        os.remove("used_nonces.txt")  # Limpieza

if __name__ == '__main__':
    unittest.main()