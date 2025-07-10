# 🚀 Despliegue en Servidor Único

## Descripción
Diagrama completo del despliegue del sistema de producción en un servidor único, sin contenedores Docker, incluyendo configuración, instalación y mantenimiento.

## Arquitectura de Despliegue

### 🖥️ Especificaciones del Servidor
- **OS**: Ubuntu 20.04 LTS o superior
- **CPU**: 4 cores (mínimo 2 cores)
- **RAM**: 8GB (mínimo 4GB)
- **Storage**: 100GB SSD
- **Network**: Gigabit Ethernet
- **IP Estática**: 192.168.1.200

## Diagrama de Despliegue

```mermaid
graph TB
    subgraph "🖥️ Servidor Físico (192.168.1.200)"
        
        subgraph "💿 Sistema Operativo"
            OS["`**Ubuntu 20.04 LTS**<br/>• Kernel 5.4+<br/>• systemd init<br/>• Firewall UFW<br/>• SSH habilitado`"]
        end
        
        subgraph "🐍 Python Runtime"
            Python["`**Python 3.11**<br/>• FastAPI Framework<br/>• PyModbus Library<br/>• SQLAlchemy ORM<br/>• Pydantic Models`"]
            
            PythonVenv["`**Virtual Environment**<br/>• /opt/production/venv<br/>• Isolated dependencies<br/>• pip package manager`"]
            
            Requirements["`**requirements.txt**<br/>• fastapi==0.104.1<br/>• uvicorn==0.24.0<br/>• pymodbus==3.5.2<br/>• sqlalchemy==2.0.23`"]
        end
        
        subgraph "🟢 Node.js Runtime"
            NodeJS["`**Node.js 18 LTS**<br/>• SvelteKit Framework<br/>• Vite Build Tool<br/>• TypeScript Support`"]
            
            NPM["`**Package Manager**<br/>• pnpm (preferred)<br/>• Global packages<br/>• Build dependencies`"]
            
            FrontendBuild["`**Production Build**<br/>• /opt/production/frontend<br/>• Static assets<br/>• SSR enabled`"]
        end
        
        subgraph "🗄️ PostgreSQL Database"
            PostgreSQL["`**PostgreSQL 15**<br/>• production_system DB<br/>• Port 5432<br/>• Local connections only`"]
            
            DBData["`**Data Directory**<br/>• /var/lib/postgresql/15<br/>• WAL archiving<br/>• Auto-vacuum enabled`"]
            
            DBBackup["`**Backup System**<br/>• Daily pg_dump<br/>• /var/backups/postgres<br/>• 30-day retention`"]
        end
        
        subgraph "🔧 System Services"
            SystemdBackend["`**backend.service**<br/>• Auto-start<br/>• Restart on failure<br/>• Logging enabled`"]
            
            SystemdFrontend["`**frontend.service**<br/>• Auto-start<br/>• Port 3000<br/>• PM2 process manager`"]
            
            SystemdPostgres["`**postgresql.service**<br/>• System managed<br/>• Auto-start<br/>• Health monitoring`"]
            
            CronJobs["`**Cron Jobs**<br/>• DB backup daily<br/>• Log rotation<br/>• Health checks`"]
        end
        
        subgraph "📁 Directory Structure"
            ProjectRoot["`**/opt/production/**<br/>• Main application directory<br/>• Owned by production user<br/>• 755 permissions`"]
            
            BackendDir["`**/opt/production/backend/**<br/>• Python application<br/>• Virtual environment<br/>• Configuration files`"]
            
            FrontendDir["`**/opt/production/frontend/**<br/>• Built SvelteKit app<br/>• Node.js application<br/>• Static assets`"]
            
            LogsDir["`**/var/log/production/**<br/>• Application logs<br/>• Access logs<br/>• Error logs`"]
            
            ConfigDir["`**/etc/production/**<br/>• Configuration files<br/>• Environment variables<br/>• SSL certificates`"]
        end
        
        subgraph "🔒 Security & Networking"
            Firewall["`**UFW Firewall**<br/>• Port 22 (SSH)<br/>• Port 502 (Modbus)<br/>• Port 3000 (Frontend)`"]
            
            SSL["`**SSL/TLS**<br/>• Self-signed cert<br/>• Or Let's Encrypt<br/>• HTTPS redirect`"]
            
            UserAccounts["`**System Users**<br/>• production (app user)<br/>• postgres (db user)<br/>• Limited privileges`"]
        end
        
        subgraph "📊 Monitoring & Logs"
            SystemLogs["`**System Logs**<br/>• journalctl<br/>• syslog<br/>• Application logs`"]
            
            Monitoring["`**Health Monitoring**<br/>• Process status<br/>• Resource usage<br/>• Disk space`"]
            
            LogRotation["`**Log Rotation**<br/>• logrotate config<br/>• Size-based rotation<br/>• Compression enabled`"]
        end
    end
    
    subgraph "🌐 External Connections"
        PLCExternal["`🏭 **PLC Externo**<br/>IP: 192.168.1.100<br/>Modbus TCP Port 502`"]
        
        UserDevices["`👥 **Dispositivos Usuario**<br/>• PC Escritorio<br/>• Tablets<br/>• Smartphones`"]
        
        NetworkSwitch["`🔗 **Switch Red**<br/>Ethernet Gigabit<br/>VLAN configurada`"]
    end
    
    %% Conexiones
    PLCExternal -.->|"Modbus TCP"| Firewall
    NetworkSwitch --> UserDevices
    NetworkSwitch --> Firewall
    
    OS --> Python
    OS --> NodeJS
    OS --> PostgreSQL
    
    Python --> PythonVenv
    PythonVenv --> Requirements
    
    NodeJS --> NPM
    NPM --> FrontendBuild
    
    PostgreSQL --> DBData
    PostgreSQL --> DBBackup
    
    OS --> SystemdBackend
    OS --> SystemdFrontend
    OS --> SystemdPostgres
    OS --> CronJobs
    
    ProjectRoot --> BackendDir
    ProjectRoot --> FrontendDir
    ProjectRoot --> LogsDir
    ProjectRoot --> ConfigDir
    
    OS --> Firewall
    OS --> SSL
    OS --> UserAccounts
    
    OS --> SystemLogs
    OS --> Monitoring
    OS --> LogRotation
    
    classDef system fill:#BBDEFB,stroke:#0D47A1,color:#000
    classDef runtime fill:#C8E6C9,stroke:#1B5E20,color:#000
    classDef database fill:#FFE0B2,stroke:#E65100,color:#000
    classDef service fill:#E1BEE7,stroke:#4A148C,color:#000
    classDef directory fill:#FFCDD2,stroke:#B71C1C,color:#000
    classDef security fill:#B2DFDB,stroke:#004D40,color:#000
    classDef external fill:#F8BBD9,stroke:#880E4F,color:#000
    
    class OS,SystemLogs,Monitoring,LogRotation system
    class Python,PythonVenv,Requirements,NodeJS,NPM,FrontendBuild runtime
    class PostgreSQL,DBData,DBBackup database
    class SystemdBackend,SystemdFrontend,SystemdPostgres,CronJobs service
    class ProjectRoot,BackendDir,FrontendDir,LogsDir,ConfigDir directory
    class Firewall,SSL,UserAccounts security
    class PLCExternal,UserDevices,NetworkSwitch external
```

## Proceso de Instalación

### 📋 Pre-requisitos del Sistema

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias básicas
sudo apt install -y curl wget git build-essential \
    software-properties-common apt-transport-https \
    ca-certificates gnupg lsb-release
```

### 🐍 Instalación Python 3.11

```bash
# Agregar repositorio deadsnakes
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Instalar Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Configurar alternativas
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
```

### 🟢 Instalación Node.js 18 LTS

```bash
# Instalar Node.js via NodeSource
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Instalar pnpm globalmente
sudo npm install -g pnpm pm2

# Verificar instalación
node --version  # v18.x.x
npm --version   # 9.x.x
pnpm --version  # 8.x.x
```

### 🗄️ Instalación PostgreSQL 15

```bash
# Instalar PostgreSQL
sudo apt install -y postgresql-15 postgresql-contrib-15

# Configurar PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Crear base de datos y usuario
sudo -u postgres psql << EOF
CREATE DATABASE production_system;
CREATE USER production_user WITH PASSWORD 'secure_password_123';
GRANT ALL PRIVILEGES ON DATABASE production_system TO production_user;
ALTER USER production_user CREATEDB;
EOF
```

### 👤 Configuración Usuario del Sistema

```bash
# Crear usuario para la aplicación
sudo adduser --system --group --home /opt/production production

# Crear estructura de directorios
sudo mkdir -p /opt/production/{backend,frontend,logs,config}
sudo mkdir -p /var/log/production
sudo mkdir -p /etc/production

# Asignar permisos
sudo chown -R production:production /opt/production
sudo chown -R production:production /var/log/production
sudo chmod 755 /opt/production
```

### 📦 Despliegue del Backend

```bash
# Cambiar a usuario production
sudo -u production -i

# Clonar repositorio (o copiar archivos)
cd /opt/production
git clone <repository_url> backend
cd backend

# Crear virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Configurar variables de entorno
cat > /etc/production/backend.env << EOF
DATABASE_URL=postgresql://production_user:secure_password_123@localhost/production_system
MODBUS_HOST=0.0.0.0
MODBUS_PORT=502
API_HOST=0.0.0.0
API_PORT=8000
JWT_SECRET_KEY=$(openssl rand -hex 32)
LOG_LEVEL=INFO
ENVIRONMENT=production
EOF

# Crear servicio systemd
sudo tee /etc/systemd/system/backend.service << EOF
[Unit]
Description=Production System Backend
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=production
Group=production
WorkingDirectory=/opt/production/backend
Environment=PATH=/opt/production/backend/venv/bin
EnvironmentFile=/etc/production/backend.env
ExecStart=/opt/production/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

### 🌐 Despliegue del Frontend

```bash
# Compilar frontend
cd /opt/production/frontend
pnpm install
pnpm build

# Configurar variables de entorno
cat > /etc/production/frontend.env << EOF
PUBLIC_API_URL=http://192.168.1.200:8000
PUBLIC_WS_URL=ws://192.168.1.200:8000
PORT=3000
NODE_ENV=production
EOF

# Crear servicio systemd
sudo tee /etc/systemd/system/frontend.service << EOF
[Unit]
Description=Production System Frontend
After=network.target backend.service

[Service]
Type=simple
User=production
Group=production
WorkingDirectory=/opt/production/frontend
EnvironmentFile=/etc/production/frontend.env
ExecStart=/usr/bin/node build/index.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

### 🔧 Configuración de Servicios

```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar y iniciar servicios
sudo systemctl enable postgresql backend frontend
sudo systemctl start backend frontend

# Verificar estado
sudo systemctl status backend frontend
```

### 🛡️ Configuración Firewall

```bash
# Configurar UFW
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Permitir SSH
sudo ufw allow 22/tcp

# Permitir Modbus TCP desde PLC
sudo ufw allow from 192.168.1.100 to any port 502

# Permitir acceso web desde red local
sudo ufw allow from 192.168.1.0/24 to any port 3000
sudo ufw allow from 192.168.1.0/24 to any port 8000

# Activar firewall
sudo ufw --force enable
sudo ufw status verbose
```

## Configuración de Backup Automático

### 📅 Script de Backup Diario

```bash
# Crear script de backup
sudo tee /opt/production/scripts/backup.sh << 'EOF'
#!/bin/bash

# Variables
BACKUP_DIR="/var/backups/production"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Crear directorio si no existe
mkdir -p "$BACKUP_DIR"

# Backup base de datos
pg_dump -h localhost -U production_user production_system | \
    gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz"

# Backup archivos de configuración
tar -czf "$BACKUP_DIR/config_backup_$DATE.tar.gz" \
    /etc/production/ \
    /opt/production/backend/app/ \
    /opt/production/frontend/src/

# Limpiar backups antiguos
find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete

# Log del backup
echo "$(date): Backup completed - $DATE" >> /var/log/production/backup.log
EOF

# Hacer ejecutable
sudo chmod +x /opt/production/scripts/backup.sh

# Agregar a crontab
sudo tee /etc/cron.d/production-backup << EOF
# Backup diario a las 2:00 AM
0 2 * * * production /opt/production/scripts/backup.sh
EOF
```

### 📊 Monitoreo de Salud del Sistema

```bash
# Script de health check
sudo tee /opt/production/scripts/health_check.sh << 'EOF'
#!/bin/bash

# Variables
LOG_FILE="/var/log/production/health.log"
DATE=$(date)

# Función de logging
log() {
    echo "[$DATE] $1" >> "$LOG_FILE"
}

# Verificar servicios
check_service() {
    if systemctl is-active --quiet "$1"; then
        log "✅ Service $1 is running"
        return 0
    else
        log "❌ Service $1 is not running"
        return 1
    fi
}

# Verificar conectividad de base de datos
check_database() {
    if sudo -u production psql -h localhost -U production_user -d production_system -c "SELECT 1;" > /dev/null 2>&1; then
        log "✅ Database connection OK"
        return 0
    else
        log "❌ Database connection failed"
        return 1
    fi
}

# Verificar espacio en disco
check_disk() {
    USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$USAGE" -lt 80 ]; then
        log "✅ Disk usage: ${USAGE}%"
        return 0
    else
        log "⚠️ Disk usage high: ${USAGE}%"
        return 1
    fi
}

# Ejecutar verificaciones
log "=== Health Check Started ==="
check_service "backend"
check_service "frontend" 
check_service "postgresql"
check_database
check_disk
log "=== Health Check Completed ==="
EOF

# Hacer ejecutable
sudo chmod +x /opt/production/scripts/health_check.sh

# Ejecutar cada 15 minutos
sudo tee /etc/cron.d/production-health << EOF
# Health check cada 15 minutos
*/15 * * * * production /opt/production/scripts/health_check.sh
EOF
```

## Configuración de Logs

### 📝 Rotación de Logs

```bash
# Configurar logrotate
sudo tee /etc/logrotate.d/production << EOF
/var/log/production/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    create 0644 production production
}
EOF

