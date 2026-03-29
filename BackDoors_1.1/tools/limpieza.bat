@echo off
echo ==============================================
echo LIMPIEZA PROFUNDA DE MALWARE (BackDoors/otros)
echo ==============================================

REM Mata posibles procesos maliciosos
for %%N in (svchost.exe lsass.exe explorer.exe winlogon.exe services.exe sysdrv.exe) do (
    taskkill /F /IM %%N >nul 2>&1
)

REM Limpia autoarranque del registro
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v SysDrv /f 2>nul
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v sysdrv /f 2>nul
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v explorer /f 2>nul

REM Borra de carpeta Startup
set "startup=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
if exist "%startup%" (
    del /f /a /q "%startup%\sysdrv.exe" 2>nul
    del /f /a /q "%startup%\svchost.exe" 2>nul
    del /f /a /q "%startup%\explorer.exe" 2>nul
    del /f /a /q "%startup%\*.lnk" 2>nul
    del /f /a /q "%startup%\*.desktop" 2>nul
)

REM Borra archivos persistentes de APPDATA, ProgramData, Temp, Windows
for %%D in ("%APPDATA%" "C:\ProgramData" "C:\Windows\Temp") do (
    del /f /a /q "%%D\sysdrv.exe" 2>nul
    del /f /a /q "%%D\svchost.exe" 2>nul
    del /f /a /q "%%D\explorer.exe" 2>nul
)

REM Borra archivos y logs del usuario
del /f /a /q "%USERPROFILE%\.keylog_backdoors.txt" 2>nul
del /f /a /q "%USERPROFILE%\screengrab_*.png" 2>nul
del /f /a /q "%USERPROFILE%\backdoors_activity.log" 2>nul
rd /s /q "%USERPROFILE%\BackDoors_1.1_Reports" 2>nul

REM Limpia dispositivos USB conectados
for %%D in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist "%%D:\" (
        del /f /a /q "%%D:\sysdrv.exe" 2>nul
        del /f /a /q "%%D:\svchost.exe" 2>nul
        del /f /a /q "%%D:\explorer.exe" 2>nul
        del /f /a /q "%%D:\*.desktop" 2>nul
        del /f /a /q "%%D:\autorun.inf" 2>nul
    )
)

echo ==============================================
echo LIMPIEZA FINALIZADA
echo ==============================================
pause
