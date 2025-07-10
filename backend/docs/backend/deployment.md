# 🚀 Deployment Guide

## 🎯 Opciones de Despliegue

### 🏠 Desarrollo Local
- **Docker Compose**: Entorno completo local
- **Native**: Python directo con PostgreSQL local

### 🏢 Staging/Testing
- **Docker Swarm**: Multi-container orchestration
- **Kubernetes**: Para testing de producción

### 🌐 Producción
- **Kubernetes**: Orquestación enterprise
- **Docker Compose**: Para deployments simples
- **Cloud Platforms**: AWS, GCP, Azure

---

## 🐳 Docker Deployment

### 📋 Prerequisitos

```bash
# Instalar Docker y Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Verificar instalación
docker --version
docker-compose --version
```

### ⚙️ Configuración Inicial

```bash
# 1. Clonar repositorio
git clone <repository_url>
cd tester_modbus_omnron

# 2. Configurar variables de entorno
cp .env.example .env

# 3. Editar configuración para Docker
vim .env
```

**Configuración recomendada para Docker (.env):**
```bash
# Database (interno a Docker)
DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/production_system

# Modbus (expuesto al host)
MODBUS_HOST=0.0.0.0
MODBUS_PORT=502

# API (expuesto al host)
API_HOST=0.0.0.0
API_PORT=8000

# Seguridad (CAMBIAR EN PRODUCCIÓN)
SECRET_KEY=production-secret-key-very-secure-2024
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logs
LOG_LEVEL=INFO
LOG_FILE=production_system.log

# Performance
DATABASE_POOL_SIZE=20
DATA_BUFFER_SIZE=2000
WEBSOCKET_MAX_CONNECTIONS=200
```

### 🚀 Despliegue con Docker Compose

#### Desarrollo Completo
```bash
# Solo base de datos
docker-compose up postgres -d

# Base de datos + pgAdmin
docker-compose --profile development up postgres pgadmin -d

# Stack completo (cuando esté el Dockerfile de la app)
docker-compose up -d
```

#### Verificación
```bash
# Verificar contenedores
docker-compose ps

# Ver logs
docker-compose logs -f postgres
docker-compose logs -f production_app

# Estado de salud
curl http://localhost:8000/api/system/health
```

---

## 🏗️ Construcción de Imagen Docker

### 📦 Dockerfile Optimizado

El `Dockerfile` existente ya incluye optimizaciones. Principales características:

```dockerfile
# Multi-stage build para optimizar tamaño
FROM python:3.11-slim as base

# Optimizaciones de seguridad
RUN adduser --disabled-password --gecos '' appuser

# Instalación eficiente de dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Aplicación como usuario no-root
USER appuser
```

### 🔨 Build de Imagen

```bash
# Build local
docker build -t production-system:latest .

# Build con tag específico
docker build -t production-system:v1.0.0 .

# Build con argumentos
docker build \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  --build-arg VERSION=v1.0.0 \
  -t production-system:v1.0.0 .
```

### 📋 Registry Configuration

```bash
# Tag para registry
docker tag production-system:latest registry.company.com/production-system:latest

# Push a registry
docker push registry.company.com/production-system:latest

# Pull en servidor destino
docker pull registry.company.com/production-system:latest
```

---

## ☸️ Kubernetes Deployment

### 📁 Manifests Kubernetes

#### Namespace
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production-system
```

#### ConfigMap
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: production-config
  namespace: production-system
data:
  DATABASE_URL: "postgresql+asyncpg://postgres:password@postgres-service:5432/production_system"
  MODBUS_HOST: "0.0.0.0"
  MODBUS_PORT: "502"
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  LOG_LEVEL: "INFO"
  DATABASE_POOL_SIZE: "20"
```

#### Secret
```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: production-secrets
  namespace: production-system
type: Opaque
data:
  SECRET_KEY: <base64-encoded-secret>
  DATABASE_PASSWORD: <base64-encoded-password>
```

#### PostgreSQL Deployment
```yaml
# k8s/postgres.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: production-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_DB
          value: production_system
        - name: POSTGRES_USER
          value: postgres
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: production-secrets
              key: DATABASE_PASSWORD
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        livenessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - postgres
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - postgres
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: production-system
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

#### Application Deployment
```yaml
# k8s/app.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: production-app
  namespace: production-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: production-app
  template:
    metadata:
      labels:
        app: production-app
    spec:
      containers:
      - name: production-app
        image: registry.company.com/production-system:latest
        ports:
        - containerPort: 8000
        - containerPort: 502
        envFrom:
        - configMapRef:
            name: production-config
        - secretRef:
            name: production-secrets
        livenessProbe:
          httpGet:
            path: /api/system/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/system/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "250m"
---
apiVersion: v1
kind: Service
metadata:
  name: production-service
  namespace: production-system
spec:
  selector:
    app: production-app
  ports:
  - name: http
    port: 8000
    targetPort: 8000
  - name: modbus
    port: 502
    targetPort: 502
  type: LoadBalancer
```

#### Persistent Volume
```yaml
# k8s/pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: production-system
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: standard
```

### 🚀 Deploy en Kubernetes

```bash
# Crear namespace
kubectl apply -f k8s/namespace.yaml

# Crear secrets (encode base64 primero)
echo -n "your-secret-key" | base64
kubectl apply -f k8s/secret.yaml

# Deploy base de datos
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/postgres.yaml

# Deploy aplicación
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/app.yaml

