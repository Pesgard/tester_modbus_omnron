@echo off
cd /d C:\ruta\a\tu\proyecto
set ORIGIN=http://localhost:3000
echo Iniciando servidor...
start "" /B cmd /c "node build/index.js"
timeout /t 5 > nul
echo Abriendo navegador en modo kiosko...
start chrome --kiosk http://localhost:3000