# Configurar logs de aplicación
sudo tee /etc/rsyslog.d/production.conf << EOF
# Production system logs
local0.*    /var/log/production/application.log
local1.*    /var/log/production/modbus.log
local2.*    /var/log/production/api.log
EOF

sudo systemctl restart rsyslog
```

## Comandos de Gestión

### 🔧 Scripts de Administración

```bash
# Script de gestión principal
sudo tee /opt/production/scripts/manage.sh << 'EOF'
#!/bin/bash

case "$1" in
    start)
        echo "Starting production system..."
        sudo systemctl start backend frontend
        ;;
    stop)
        echo "Stopping production system..."
        sudo systemctl stop backend frontend
        ;;
    restart)
        echo "Restarting production system..."
        sudo systemctl restart backend frontend
        ;;
    status)
        echo "=== System Status ==="
        sudo systemctl status backend --no-pager -l
        sudo systemctl status frontend --no-pager -l
        sudo systemctl status postgresql --no-pager -l
        ;;
    logs)
        echo "=== Recent Logs ==="
        sudo journalctl -u backend -u frontend -n 50 --no-pager
        ;;
    backup)
        echo "Running manual backup..."
        /opt/production/scripts/backup.sh
        ;;
    health)
        echo "Running health check..."
        /opt/production/scripts/health_check.sh
        tail -20 /var/log/production/health.log
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|backup|health}"
        exit 1
        ;;
