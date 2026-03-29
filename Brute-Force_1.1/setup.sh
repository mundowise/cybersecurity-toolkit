#!/bin/bash

echo "Instalando dependencias de sistema..."
sudo apt update
sudo apt install -y python3 python3-pip python3-tk python3-dev python3-pyqt5 libpq-dev libmysqlclient-dev \
    aircrack-ng hashcat nmap unrar

echo "Instalando dependencias de Python..."
pip3 install -r requirements.txt

echo "Configurando permisos para herramientas de cracking..."
sudo chmod +s /usr/sbin/aircrack-ng 2>/dev/null
sudo chmod +s /usr/sbin/hashcat 2>/dev/null

echo "Instalación completada. Puedes ejecutar la suite con:"
echo "python3 main.py"
