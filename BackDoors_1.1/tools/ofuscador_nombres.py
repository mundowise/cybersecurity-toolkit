import os
import re
import random
import string
import shutil

# Carpetas que deseas ofuscar (ajusta según tu proyecto)
CARPETA = "src"

# Palabras reservadas y nombres a evitar
RESERVADAS = set([
    "self", "cls", "__init__", "__main__", "__name__", "__file__", "__dict__",
    "__class__", "__module__", "__bases__", "__doc__"
])

# Evita cambiar palabras clave de Python o librerías externas
PYTHON_KEYWORDS = set([
    "False", "class", "finally", "is", "return", "None", "continue", "for", "lambda", "try", "True", "def", "from",
    "nonlocal", "while", "and", "del", "global", "not", "with", "as", "elif", "if", "or", "yield", "assert", "else",
    "import", "pass", "break", "except", "in", "raise"
])

def random_name(n=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

def encontrar_nombres(archivo):
    with open(archivo, "r", encoding="utf-8") as f:
        codigo = f.read()
    # Busca funciones, clases y variables (muy básico, pero seguro)
    funciones = re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\(', codigo)
    clases = re.findall(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\b', codigo)
    variables = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=', codigo)
    encontrados = set(funciones + clases + variables)
    # Excluye reservadas, keywords y nombres de librerías
    encontrados = [x for x in encontrados if x not in RESERVADAS and x not in PYTHON_KEYWORDS and len(x) > 2]
    return encontrados

def crear_diccionario_nombres(nombres):
    reemplazos = {}
    usados = set()
    for nombre in nombres:
        nuevo = random_name()
        while nuevo in usados or nuevo in nombres:
            nuevo = random_name()
        reemplazos[nombre] = nuevo
        usados.add(nuevo)
    return reemplazos

def ofuscar_archivo(archivo, reemplazos):
    with open(archivo, "r", encoding="utf-8") as f:
        codigo = f.read()
    for viejo, nuevo in reemplazos.items():
        # Reemplaza solo palabras completas, no strings
        codigo = re.sub(rf'\b{viejo}\b', nuevo, codigo)
    with open(archivo, "w", encoding="utf-8") as f:
        f.write(codigo)

def backup_carpeta(src, backup):
    if os.path.exists(backup):
        shutil.rmtree(backup)
    shutil.copytree(src, backup)
    print(f"[*] Backup creado en: {backup}")

def main():
    print("==== OFUSCADOR PROFESIONAL DE NOMBRES (SAFE) ====")
    backup_dir = CARPETA + "_backup"
    backup_carpeta(CARPETA, backup_dir)
    todos = set()
    archivos = []
    for root, dirs, files in os.walk(CARPETA):
        for f in files:
            if f.endswith(".py"):
                arch = os.path.join(root, f)
                archivos.append(arch)
                nombres = encontrar_nombres(arch)
                todos.update(nombres)
    print(f"[+] Nombres encontrados: {todos}")
    reemplazos = crear_diccionario_nombres(todos)
    print(f"[+] Diccionario de reemplazos: {reemplazos}")
    for archivo in archivos:
        ofuscar_archivo(archivo, reemplazos)
    print("[+] Ofuscación completa. Prueba tu suit antes de compilar.")

if __name__ == "__main__":
    main()
