# 🔧 Troubleshooting Guide

## 🎯 Guía Rápida de Diagnóstico

### ✅ Checklist Inicial

```bash
# 1. Verificar estado general del sistema
curl http://localhost:8000/api/system/health

# 2. Revisar logs recientes
tail -f production_system.log

# 3. Verificar procesos activos
docker-compose ps
# o en Kubernetes
kubectl get pods -n production-system

# 4. Verificar conectividad de red
netstat -tulpn | grep -E "(8000|502|5432)"
```

---

## 🚨 Problemas Comunes y Soluciones

### 🔌 Problemas de Conectividad

#### ❌ **Error: Connection refused en puerto 8000**

**Síntomas:**
```
curl: (7) Failed to connect to localhost port 8000: Connection refused
```

**Diagnóstico:**
```bash
# Verificar si la aplicación está ejecutándose
ps aux | grep python
docker ps | grep production

# Verificar puerto ocupado
sudo lsof -i :8000
```

**Soluciones:**
```bash
# Solución 1: Reiniciar aplicación
docker-compose restart production_app

# Solución 2: Verificar configuración
grep API_PORT .env

# Solución 3: Cambiar puerto si está ocupado
export API_PORT=8001
```

#### ❌ **Error: Modbus connection timeout**

**Síntomas:**
```
ModbusIOException: [Input/Output] No Response received from the remote unit
```

**Diagnóstico:**
```bash
# Verificar puerto Modbus
netstat -tulpn | grep :502

# Test de conectividad básica
telnet localhost 502

# Verificar logs del servidor Modbus
grep "Modbus" production_system.log
```

**Soluciones:**
```bash
# Solución 1: Verificar configuración
grep MODBUS_ .env

# Solución 2: Reiniciar servidor Modbus
docker-compose restart production_app

# Solución 3: Verificar firewall
sudo ufw status
sudo iptables -L | grep 502
```

### 🗄️ Problemas de Base de Datos

#### ❌ **Error: Could not connect to database**

**Síntomas:**
```
sqlalchemy.exc.OperationalError: (asyncpg.exceptions.ConnectFailureError)
```

**Diagnóstico:**
```bash
# Verificar estado de PostgreSQL
docker logs production_system_postgres_1

# Test de conexión directa
docker exec -it production_system_postgres_1 psql -U postgres -d production_system

# Verificar variables de entorno
grep DATABASE_URL .env
```

**Soluciones:**
```bash
# Solución 1: Reiniciar PostgreSQL
docker-compose restart postgres

# Solución 2: Verificar credenciales
docker-compose exec postgres psql -U postgres -c "\l"

# Solución 3: Recrear base de datos
docker-compose down postgres
docker volume rm production_system_postgres_data
docker-compose up postgres -d
```

#### ❌ **Error: Database tables don't exist**

**Síntomas:**
```
asyncpg.exceptions.UndefinedTableError: relation "production_records" does not exist
```

**Diagnóstico:**
```bash
# Verificar tablas existentes
docker exec -it postgres psql -U postgres -d production_system -c "\dt"

# Verificar logs de creación de tablas
grep "Database tables" production_system.log
```

**Soluciones:**
```bash
# Solución 1: Ejecutar script de inicialización
docker exec -it postgres psql -U postgres -d production_system -f /docker-entrypoint-initdb.d/init-db.sql

# Solución 2: Recrear aplicación (fuerza creación de tablas)
docker-compose restart production_app

# Solución 3: Crear tablas manualmente
python -c "
import asyncio
from app.infrastructure.database.repository import DatabaseManager
async def create_tables():
    db = DatabaseManager()
    await db.create_tables()
asyncio.run(create_tables())
"
```

### 🔐 Problemas de Autenticación

#### ❌ **Error: Token has expired**

**Síntomas:**
```json
{
  "detail": "Token has expired"
}
```

