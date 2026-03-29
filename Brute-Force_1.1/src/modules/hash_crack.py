import subprocess
import os
from hashid import HashID

def detect_hash_type(hash_str):
    """Autodetecta el tipo de hash usando hashid."""
    h = HashID()
    result = h.identifyHash(hash_str)
    if not result or len(result['matches']) == 0:
        return None
    # El nombre de hashcat está en 'hashcat'
    for m in result['matches']:
        if 'hashcat' in m:
            return m['hashcat']
    return None

def crack_hashcat(hash_file, wordlist_file, hash_type=None, device=None, extra_args=None):
    """
    Crackea hashes usando hashcat. Devuelve un dict {hash: password}
    """
    if not hash_type:
        # Leer primer hash y detectar tipo
        with open(hash_file) as f:
            first_hash = f.readline().strip()
            hash_type = detect_hash_type(first_hash)
        if not hash_type:
            raise Exception("No se pudo detectar el tipo de hash.")
    cmd = [
        "hashcat", "-m", str(hash_type),
        hash_file, wordlist_file,
        "--potfile-disable"
    ]
    if device:
        cmd += ["-d", str(device)]
    if extra_args:
        cmd += extra_args
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # Leer el archivo de salida
    output = proc.stdout + proc.stderr
    found = {}
    # Buscar las líneas crackeadas (hash:password)
    if os.path.isfile(hash_file + ".cracked"):
        with open(hash_file + ".cracked") as f:
            for line in f:
                parts = line.strip().split(':', 1)
                if len(parts) == 2:
                    found[parts[0]] = parts[1]
    else:
        # Analiza la salida por si hashcat imprime resultados directos
        for line in output.splitlines():
            if ":" in line and len(line.split(":")) == 2:
                h, p = line.split(":", 1)
                found[h.strip()] = p.strip()
    return found

def crack_john(hash_file, wordlist_file, extra_args=None):
    """
    Crackea hashes usando John the Ripper.
    """
    cmd = [
        "john", "--wordlist=" + wordlist_file, hash_file
    ]
    if extra_args:
        cmd += extra_args
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # Obtener los resultados con john --show
    show_cmd = ["john", "--show", hash_file]
    proc = subprocess.run(show_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    found = {}
    for line in proc.stdout.splitlines():
        if ":" in line and len(line.split(":")) >= 2:
            h, p = line.split(":", 1)
            found[h.strip()] = p.strip().split(":")[0]
    return found
