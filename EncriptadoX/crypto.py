import base64
import secrets
import zlib
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import logging

# Configurar logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Constantes
PBKDF2_ITERATIONS = 100000
SALT_LENGTH = 16
IV_LENGTH = 12
TAG_LENGTH = 16
NONCE_LENGTH = 16

def zeroize(data: bytearray) -> None:
    """Sobrescribe datos sensibles con ceros."""
    logging.debug("Zeroizando datos sensibles")
    for i in range(len(data)):
        data[i] = 0

def is_strong_password(password: str) -> bool:
    """Verifica si la contraseña cumple con los requisitos de seguridad."""
    valid = (len(password) >= 12 and
             any(c.isupper() for c in password) and
             any(c.isdigit() for c in password))
    logging.debug(f"Verificación de contraseña: {'Válida' if valid else 'Inválida'}")
    return valid

def generate_password() -> str:
    """Genera una contraseña fuerte y única."""
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
    password = ''.join(secrets.choice(chars) for _ in range(16))
    logging.debug("Contraseña generada")
    return password

def derive_key(password: str, salt: bytes) -> bytearray:
    """Deriva una clave de encriptación a partir de la contraseña y la sal."""
    if not is_strong_password(password):
        raise ValueError("La contraseña debe tener al menos 12 caracteres e incluir mayúsculas y dígitos.")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
        backend=default_backend()
    )
    key = bytearray(kdf.derive(password.encode()))
    logging.debug("Clave de encriptación derivada")
    return key

def check_nonce(nonce: bytes) -> bool:
    """Verifica si el nonce ya ha sido usado."""
    used_nonces_file = "used_nonces.txt"
    try:
        with open(used_nonces_file, 'r') as f:
            used_nonces = f.read().splitlines()
        nonce_str = base64.urlsafe_b64encode(nonce).decode('ascii')
        if nonce_str in used_nonces:
            logging.error(f"Nonce ya usado: {nonce_str}")
            return False
        return True
    except FileNotFoundError:
        return True

def mark_nonce_used(nonce: bytes) -> None:
    """Marca un nonce como usado."""
    used_nonces_file = "used_nonces.txt"
    nonce_str = base64.urlsafe_b64encode(nonce).decode('ascii')
    with open(used_nonces_file, 'a') as f:
        f.write(nonce_str + '\n')
    logging.debug(f"Nonce marcado como usado: {nonce_str}")

def encrypt_data(message: str, password: str) -> tuple[bytes, bytes]:
    """Encripta un mensaje usando AES-256-GCM con un nonce de un solo uso."""
    logging.debug("Iniciando encriptación")
    compressed = zlib.compress(message.encode())
    salt = secrets.token_bytes(SALT_LENGTH)
    nonce = secrets.token_bytes(NONCE_LENGTH)
    key = derive_key(password, salt)
    
    iv = secrets.token_bytes(IV_LENGTH)
    encryptor = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend()).encryptor()
    ciphertext = encryptor.update(compressed) + encryptor.finalize()
    tag = encryptor.tag
    
    zeroize(key)
    logging.debug("Encriptación completada")
    return salt + nonce + iv + tag + ciphertext, salt

def decrypt_data(combined: bytes, password: str) -> str:
    """Desencripta un mensaje usando AES-256-GCM, verificando el nonce."""
    logging.debug("Iniciando desencriptación")
    if len(combined) < SALT_LENGTH + NONCE_LENGTH + IV_LENGTH + TAG_LENGTH:
        raise ValueError("Longitud de datos encriptados inválida.")
    
    salt = combined[:SALT_LENGTH]
    nonce = combined[SALT_LENGTH:SALT_LENGTH + NONCE_LENGTH]
    iv = combined[SALT_LENGTH + NONCE_LENGTH:SALT_LENGTH + NONCE_LENGTH + IV_LENGTH]
    tag = combined[SALT_LENGTH + NONCE_LENGTH + IV_LENGTH:SALT_LENGTH + NONCE_LENGTH + IV_LENGTH + TAG_LENGTH]
    ciphertext = combined[SALT_LENGTH + NONCE_LENGTH + IV_LENGTH + TAG_LENGTH:]
    
    if not check_nonce(nonce):
        raise ValueError("La contraseña ya ha sido usada para este mensaje (nonce inválido).")
    
    key = derive_key(password, salt)
    try:
        decryptor = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend()).decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        result = zlib.decompress(plaintext).decode()
        mark_nonce_used(nonce)  # Marcar nonce como usado tras desencriptación exitosa
        logging.debug("Desencriptación exitosa")
        return result
    except Exception as e:
        logging.error(f"Fallo en desencriptación: {str(e)}")
        raise ValueError("Fallo en desencriptación: Contraseña incorrecta, nonce inválido o datos corruptos.")
    finally:
        zeroize(key)

def save_password(password: str, master_key: str, filename: str = "password.enc") -> None:
    """Guarda una contraseña en un archivo encriptado."""
    logging.debug("Guardando contraseña en archivo encriptado")
    salt = secrets.token_bytes(SALT_LENGTH)
    key = derive_key(master_key, salt)
    iv = secrets.token_bytes(IV_LENGTH)
    encryptor = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend()).encryptor()
    ciphertext = encryptor.update(password.encode()) + encryptor.finalize()
    tag = encryptor.tag
    with open(filename, 'wb') as f:
        f.write(salt + iv + tag + ciphertext)
    zeroize(key)
    logging.debug("Contraseña guardada exitosamente")

def load_password(master_key: str, filename: str = "password.enc") -> str:
    """Carga una contraseña desde un archivo encriptado."""
    logging.debug("Cargando contraseña desde archivo encriptado")
    try:
        with open(filename, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        logging.error(f"Archivo {filename} no encontrado")
        raise ValueError(f"Archivo {filename} no encontrado.")
    
    if len(data) < SALT_LENGTH + IV_LENGTH + TAG_LENGTH:
        logging.error("Longitud de datos en archivo encriptado inválida")
        raise ValueError("Longitud de datos en archivo encriptado inválida.")
    
    salt = data[:SALT_LENGTH]
    iv = data[SALT_LENGTH:SALT_LENGTH + IV_LENGTH]
    tag = data[SALT_LENGTH + IV_LENGTH:SALT_LENGTH + IV_LENGTH + TAG_LENGTH]
    ciphertext = data[SALT_LENGTH + IV_LENGTH + TAG_LENGTH:]
    
    key = derive_key(master_key, salt)
    try:
        decryptor = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend()).decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        result = plaintext.decode()
        logging.debug("Contraseña cargada exitosamente")
        return result
    except Exception as e:
        logging.error(f"Fallo al cargar contraseña: {str(e)}")
        raise ValueError("Fallo al cargar contraseña: Clave maestra incorrecta o datos corruptos.")
    finally:
        zeroize(key)