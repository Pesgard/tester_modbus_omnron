# 🔧 Comandos de Diagnóstico - PLC App (Windows)

Este documento contiene comandos para diagnosticar y resolver incidencias en la aplicación PLC.

---

## 📋 Índice

1. [Estado de la Aplicación](#1-estado-de-la-aplicación)
2. [Verificación de Puertos](#2-verificación-de-puertos)
3. [Verificación de Directorios FTP](#3-verificación-de-directorios-ftp)
4. [Configuración de Red](#4-configuración-de-red)
5. [Base de Datos (Prisma)](#5-base-de-datos-prisma)
6. [Logs y Monitoreo](#6-logs-y-monitoreo)
7. [Comandos de Reinicio](#7-comandos-de-reinicio)

---

## 1. Estado de la Aplicación

### Verificar si Node.js está corriendo
```powershell
Get-Process -Name "node" -ErrorAction SilentlyContinue | Format-Table Id, ProcessName, CPU, WorkingSet -AutoSize
```

### Ver todos los procesos Node con detalles
```powershell
Get-Process node -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, StartTime, CPU, WorkingSet64
```

### Verificar si la aplicación está escuchando en los puertos correctos
```powershell
netstat -ano | findstr ":900 :4000 :5173"
```

### Matar proceso Node (si es necesario reiniciar)
```powershell
# Primero identificar el PID
netstat -ano | findstr ":900"
# Luego matar el proceso (reemplazar <PID> con el número)
taskkill /PID <PID> /F
```

---

## 2. Verificación de Puertos

### Puerto TCP Server (PLC) - Puerto 900
```powershell
netstat -ano | findstr ":900"
```

### Puerto WebSocket Server - Puerto 4000
```powershell
netstat -ano | findstr ":4000"
```

### Puerto Dev Server (Vite) - Puerto 5173
```powershell
netstat -ano | findstr ":5173"
```

### Ver todos los puertos en escucha
```powershell
netstat -an | findstr "LISTENING"
```

### Test de conectividad al puerto TCP (desde otra terminal)
```powershell
Test-NetConnection -ComputerName localhost -Port 900
```

### Test de conectividad al puerto WebSocket
```powershell
Test-NetConnection -ComputerName localhost -Port 4000
```

---

## 3. Verificación de Directorios FTP

### Verificar existencia del directorio FTP principal
```powershell
Test-Path "$env:USERPROFILE\ftp"
```

### Verificar existencia del directorio de imágenes PLC
```powershell
Test-Path "$env:USERPROFILE\ftp\plc_images"
```

### Crear directorios si no existen
```powershell
# Crear directorio FTP principal
New-Item -ItemType Directory -Path "$env:USERPROFILE\ftp" -Force

# Crear subdirectorio de imágenes PLC
New-Item -ItemType Directory -Path "$env:USERPROFILE\ftp\plc_images" -Force

# Crear subdirectorio de procesados
New-Item -ItemType Directory -Path "$env:USERPROFILE\ftp\procesados" -Force
```

### Ver contenido del directorio FTP
```powershell
Get-ChildItem "$env:USERPROFILE\ftp" -Recurse | Format-Table Name, Length, LastWriteTime -AutoSize
```

### Ver solo imágenes en el directorio
```powershell
Get-ChildItem "$env:USERPROFILE\ftp\plc_images" -Filter "*.jpg" | Format-Table Name, Length, LastWriteTime -AutoSize
```

### Verificar permisos del directorio FTP
```powershell
Get-Acl "$env:USERPROFILE\ftp" | Format-List
```

### Verificar permisos detallados
```powershell
(Get-Acl "$env:USERPROFILE\ftp").Access | Format-Table IdentityReference, FileSystemRights, AccessControlType -AutoSize
```

### Contar archivos pendientes de procesar
```powershell
(Get-ChildItem "$env:USERPROFILE\ftp" -File).Count
```

### Monitorear cambios en tiempo real (similar a tail -f)
```powershell
# Monitorear nuevos archivos en el directorio FTP
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = "$env:USERPROFILE\ftp"
$watcher.EnableRaisingEvents = $true
Register-ObjectEvent $watcher "Created" -Action { Write-Host "Nuevo archivo: $($Event.SourceEventArgs.Name)" }
```

---

## 4. Configuración de Red

### Ver IP local
```powershell
ipconfig | findstr /i "IPv4"
```

### Ver configuración completa de red
```powershell
ipconfig /all
```

### Ver IP de la máquina (formato limpio)
```powershell
(Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" }).IPAddress
```

### Ver tabla de rutas
```powershell
route print
```

### Ver conexiones activas
```powershell
netstat -an | findstr "ESTABLISHED"
```

### Ping a una IP específica (para verificar conectividad con PLC)
```powershell
# Reemplazar <IP_PLC> con la dirección IP del PLC
ping <IP_PLC>
```

### Ver dispositivos en la red local
```powershell
arp -a
```

### Verificar firewall para puerto 900 (TCP Server)
```powershell
netsh advfirewall firewall show rule name=all | findstr "900"
```

### Agregar regla de firewall para TCP Server (si es necesario - ejecutar como Admin)
```powershell
netsh advfirewall firewall add rule name="PLC TCP Server" dir=in action=allow protocol=tcp localport=900
```

### Agregar regla de firewall para WebSocket (si es necesario - ejecutar como Admin)
```powershell
netsh advfirewall firewall add rule name="PLC WebSocket Server" dir=in action=allow protocol=tcp localport=4000
```

---

## 5. Base de Datos (Prisma)

### Abrir Prisma Studio (interfaz gráfica de base de datos)
```powershell
npx prisma studio
```

### Ver estado de las migraciones
```powershell
npx prisma migrate status
```

### Ejecutar migraciones pendientes
```powershell
npx prisma migrate deploy
```

### Generar cliente Prisma
```powershell
npx prisma generate
```

### Resetear base de datos (⚠️ ELIMINA TODOS LOS DATOS)
```powershell
npx prisma migrate reset
```

### Ejecutar seed de datos
```powershell
node prisma/seed.js
```

### Ver esquema de la base de datos
```powershell
npx prisma db pull
```

### Validar esquema Prisma
```powershell
npx prisma validate
```

### Formatear esquema Prisma
```powershell
npx prisma format
```

---

## 6. Logs y Monitoreo

### Iniciar aplicación en modo desarrollo (con logs)
```powershell
pnpm dev
```

### Ver logs del proceso Node (si está corriendo en background)
```powershell
Get-EventLog -LogName Application -Source "Node" -Newest 20
```

### Monitorear uso de recursos del sistema
```powershell
Get-Process node -ErrorAction SilentlyContinue | Select-Object CPU, WorkingSet64, Id | Format-Table -AutoSize
```

### Ver espacio en disco
```powershell
Get-PSDrive -PSProvider FileSystem | Format-Table Name, Used, Free -AutoSize
```

### Verificar variables de entorno relevantes
```powershell
# Ver todas las variables de entorno
Get-ChildItem Env:

# Buscar variables específicas de la aplicación
Get-ChildItem Env: | Where-Object { $_.Name -like "*PLC*" -or $_.Name -like "*FTP*" -or $_.Name -like "*DATABASE*" }
```

---

## 7. Comandos de Reinicio

### Reiniciar la aplicación completa
```powershell
# 1. Detener todos los procesos Node
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force

# 2. Esperar un momento
Start-Sleep -Seconds 2

# 3. Iniciar la aplicación
pnpm dev
```

### Script de diagnóstico completo
```powershell
Write-Host "=== DIAGNÓSTICO PLC APP ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Estado de Node.js:" -ForegroundColor Yellow
Get-Process node -ErrorAction SilentlyContinue | Format-Table Id, ProcessName, CPU -AutoSize
if (-not $?) { Write-Host "   Node.js NO está corriendo" -ForegroundColor Red }

Write-Host ""
Write-Host "2. Puertos en uso:" -ForegroundColor Yellow
netstat -ano | findstr ":900 :4000 :5173"

Write-Host ""
Write-Host "3. Directorios FTP:" -ForegroundColor Yellow
Write-Host "   FTP Principal: $(Test-Path "$env:USERPROFILE\ftp")"
Write-Host "   PLC Images: $(Test-Path "$env:USERPROFILE\ftp\plc_images")"

Write-Host ""
Write-Host "4. IP Local:" -ForegroundColor Yellow
ipconfig | findstr /i "IPv4"

Write-Host ""
Write-Host "=== FIN DIAGNÓSTICO ===" -ForegroundColor Cyan
```

---

## 📁 Rutas Importantes

| Descripción | Ruta |
|-------------|------|
| Directorio FTP (Watcher) | `%USERPROFILE%\ftp` |
| Imágenes PLC | `%USERPROFILE%\ftp\plc_images` |
| Archivos Procesados | `%USERPROFILE%\ftp\procesados` |
| Proyecto | Directorio actual del proyecto |

---

## 🔌 Puertos de la Aplicación

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| TCP Server | 900 | Comunicación con PLC |
| WebSocket Server | 4000 | Actualizaciones en tiempo real |
| Dev Server (Vite) | 5173 | Servidor de desarrollo |
| Prisma Studio | 5555 | Interfaz de base de datos |

---

## ⚠️ Solución de Problemas Comunes

### El watcher de imágenes no detecta archivos
1. Verificar que el directorio existe: `Test-Path "$env:USERPROFILE\ftp"`
2. Verificar permisos: `Get-Acl "$env:USERPROFILE\ftp"`
3. Reiniciar la aplicación

### El PLC no se conecta
1. Verificar que el puerto 900 está abierto: `Test-NetConnection -ComputerName localhost -Port 900`
2. Verificar reglas de firewall
3. Verificar la IP del servidor

### Prisma Studio no abre
1. Verificar conexión a la base de datos
2. Ejecutar: `npx prisma generate`
3. Verificar el archivo `.env` con `DATABASE_URL`

### La aplicación no inicia
1. Verificar dependencias: `pnpm install`
2. Generar cliente Prisma: `npx prisma generate`
3. Verificar que no hay otro proceso usando los puertos

---

## 📝 Notas

- **FTP Watcher**: La aplicación usa Chokidar para monitorear el directorio `%USERPROFILE%\ftp`. No es un servidor SFTP propio, sino un watcher de archivos que detecta cuando un cliente SFTP externo deposita archivos.
- **Variables de entorno**: `PLC_IMAGE_DIR` y `FTP_WATCH_DIR` pueden sobrescribir las rutas por defecto.
- **Ejecutar como Administrador**: Algunos comandos de firewall requieren privilegios elevados.
