# src/brute_manager.py

import threading
import random
import string
import time
from src.core.config import MAX_REINTENTOS, TIMEOUT_GLOBAL, SERVICIOS
from src.core.blacklist import en_blacklist_cred, en_blacklist_ip, agregar_blacklist_cred, agregar_blacklist_ip
from src.core.logger import log_resultado_general, log_exito, log_error

class FuerzaBrutaManager:
    def __init__(
        self, servicio, objetivo, usuarios, passwords, hilos=10, aleatorio=False,
        longitud=8, cantidad_aleatoria=10000, puerto=None, url=None, otp_field=None,
        otp_code=None, control_event=None, http_headers=None, http_cookies=None,
        http_post_extra=None, http_useragent=None, patrones_bloqueo=None, actualizar_stats=None
    ):
        self.servicio = servicio
        self.objetivo = objetivo
        self.usuarios = usuarios
        self.passwords = passwords
        self.hilos = hilos
        self.aleatorio = aleatorio
        self.longitud = longitud
        self.cantidad_aleatoria = cantidad_aleatoria
        self.puerto = puerto
        self.url = url
        self.encontrado = threading.Event()
        self.resultado = []
        self.total = 0
        self.contador = 0
        self.lock = threading.Lock()
        self.exitos = 0
        self.errores = 0
        self.intentos_hilo = {}
        self.exitos_hilo = {}
        self.errores_hilo = {}
        self.captcha_detected = threading.Event()
        self.otp_field = otp_field
        self.otp_code = otp_code
        self.control_event = control_event or StoppableEvent()
        self.http_headers = http_headers
        self.http_cookies = http_cookies
        self.http_post_extra = http_post_extra
        self.http_useragent = http_useragent
        self.patrones_bloqueo = patrones_bloqueo or []
        self.actualizar_stats = actualizar_stats
        self.t0 = time.time()
        if self.aleatorio:
            self.usuarios = self.generar_combinaciones_aleatorias(self.longitud, self.cantidad_aleatoria) if self.usuarios is None else self.usuarios
            self.passwords = self.generar_combinaciones_aleatorias(self.longitud, self.cantidad_aleatoria)
        self._rellenar_queue()

    def generar_combinaciones_aleatorias(self, longitud, cantidad):
        chars = string.ascii_letters + string.digits + string.punctuation
        return [''.join(random.choice(chars) for _ in range(longitud)) for _ in range(cantidad)]

    def _rellenar_queue(self):
        if SERVICIOS[self.servicio]['requiere_usuario']:
            todo = [(u, p) for u in self.usuarios for p in self.passwords]
            self.total = len(todo)
            chunk_size = max(1, self.total // self.hilos)
            self.chunks = [todo[i:i+chunk_size] for i in range(0, self.total, chunk_size)]
        else:
            todo = [(None, p) for p in self.passwords]
            self.total = len(todo)
            chunk_size = max(1, self.total // self.hilos)
            self.chunks = [todo[i:i+chunk_size] for i in range(0, self.total, chunk_size)]

    def _worker(self, chunk, idhilo):
        self.intentos_hilo[idhilo] = 0
        self.exitos_hilo[idhilo] = 0
        self.errores_hilo[idhilo] = 0
        # Carga el módulo dinámicamente:
        modulo = __import__(f"src.modules.{self.servicio.lower()}", fromlist=[f"login_{self.servicio.lower()}"])
        login_func = getattr(modulo, SERVICIOS[self.servicio]['func'])
        for usuario, password in chunk:
            if self.control_event.should_stop() or self.captcha_detected.is_set() or self.encontrado.is_set():
                break
            while self.control_event.should_pause():
                time.sleep(0.2)

            if en_blacklist_ip(self.objetivo):
                continue
            if en_blacklist_cred(usuario, password):
                continue

            intentos_reintento = 0
            resultado = False
            proxy_usado = "-"  # Proxy handling se puede reintegrar si lo modularizas.
            otp_str = self.otp_code if self.otp_code else "-"
            puerto_ataque = self.puerto or SERVICIOS[self.servicio]['puerto']

            while intentos_reintento <= MAX_REINTENTOS:
                try:
                    # Web login
                    if self.servicio in ['HTTP_POST', 'HTTP_BASIC']:
                        resultado = login_func(
                            self.url, usuario, password, otp_field=self.otp_field, otp_code=self.otp_code,
                            http_headers=self.http_headers, http_cookies=self.http_cookies,
                            http_post_extra=self.http_post_extra, http_useragent=self.http_useragent,
                            patrones_bloqueo=self.patrones_bloqueo, timeout=TIMEOUT_GLOBAL
                        )
                    # ZIP/RAR
                    elif self.servicio in ['ZIP', 'RAR']:
                        resultado = login_func(self.objetivo, password, timeout=TIMEOUT_GLOBAL)
                    else:
                        resultado = login_func(self.objetivo, usuario, password, puerto_ataque, timeout=TIMEOUT_GLOBAL)

                    log_resultado_general(self.servicio, self.objetivo, usuario, password, resultado, proxy_usado, puerto_ataque, otp_str, error="")
                    # Manejo de bloqueos/captcha
                    if isinstance(resultado, str) and resultado.startswith("BLOQUEO"):
                        self.captcha_detected.set()
                        break
                    break
                except Exception as ex:
                    log_error(self.servicio, self.objetivo, usuario, password, proxy_usado, puerto_ataque, otp_str, error=str(ex))
                    intentos_reintento += 1
                    if intentos_reintento > MAX_REINTENTOS:
                        agregar_blacklist_cred(usuario, password)
                        agregar_blacklist_ip(self.objetivo)
                        with self.lock:
                            self.errores_hilo[idhilo] += 1
                            self.errores += 1
                        break
                    time.sleep(1)

            with self.lock:
                self.contador += 1
                self.intentos_hilo[idhilo] += 1

            if resultado == "CAPTCHA":
                self.captcha_detected.set()
                break
            if isinstance(resultado, str) and resultado.startswith("BLOQUEO:"):
                self.captcha_detected.set()
                break
            if resultado is True:
                self.resultado.append((usuario, password))
                self.exitos_hilo[idhilo] += 1
                with self.lock:
                    self.exitos += 1
                self.encontrado.set()
                log_exito(self.servicio, self.objetivo, usuario, password, proxy_usado, puerto_ataque, otp_str)

            if self.actualizar_stats:
                eta = self.eta_estimado()
                self.actualizar_stats(self.contador, self.total, self.exitos, self.errores, self.intentos_hilo, self.exitos_hilo, self.errores_hilo, eta)

    def eta_estimado(self):
        if self.contador == 0:
            return "-"
        duracion = time.time() - self.t0
        restante = self.total - self.contador
        eta = (duracion / self.contador) * restante
        return time.strftime('%H:%M:%S', time.gmtime(eta))

    def iniciar(self, actualizar_barra=None, actualizar_stats=None):
        threads = []
        for i, chunk in enumerate(self.chunks):
            hilo = threading.Thread(target=self._worker, args=(chunk, i))
            hilo.start()
            threads.append(hilo)
        while any(t.is_alive() for t in threads):
            if actualizar_barra:
                actualizar_barra(self.contador, self.total, self.exitos)
            if self.actualizar_stats:
                self.actualizar_stats(self.contador, self.total, self.exitos, self.errores, self.intentos_hilo, self.exitos_hilo, self.errores_hilo, self.eta_estimado())
            time.sleep(0.2)
        for t in threads:
            t.join()
        if actualizar_barra:
            actualizar_barra(self.total, self.total, self.exitos)
        if self.actualizar_stats:
            self.actualizar_stats(self.total, self.total, self.exitos, self.errores, self.intentos_hilo, self.exitos_hilo, self.errores_hilo, self.eta_estimado())
        return self.resultado

# Clase de control de hilos
class StoppableEvent:
    def __init__(self):
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()

    def set_stop(self):
        self._stop_event.set()

    def clear_stop(self):
        self._stop_event.clear()

    def should_stop(self):
        return self._stop_event.is_set()

    def set_pause(self):
        self._pause_event.set()

    def clear_pause(self):
        self._pause_event.clear()

    def should_pause(self):
        return self._pause_event.is_set()
