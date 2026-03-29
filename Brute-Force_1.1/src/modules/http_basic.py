# src/modules/http_basic.py

import requests
from src.core.utils import contiene_captcha, analizar_respuesta_web

def login_web_basic(url, usuario, password, otp_field=None, otp_code=None, http_headers=None, http_cookies=None, http_useragent=None, patrones_bloqueo=None, timeout=6, **kwargs):
    try:
        headers = http_headers or {}
        if http_useragent:
            headers['User-Agent'] = http_useragent
        cookies = http_cookies or {}
        r = requests.get(url, auth=(usuario, password), headers=headers, cookies=cookies, timeout=timeout)
        if contiene_captcha(r.text):
            return "CAPTCHA"
        match_bloqueo = analizar_respuesta_web(r.text, patrones_bloqueo)
        if match_bloqueo:
            return f"BLOQUEO:{match_bloqueo}"
        return r.status_code == 200
    except Exception:
        return False
