@echo off
cd /d C:\ruta\a\tu\proyecto
start "" /B cmd /c "npm run start"
timeout /t 5 > nul
start chrome --kiosk http://localhost:3000
