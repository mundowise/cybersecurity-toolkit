README - Builder Crypter (EXE y PY)
by WodeN-4ever

¿Qué es este Crypter?
Herramienta profesional para proteger y camuflar tus payloads (RAT, dropper, backdoor…) de antivirus y análisis estático/dinámico.
Permite generar stubs polimórficos, cifrados y ejecutados “fileless” (en memoria),
evadiendo AVs y haciendo cada build único.

Componentes
builder_crypter.py — Cifra cualquier payload .py (script Python)

builder_crypter_exe.py — Cifra cualquier payload binario .exe (ejecutable Windows/PE)

Ambos generan un stub final (script Python) que:

Contiene el payload cifrado en AES-256

Descifra y ejecuta el payload en RAM, sin escribir a disco

Incluye code junk y polimorfismo para evasión

Detecta entornos de análisis (VM, sandbox) y puede autodestruirse

Requisitos
Python 3.8 o superior

pycryptodome

Para EXE: pyinstaller, Windows (para máxima efectividad)

Para ejecución fileless de EXE, solo Windows

Instala dependencias:

pip install pycryptodome
pip install pyinstaller


Uso — Payload Python (.py)
Prepara tu payload

Ejemplo: mi_payload.py (debe poder ejecutarse con exec()).

Genera el stub cifrado:
python builder_crypter.py mi_payload.py stub_final.py

Opcional: Compila a EXE (más evasión):
pyinstaller --onefile --noconsole stub_final.py
El archivo final estará en dist\stub_final.exe.

Uso — Payload Binario (.exe)
Prepara tu binario

Ejemplo: cliente.exe (puede ser cualquier ejecutable, PyInstaller, C, etc).

Genera el stub cifrado:
python builder_crypter_exe.py cliente.exe stub_exe.py

Compila el stub a EXE:
pyinstaller --onefile --noconsole stub_exe.py
El archivo final estará en dist\stub_exe.exe.

¿Qué hace el stub?
Descifra el payload embebido en RAM usando AES-256

Lo ejecuta directamente en memoria (exec() para .py, RunPE para .exe)

No deja rastro en disco ni archivos temporales

Cada build es único: clave y cifrado aleatorio

Dificulta análisis por AV con code junk, anti-VM básico y estructura polimórfica

Notas y recomendaciones
Si tu payload requiere argumentos, modifica el stub para inyectarlos.

Puedes aumentar el nivel de polimorfismo cambiando el code junk en cada build.

Para máxima evasión, recompila el stub antes de cada auditoría.

Verifica siempre el payload final en un entorno controlado (sandbox propia o VM aislada).

NO abuses: Solo para uso profesional y pruebas de pentesting controladas.

Autor: WodeN-4ever
Telegram: t.me/wodenpentest
Github: github.com/WodeN-4ever