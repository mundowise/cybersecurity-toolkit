import os
import datetime

def get_screengrab_path():
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.expanduser(f"~/screengrab_{now}.png")

def snap_screen():
    try:
        if os.name == "nt":
            import pyscreenshot as ImageGrab
        else:
            from PIL import ImageGrab
        path = get_screengrab_path()
        img = ImageGrab.grab()
        img.save(path)
        return path
    except Exception as e:
        return f"[!] Error: {e}"

def run(cmd, *args):
    if cmd == "snap":
        return snap_screen()
    elif cmd == "fetch":
        from glob import glob
        files = sorted(glob(os.path.expanduser("~/screengrab_*.png")), reverse=True)
        return files[0] if files else "[!] No hay capturas previas."
    else:
        return "[!] Comando no soportado en screengrab."
