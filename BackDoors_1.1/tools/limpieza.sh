#!/bin/bash
echo "=============================================="
echo "LIMPIEZA PROFUNDA DE MALWARE (BackDoors/otros)"
echo "=============================================="

# Matar procesos sospechosos
for nombre in svchost systemd init bash python3 pulseaudio sysdrv explorer; do
    pkill -f "$nombre" 2>/dev/null
done

# Limpiar crontab y autostart
crontab -r 2>/dev/null
AUTOSTART="$HOME/.config/autostart"
if [ -d "$AUTOSTART" ]; then
    rm -f "$AUTOSTART"/SysDrv*.desktop 2>/dev/null
    rm -f "$AUTOSTART"/*.desktop 2>/dev/null
fi

# Borrar archivos persistentes y logs
for ruta in "$HOME/.config" "$HOME/.local/bin" "/usr/local/bin" "/tmp" "$HOME"; do
    find "$ruta" -type f \( -name 'sysdrv*' -o -name 'svchost*' -o -name 'explorer*' -o -name '.sysdrv*' \) -exec chattr -i {} \; -exec rm -f {} \; 2>/dev/null
done

rm -f "$HOME/.keylog_backdoors.txt"
rm -f "$HOME"/screengrab_*.png
rm -f "$HOME/backdoors_activity.log"
rm -rf "$HOME/BackDoors_1.1_Reports"

# Limpiar USBs montados
for base in /media /run/media /mnt; do
    [ -d "$base" ] || continue
    for sub in "$base"/*; do
        [ -d "$sub" ] || continue
        find "$sub" -type f \( -name 'sysdrv*' -o -name 'svchost*' -o -name 'explorer*' -o -name '.sysdrv*' -o -name '*.desktop' \) -exec rm -f {} \; 2>/dev/null
    done
done

echo "=============================================="
echo "LIMPIEZA FINALIZADA"
echo "=============================================="
