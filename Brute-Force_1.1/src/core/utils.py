# src/core/utils.py

import string
import re

def es_valido(texto):
    caracteres_permitidos = string.ascii_letters + string.digits + string.punctuation
    return all(c in caracteres_permitidos for c in texto)

def parse_headers(headers_text):
    headers = {}
    for line in headers_text.splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            headers[k.strip()] = v.strip()
    return headers

def parse_post_data(post_text):
    data = {}
    for line in post_text.splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            data[k.strip()] = v.strip()
    return data

def contiene_captcha(texto):
    patrones = [
        "captcha", "g-recaptcha", "recaptcha", "hcaptcha", "<img", "data-sitekey", "2fa", "otp", "one time password"
    ]
    texto = texto.lower()
    return any(p in texto for p in patrones)

def analizar_respuesta_web(texto, patrones):
    if not patrones:
        return None
    texto = texto.lower()
    for p in patrones:
        if p and p in texto:
            return p
    return None
