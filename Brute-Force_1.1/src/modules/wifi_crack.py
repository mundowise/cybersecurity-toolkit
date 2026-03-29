# src/modules/wifi_crack.py

import subprocess

def crack_handshake_aircrack(handshake_file, wordlist_file, bssid=None):
    cmd = ["aircrack-ng", "-w", wordlist_file, handshake_file]
    if bssid:
        cmd += ["-b", bssid]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = proc.stdout + proc.stderr
    if "KEY FOUND!" in output:
        key = output.split("KEY FOUND! [")[1].split("]")[0]
        return key.strip()
    return None

def crack_handshake_hashcat(hccapx_file, wordlist_file, hash_mode="22000", device=None):
    cmd = ["hashcat", "-m", hash_mode, hccapx_file, wordlist_file, "--force", "--potfile-disable"]
    if device:
        cmd += ["-d", str(device)]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = proc.stdout + proc.stderr
    # Procesa resultado y busca línea crackeada en stdout/stderr
    for line in output.splitlines():
        if ":" in line and len(line.split(":")) == 2:
            return line.split(":")[1].strip()
    return None
