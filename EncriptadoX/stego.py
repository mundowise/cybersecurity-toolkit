import base64
import hashlib
import random
from typing import List
import os
import logging

# Configurar logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Caracteres de ancho cero
ZWS = '\u200B'  # Zero Width Space -> '1'
ZWNJ = '\u200C'  # Zero Width Non-Joiner -> '0'

def load_cover_text(lang: str) -> List[str]:
    """Carga el texto de cobertura para el idioma especificado."""
    file_path = f"cover_texts/{lang}.txt"
    if not os.path.exists(file_path):
        logging.error(f"Archivo de texto de cobertura no encontrado: {file_path}")
        raise ValueError(f"Archivo de texto de cobertura para el idioma '{lang}' no encontrado.")
    with open(file_path, 'r', encoding='utf-8') as f:
        texts = [p.strip() for p in f.read().split('\n') if p.strip()]
    logging.debug(f"Cargados {len(texts)} párrafos para el idioma {lang}")
    return texts

def has_enough_hidden_chars(text: str) -> bool:
    """Verifica si el texto contiene suficientes caracteres de ancho cero para un mensaje válido."""
    count = sum(1 for c in text if c in (ZWS, ZWNJ))
    enough = count >= 8
    logging.debug(f"Verificados caracteres ocultos: {count} encontrados, {'suficiente' if enough else 'insuficiente'}")
    return enough

def hide_message(message: bytes, password: str, cover_texts: List[str]) -> str:
    """Oculta un mensaje encriptado en un texto de cobertura usando caracteres de ancho cero."""
    logging.debug("Iniciando codificación de esteganografía")
    b64_encoded = base64.urlsafe_b64encode(message).decode('ascii')
    binary = ''.join(format(byte, '08b') for byte in b64_encoded.encode('ascii'))
    
    seed = int(hashlib.sha256(password.encode()).hexdigest(), 16)
    random.seed(seed)
    cover_text = random.choice(cover_texts)
    
    hidden_text = ''
    binary_idx = 0
    for char in cover_text:
        hidden_text += char
        if binary_idx < len(binary):
            hidden_text += ZWS if binary[binary_idx] == '1' else ZWNJ
            binary_idx += 1
    while binary_idx < len(binary):
        hidden_text += ZWS if binary[binary_idx] == '1' else ZWNJ
        binary_idx += 1
    
    logging.debug("Codificación de esteganografía completada")
    return hidden_text

def extract_message(hidden_text: str) -> bytes:
    """Extrae un mensaje de un texto que contiene caracteres de ancho cero."""
    logging.debug("Iniciando decodificación de esteganografía")
    if not has_enough_hidden_chars(hidden_text):
        logging.error("Caracteres ocultos insuficientes")
        raise ValueError("El texto no contiene suficientes caracteres ocultos para formar un mensaje válido.")
    
    binary = ''
    for char in hidden_text:
        if char == ZWS:
            binary += '1'
        elif char == ZWNJ:
            binary += '0'
    
    if len(binary) % 8 != 0:
        logging.error(f"Longitud binaria {len(binary)} no es múltiplo de 8")
        raise ValueError("Datos binarios inválidos: secuencia de bytes incompleta.")
    
    try:
        b64_encoded = ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))
        decoded = base64.urlsafe_b64decode(b64_encoded)
        logging.debug("Decodificación de esteganografía exitosa")
        return decoded
    except Exception as e:
        logging.error(f"Fallo en decodificación base64: {str(e)}")
        raise ValueError("Mensaje oculto corrupto: codificación base64 inválida.")