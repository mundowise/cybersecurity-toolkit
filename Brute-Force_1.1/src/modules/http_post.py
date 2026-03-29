# src/modules/http_post.py

import requests
from src.core.utils import contiene_captcha, analizar_respuesta_web

def login_web_post(url, usuario, password, otp_field=None, otp_code=None, http_headers=None, http_cookies=None, http_post_extra=None, http_useragent=None, patrones_bloqueo=None, timeout=6, **kwargs):
    try:
        data = {'username': usuario, 'password': password}
        if http_post_extra:
            data.update(http_post_extra)
        if otp_field and otp_code:
            data[otp_field] = otp_code
        headers = http_headers or {}
        if http_useragent:
            headers['User-Agent'] = http_useragent
        cookies = http_cookies or {}
        r = requests.post(url, data=data, headers=headers, cookies=cookies, timeout=timeout)
        if contiene_captcha(r.text):
            return "CAPTCHA"
        match_bloqueo = analizar_respuesta_web(r.text, patrones_bloqueo)
        if match_bloqueo:
            return f"BLOQUEO:{match_bloqueo}"
        return "bienvenido" in r.text.lower() or r.status_code == 200
    except Exception:
        return False