**Diagnóstico:**
```bash
# Verificar configuración de expiración
grep ACCESS_TOKEN_EXPIRE_MINUTES .env

# Decodificar token JWT (sin verificar)
python -c "
import jwt
token = 'your-token-here'
print(jwt.decode(token, options={'verify_signature': False}))
"
```

**Soluciones:**
```bash
# Solución 1: Generar nuevo token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Solución 2: Aumentar tiempo de expiración
echo "ACCESS_TOKEN_EXPIRE_MINUTES=60" >> .env
docker-compose restart production_app
```

#### ❌ **Error: Invalid credentials**

**Síntomas:**
```json
{
  "detail": "Incorrect username or password"
}
```

**Diagnóstico:**
```bash
# Verificar usuarios en base de datos
docker exec -it postgres psql -U postgres -d production_system -c "SELECT username, email, is_active FROM users;"

# Verificar logs de autenticación
grep "authentication" production_system.log
```

**Soluciones:**
```bash
# Solución 1: Verificar credenciales por defecto
# Usuario: admin, Password: admin123

# Solución 2: Crear usuario admin manualmente
docker exec -it postgres psql -U postgres -d production_system -c "
INSERT INTO users (username, email, password_hash, role, is_active) 
VALUES ('admin', 'admin@company.com', 'hashed_password', 'admin', true);
"

# Solución 3: Reset completo de datos
docker-compose down
docker volume prune -f
docker-compose up -d
```

### 📊 Problemas de Performance

#### ❌ **Aplicación lenta o timeouts**

**Síntomas:**
- Respuestas lentas (>5 segundos)
- Timeouts frecuentes
- CPU alto constante

**Diagnóstico:**
```bash
# Verificar uso de recursos
docker stats

# Verificar conexiones de base de datos
docker exec -it postgres psql -U postgres -c "
SELECT COUNT(*) as active_connections 
FROM pg_stat_activity 
WHERE state = 'active';
"

# Verificar queries lentas
docker exec -it postgres psql -U postgres -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"
```

**Soluciones:**
```bash
# Solución 1: Optimizar configuración de BD
echo "DATABASE_POOL_SIZE=20" >> .env
echo "DATABASE_ECHO=false" >> .env

# Solución 2: Limpiar logs antiguos
find . -name "*.log" -size +100M -delete

# Solución 3: Aumentar recursos
# En docker-compose.yml:
#   deploy:
#     resources:
#       limits:
#         memory: 1G
#         cpus: "1.0"
```

#### ❌ **Memoria insuficiente (Out of Memory)**

**Síntomas:**
```
docker: Error response from daemon: OCI runtime create failed: container_linux.go:349: starting container process caused "exec: \"python\": executable file not found in $PATH"
```

**Diagnóstico:**
```bash
# Verificar uso de memoria
free -h
docker system df

# Verificar logs del kernel
dmesg | grep -i "killed process"

# Verificar memoria por contenedor
docker stats --no-stream
```

**Soluciones:**
```bash
# Solución 1: Limpiar sistema Docker
docker system prune -f
docker volume prune -f

# Solución 2: Aumentar swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Solución 3: Reducir buffer de datos
echo "DATA_BUFFER_SIZE=500" >> .env
```

### 🌐 Problemas de WebSocket

#### ❌ **WebSocket connection failed**

**Síntomas:**
- Cliente no puede conectar via WebSocket
- Conexiones se desconectan frecuentemente

**Diagnóstico:**
```bash
# Test de conexión WebSocket
curl --include \
     --no-buffer \
     --header "Connection: Upgrade" \
     --header "Upgrade: websocket" \
     --header "Sec-WebSocket-Key: SGVsbG8sIHdvcmxkIQ==" \
     --header "Sec-WebSocket-Version: 13" \
     http://localhost:8000/ws/production

# Verificar logs de WebSocket
grep -i websocket production_system.log
```

