import os
import datetime

LOG_FILE = os.path.expanduser("~/backdoors_activity.log")

def log_event(event, message):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8", errors="ignore") as f:
        f.write(f"[{now}] {event}: {message}\n")

def run(cmd, *args):
    if cmd == "show":
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()[-4096:]
        return "[!] No hay logs."
    else:
        return "[!] Comando no soportado en logger."