# Verificar deployment
kubectl get pods -n production-system
kubectl get services -n production-system
```

---

## 🔧 Configuración de Producción

### 🛡️ Seguridad

#### Variables de Entorno Seguras
```bash
# Generar secret key segura
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Variables críticas para producción
export SECRET_KEY="generated-secure-key"
export DATABASE_URL="postgresql+asyncpg://user:pass@prod-db:5432/production"
export DEBUG=false
export LOG_LEVEL=WARNING
```

#### SSL/TLS Configuration
```yaml
# nginx.conf para reverse proxy
server {
    listen 443 ssl;
    server_name production.company.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://production-service:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /ws/ {
        proxy_pass http://production-service:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 📊 Performance Tuning

#### Database Optimization
```sql
-- PostgreSQL production settings
ALTER SYSTEM SET shared_buffers = '512MB';
ALTER SYSTEM SET effective_cache_size = '2GB';
ALTER SYSTEM SET maintenance_work_mem = '128MB';
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET work_mem = '4MB';
```

#### Application Settings
```bash
# High-performance configuration
DATABASE_POOL_SIZE=50
DATA_BUFFER_SIZE=5000
WEBSOCKET_MAX_CONNECTIONS=500
LOG_LEVEL=WARNING
DATABASE_ECHO=false
```

---

## 📈 Monitoring & Observability

### 🔍 Health Checks

#### Application Health
```bash
# Health endpoint
curl http://localhost:8000/api/system/health

# Expected response
{
  "status": "healthy",
  "services": {
    "modbus_server": "running",
    "database": "connected",
    "api": "running"
  }
}
```

#### Container Health
```dockerfile
# En Dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/system/health || exit 1
```

### 📊 Monitoring Stack

#### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'production-system'
    static_configs:
      - targets: ['production-service:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s
```

#### Grafana Dashboard
- **Métricas de aplicación**: Request rate, response time, errors
- **Métricas de sistema**: CPU, memory, disk usage
- **Métricas de negocio**: Production count, quality rate, cycle time

### 📝 Logging

#### Structured Logging
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "module": "app.infrastructure.modbus.server",
  "message": "PLC wrote data",
  "extra": {
    "address": 1,
    "product_id": 12345,
    "trace_id": "abc123"
  }
}
```

#### Log Aggregation
```yaml
# filebeat.yml
filebeat.inputs:
- type: container
  paths:
    - '/var/lib/docker/containers/*/*.log'
  processors:
  - add_docker_metadata:
      host: "unix:///var/run/docker.sock"

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

---

## 🔄 CI/CD Pipeline

### 🏗️ GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy Production System

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Run tests
      run: |
        pip install -r requirements.txt
        python -m pytest tests/

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Build Docker image
      run: |
        docker build -t production-system:${{ github.sha }} .
        docker tag production-system:${{ github.sha }} registry.company.com/production-system:latest
    - name: Push to registry
      run: |
        echo ${{ secrets.REGISTRY_PASSWORD }} | docker login registry.company.com -u ${{ secrets.REGISTRY_USERNAME }} --password-stdin
        docker push registry.company.com/production-system:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/production-app production-app=registry.company.com/production-system:${{ github.sha }} -n production-system
        kubectl rollout status deployment/production-app -n production-system
```

---

## 🆘 Troubleshooting

### 🔍 Problemas Comunes

#### Database Connection Issues
```bash
# Verificar conectividad
docker exec -it production_system_postgres_1 psql -U postgres -d production_system

# Ver logs de PostgreSQL
docker logs production_system_postgres_1

# Test connection desde app
docker exec -it production_app python -c "
from app.infrastructure.database.repository import DatabaseManager
import asyncio
async def test():
    db = DatabaseManager()
    print('Database test passed')
asyncio.run(test())
"
```

#### Modbus Connection Issues
```bash
# Verificar puerto Modbus
netstat -tulpn | grep :502

# Test Modbus connection
python -c "
from pymodbus.client import ModbusTcpClient
client = ModbusTcpClient('localhost', port=502)
print('Connected:', client.connect())
client.close()
"
```

#### Performance Issues
```bash
# Verificar recursos
docker stats

# Ver logs de performance
grep "slow" production_system.log

# Database performance
docker exec -it postgres psql -U postgres -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"
```

### 📋 Comandos de Diagnóstico

```bash
# Estado completo del sistema
kubectl describe deployment production-app -n production-system

# Logs de aplicación
kubectl logs -f deployment/production-app -n production-system

# Métricas de pods
kubectl top pods -n production-system

# Debug de networking
kubectl exec -it deployment/production-app -n production-system -- netstat -tulpn

# Backup de base de datos
kubectl exec -it postgres-pod -- pg_dump -U postgres production_system > backup.sql
```

---

## 📚 Best Practices

### 🔒 Security
1. **Secrets Management**: Usar Kubernetes secrets o Vault
2. **Network Policies**: Restringir comunicación entre pods
3. **RBAC**: Configurar roles mínimos necesarios
4. **Image Scanning**: Escanear imágenes por vulnerabilidades

### 📈 Performance
1. **Resource Limits**: Configurar limits y requests apropiados
2. **Horizontal Scaling**: HPA basado en CPU/memoria
3. **Database Tuning**: Optimizar parámetros PostgreSQL
4. **Caching**: Implementar Redis para datos frecuentes

### 🔄 Reliability
1. **Health Checks**: Liveness y readiness probes
2. **Graceful Shutdown**: Manejo de SIGTERM
3. **Circuit Breakers**: Para servicios externos
4. **Backup Strategy**: Backups automáticos de BD

---

## 📞 Support & Maintenance

### 🆘 Escalation Procedures
1. **Level 1**: Restart pods/containers
2. **Level 2**: Check logs and metrics
3. **Level 3**: Database and infrastructure review
4. **Level 4**: Code review and hotfix deployment

### 🔄 Maintenance Windows
- **Weekly**: Minor updates and patches
- **Monthly**: Major version updates
- **Quarterly**: Infrastructure reviews and optimizations 