esac
EOF

# Hacer ejecutable
sudo chmod +x /opt/production/scripts/manage.sh

# Crear enlace simbólico para acceso fácil
sudo ln -s /opt/production/scripts/manage.sh /usr/local/bin/production
```

## Actualización del Sistema

### 🔄 Proceso de Update

```bash
# Script de actualización
sudo tee /opt/production/scripts/update.sh << 'EOF'
#!/bin/bash

echo "=== Updating Production System ==="

# Backup antes de actualizar
echo "Creating backup..."
/opt/production/scripts/backup.sh

# Parar servicios
echo "Stopping services..."
sudo systemctl stop backend frontend

# Actualizar backend
echo "Updating backend..."
cd /opt/production/backend
git pull origin main
source venv/bin/activate
pip install -r requirements.txt

# Actualizar frontend
echo "Updating frontend..."
cd /opt/production/frontend
pnpm install
pnpm build

# Migrar base de datos si es necesario
echo "Running database migrations..."
cd /opt/production/backend
source venv/bin/activate
alembic upgrade head

# Reiniciar servicios
echo "Restarting services..."
sudo systemctl start backend frontend

# Verificar estado
echo "Checking status..."
sleep 5
sudo systemctl status backend frontend

echo "=== Update completed ==="
EOF

sudo chmod +x /opt/production/scripts/update.sh
```

### 📊 Métricas de Rendimiento

```bash
# Crear script de métricas
sudo tee /opt/production/scripts/metrics.sh << 'EOF'
#!/bin/bash

echo "=== System Metrics ==="
echo "Date: $(date)"
echo ""

echo "CPU Usage:"
top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//'

echo ""
echo "Memory Usage:"
free -h

echo ""
echo "Disk Usage:"
df -h /

echo ""
echo "Network Connections:"
ss -tuln | grep -E ":502|:3000|:8000|:5432"

echo ""
echo "Process Status:"
ps aux | grep -E "(python|node|postgres)" | grep -v grep

echo ""
echo "Service Status:"
systemctl is-active backend frontend postgresql
EOF

sudo chmod +x /opt/production/scripts/metrics.sh
``` 