**Soluciones:**
```bash
# Solución 1: Verificar configuración
grep WEBSOCKET_MAX_CONNECTIONS .env

# Solución 2: Reiniciar aplicación
docker-compose restart production_app

# Solución 3: Verificar proxy/firewall
# Si usas nginx, verificar configuración WebSocket
```

---

## 🔍 Técnicas de Debugging

### 📝 Análisis de Logs

#### Logs Estructurados
```bash
# Filtrar por nivel de error
grep "ERROR" production_system.log

# Filtrar por módulo específico
grep "modbus.server" production_system.log

# Filtrar por timestamp
grep "2024-01-01" production_system.log

# Ver logs en tiempo real con filtros
tail -f production_system.log | grep -E "(ERROR|WARNING)"
```

#### Logs con Contexto
```bash
# Ver líneas antes y después del error
grep -B 5 -A 5 "ERROR" production_system.log

# Buscar patrones específicos
grep -E "(timeout|connection|failed)" production_system.log

# Análisis de frecuencia de errores
grep "ERROR" production_system.log | cut -d'-' -f4-5 | sort | uniq -c | sort -nr
```

### 🔬 Debug Interactivo

#### Python Debug Session
```bash
# Acceder al contenedor
docker exec -it production_app bash

# Ejecutar shell interactivo Python
python -c "
from app.core.config import settings
from app.infrastructure.database.repository import DatabaseManager
import asyncio

async def debug_session():
    print('Config:', settings.__dict__)
    db = DatabaseManager()
    # Aquí puedes hacer debugging interactivo
    
asyncio.run(debug_session())
"
```

#### Database Debug
```bash
# Conexión directa a PostgreSQL
docker exec -it postgres psql -U postgres -d production_system

# Queries de debugging
\dt                           # Listar tablas
\d production_records         # Describir tabla
SELECT COUNT(*) FROM production_records;  # Contar registros
SELECT * FROM production_records ORDER BY timestamp DESC LIMIT 5;  # Últimos registros
```

### 📊 Monitoreo en Tiempo Real

#### System Metrics
```bash
# CPU y memoria en tiempo real
watch -n 1 "docker stats --no-stream"

# Conexiones de red
watch -n 1 "netstat -tulpn | grep -E '(8000|502|5432)'"

# Espacio en disco
watch -n 10 "df -h"
```

#### Application Metrics
```bash
# Health check continuo
watch -n 5 "curl -s http://localhost:8000/api/system/health | jq"

# Debug endpoint
watch -n 10 "curl -s -H 'Authorization: Bearer <token>' http://localhost:8000/api/system/debug/recent-data | jq '.system_info'"
```

---

## 🚑 Procedimientos de Emergencia

### 🔄 Restart Completo
```bash
# Docker Compose
docker-compose down
docker-compose up -d

# Kubernetes
kubectl rollout restart deployment/production-app -n production-system
kubectl rollout restart deployment/postgres -n production-system
```

### 💾 Backup de Emergencia
```bash
# Backup de base de datos
docker exec postgres pg_dump -U postgres production_system > emergency_backup_$(date +%Y%m%d_%H%M%S).sql

# Backup de configuración
cp .env .env.backup_$(date +%Y%m%d_%H%M%S)
cp docker-compose.yml docker-compose.yml.backup_$(date +%Y%m%d_%H%M%S)

# Backup de logs
cp production_system.log production_system.log.backup_$(date +%Y%m%d_%H%M%S)
```

### 🔧 Reset Factory
```bash
# CUIDADO: Esto borra todos los datos
docker-compose down -v
docker system prune -f
docker volume prune -f
cp .env.example .env
docker-compose up -d
```

---

## 📋 Scripts de Diagnóstico

### 🔍 Script de Health Check Completo

