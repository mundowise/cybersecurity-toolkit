# src/core/logger.py

import csv
from datetime import datetime
import os

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/resultados'))

def log_resultado_general(servicio, objetivo, usuario, password, resultado, proxy, puerto, otp, error=""):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = [now, servicio, objetivo, usuario or "-", password or "-", str(resultado), proxy or "-", str(puerto or "-"), otp or "-", error]
    with open(os.path.join(DATA_DIR, "resultados_todos.csv"), "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(linea)
    with open(os.path.join(DATA_DIR, "resultados_todos.txt"), "a", encoding='utf-8') as f:
        f.write(",".join(linea) + "\n")

def log_exito(servicio, objetivo, usuario, password, proxy, puerto, otp):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = [now, servicio, objetivo, usuario or "-", password or "-", proxy or "-", str(puerto or "-"), otp or "-"]
    with open(os.path.join(DATA_DIR, "resultados_exitos.csv"), "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(linea)
    with open(os.path.join(DATA_DIR, "resultados_exitos.txt"), "a", encoding='utf-8') as f:
        f.write(",".join(linea) + "\n")

def log_error(servicio, objetivo, usuario, password, proxy, puerto, otp, error):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = [now, servicio, objetivo, usuario or "-", password or "-", proxy or "-", str(puerto or "-"), otp or "-", error]
    with open(os.path.join(DATA_DIR, "resultados_errores.csv"), "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(linea)
    with open(os.path.join(DATA_DIR, "resultados_errores.txt"), "a", encoding='utf-8') as f:
        f.write(",".join(linea) + "\n")
