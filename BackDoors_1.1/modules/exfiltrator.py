# modules/exfiltrator.py

import os
import shutil

def upload_file(src, dest):
    try:
        shutil.copy2(src, dest)
        return f"Archivo {src} subido a {dest}"
    except Exception as e:
        return f"Error al subir archivo: {e}"

def download_file(src, dest):
    try:
        shutil.copy2(src, dest)
        return f"Archivo {src} descargado a {dest}"
    except Exception as e:
        return f"Error al descargar archivo: {e}"

def run(comando, *args):
    if comando == "upload":
        return upload_file(*args)
    elif comando == "download":
        return download_file(*args)
    else:
        return "Comando desconocido"