```bash
#!/bin/bash
# health_check.sh

echo "=== PRODUCTION SYSTEM HEALTH CHECK ==="
echo "Timestamp: $(date)"
echo

# 1. Verificar servicios
echo "1. Services Status:"
docker-compose ps
echo

# 2. Verificar conectividad
echo "2. Network Connectivity:"
echo "API Health: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/system/health)"
echo "Modbus Port: $(nc -z localhost 502 && echo "OPEN" || echo "CLOSED")"
echo "Database Port: $(nc -z localhost 5432 && echo "OPEN" || echo "CLOSED")"
echo

# 3. Verificar recursos
echo "3. Resource Usage:"
echo "Memory: $(free -h | grep Mem | awk '{print $3"/"$2}')"
echo "Disk: $(df -h / | tail -1 | awk '{print $3"/"$2" ("$5")"}')"
echo

# 4. Verificar logs recientes
echo "4. Recent Errors:"
tail -100 production_system.log | grep -E "(ERROR|CRITICAL)" | tail -5
echo

# 5. Verificar base de datos
echo "5. Database Status:"
docker exec postgres psql -U postgres -d production_system -c "SELECT COUNT(*) as total_records FROM production_records;" 2>/dev/null || echo "DB CONNECTION FAILED"
echo

echo "=== END HEALTH CHECK ==="
```

### 🧹 Script de Limpieza

```bash
#!/bin/bash
# cleanup.sh

echo "=== SYSTEM CLEANUP ==="

# Limpiar logs antiguos
find . -name "*.log" -size +50M -exec truncate -s 10M {} \;
echo "✓ Large logs truncated"

# Limpiar Docker
docker system prune -f
echo "✓ Docker system pruned"

# Limpiar archivos temporales
find /tmp -name "*.tmp" -mtime +7 -delete 2>/dev/null
echo "✓ Temporary files cleaned"

# Verificar espacio en disco
df -h /
echo "✓ Disk space checked"

echo "=== CLEANUP COMPLETE ==="
```

---

## 📞 Escalación y Soporte

### 🆘 Niveles de Escalación

#### **Nivel 1 - Operador**
- Verificar health checks
- Reiniciar servicios
- Revisar logs básicos

#### **Nivel 2 - Administrador de Sistema**
- Análisis de performance
- Problemas de red/conectividad
- Configuración de entorno

#### **Nivel 3 - Desarrollador**
- Bugs en aplicación
- Problemas de lógica de negocio
- Cambios de código

#### **Nivel 4 - Arquitecto**
- Problemas de diseño
- Escalabilidad
- Cambios mayores de arquitectura

### 📋 Información para Soporte

Cuando reportes un problema, incluye:

```bash
# Información del sistema
uname -a
docker --version
docker-compose --version

# Estado de servicios
docker-compose ps
curl -s http://localhost:8000/api/system/health

# Logs relevantes (últimas 50 líneas)
tail -50 production_system.log

# Configuración (sin secrets)
grep -v "SECRET\|PASSWORD" .env

# Uso de recursos
docker stats --no-stream
df -h
free -h
```

### 🔗 Recursos Adicionales

- **Logs de aplicación**: `production_system.log`
- **Swagger UI**: `http://localhost:8000/docs`
- **pgAdmin**: `http://localhost:8080` (en modo desarrollo)
- **WebSocket Client**: `http://localhost:8000/client`

---

## 🎯 Prevención de Problemas

### ✅ Mejores Prácticas

1. **Monitoreo proactivo**: Configurar alertas en métricas clave
2. **Backups regulares**: Automatizar backups diarios
3. **Updates graduales**: Probar en staging antes de producción
4. **Documentación**: Mantener logs de cambios
5. **Testing**: Pruebas automáticas en CI/CD

### 📊 Métricas a Monitorear

- **API Response Time**: < 1 segundo para endpoints normales
- **Database Connections**: < 80% del pool
- **Memory Usage**: < 80% de la disponible
- **Disk Space**: > 20% libre
- **Error Rate**: < 1% de requests 