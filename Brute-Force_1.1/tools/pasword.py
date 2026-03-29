import string
from tqdm import tqdm

def login(usuario, contrasena):
    # Simula un login real, cámbialo por tu validación/lógica web.
    return usuario == "SuperUser!" and contrasena == "Qwerty#2024"

# --- Carga los diccionarios ---
with open("usuarios.txt", "r", encoding="utf-8", errors="ignore") as f_user:
    usuarios = [u.strip() for u in f_user if 6 <= len(u.strip()) <= 10]

with open("passwords.txt", "r", encoding="utf-8", errors="ignore") as f_pass:
    passwords = [p.strip() for p in f_pass if 6 <= len(p.strip()) <= 10]

caracteres_permitidos = string.ascii_letters + string.digits + string.punctuation

def es_valido(texto):
    return all(c in caracteres_permitidos for c in texto)

usuarios = [u for u in usuarios if es_valido(u)]
passwords = [p for p in passwords if es_valido(p)]

encontrado = False
intentos = 0

print(f"[i] Usuarios a probar: {len(usuarios)}")
print(f"[i] Contraseñas a probar: {len(passwords)}")
print(f"[i] Total de combinaciones: {len(usuarios) * len(passwords)}")

for usuario in tqdm(usuarios, desc="Usuarios"):
    for contrasena in tqdm(passwords, desc="Passwords", leave=False):
        intentos += 1
        if login(usuario, contrasena):
            print(f"\n[+] ENCONTRADO: Usuario: '{usuario}' | Contraseña: '{contrasena}'")
            print(f"Intentos realizados: {intentos}")
            encontrado = True
            break
    if encontrado:
        break

if not encontrado:
    print("[-] No se encontró combinación usuario/contraseña en los diccionarios.")
