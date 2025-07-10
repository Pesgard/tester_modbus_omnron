# 🏭 Production System Backend Documentation

## 📋 Descripción General

El backend del Sistema de Producción es una aplicación basada en **FastAPI** que integra comunicación **Modbus TCP**, base de datos **PostgreSQL**, **WebSockets** en tiempo real y autenticación **JWT**. Está diseñado para monitorear y controlar líneas de producción industrial.

## 🏗️ Arquitectura

El sistema sigue una **arquitectura hexagonal (Clean Architecture)** con separación clara de responsabilidades:

```
app/
├── core/                   # Configuración central
├── domain/                 # Lógica de negocio
│   ├── models.py          # Entidades de dominio
│   └── services/          # Servicios de dominio
├── infrastructure/        # Implementaciones técnicas
│   ├── api/              # Endpoints REST
│   ├── database/         # Persistencia
│   ├── modbus/          # Comunicación Modbus
│   ├── websocket/       # Comunicación WebSocket
│   └── logging/         # Sistema de logs
├── presentation/         # Interfaz web
└── simulator/           # Simulador PLC
```

## 🚀 Tecnologías Principales

- **FastAPI**: Framework web asíncrono
- **SQLAlchemy**: ORM para PostgreSQL
- **PyModbus**: Comunicación Modbus TCP
- **WebSockets**: Comunicación en tiempo real
- **JWT**: Autenticación y autorización
- **Pydantic**: Validación de datos
- **Docker**: Containerización

## ⚙️ Configuración

### Variables de Entorno

Copia `.env.example` a `.env` y configura:

```bash
# Base de datos
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/production_system

# Servidor Modbus
MODBUS_HOST=0.0.0.0
MODBUS_PORT=502

# API
API_HOST=0.0.0.0
API_PORT=8000

# Seguridad
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logs
LOG_LEVEL=INFO
LOG_FILE=production_system.log
```

### Instalación

```bash
# 1. Clonar el repositorio
git clone <repository_url>
cd tester_modbus_omnron

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# 5. Inicializar base de datos
docker-compose up postgres -d

# 6. Ejecutar aplicación
python main.py
```

## 🌐 Endpoints Principales

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/me` - Información del usuario actual

### Producción
- `GET /api/production/current` - Estado actual de producción
- `GET /api/production/history` - Historial de producción
- `GET /api/production/stats` - Estadísticas de producción
- `POST /api/production/batch/new` - Iniciar nuevo lote

### Sistema
- `GET /api/system/health` - Estado del sistema
- `GET /api/system/debug/recent-data` - Datos de depuración

### Administración
- `GET /api/admin/users` - Listar usuarios (admin)
- `POST /api/admin/users` - Crear usuario (admin)

## 🔌 WebSocket

Endpoint: `ws://localhost:8000/ws/production`

Mensajes enviados:
- `connection`: Confirmación de conexión
- `production_data`: Datos de producción en tiempo real
- `pong`: Respuesta a ping del cliente

## 📊 Modelos de Datos

### ProductionData
```python
{
    "timestamp": "2024-01-01T12:00:00",
    "product_id": 12345,
    "quality_status": 1,  # 0=NOK, 1=OK, 2=PENDING
    "production_count": 100,
    "line_status": 1,     # 0=STOPPED, 1=RUNNING, 2=ERROR, 3=MAINTENANCE
    "error_code": 0,
    "cycle_time_ms": 2500,
    "temperature": 25.5,
    "pressure": 4.2,
    "operator_id": 1,
    "batch_id": "BATCH_20240101_001"
}
```

### UserResponse
```python
{
    "id": 1,
    "username": "admin",
    "email": "admin@company.com",
    "full_name": "Administrator",
    "role": "admin",  # admin, operator, supervisor, viewer
    "is_active": true,
    "last_login": "2024-01-01T12:00:00",
    "created_at": "2024-01-01T10:00:00"
}
```

## 🔐 Autenticación

El sistema usa **JWT Bearer tokens** para autenticación:

```bash
# 1. Obtener token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 2. Usar token en requests
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/production/current
```

## 🧪 Testing

```bash
# Ejecutar tests
python -m pytest tests/

# Con coverage
python -m pytest tests/ --cov=app

# Test específico
python -m pytest tests/infrastructure/test_api.py
```

## 📝 Logs

Los logs se guardan en `production_system.log` y también se muestran en consola:

```
2024-01-01 12:00:00 - app.main - INFO - Starting production system services...
2024-01-01 12:00:01 - app.infrastructure.modbus.server - INFO - Starting Modbus server on 0.0.0.0:502
2024-01-01 12:00:02 - app.infrastructure.database - INFO - Database tables created successfully
```

## 🐳 Docker

```bash
# Ejecutar solo base de datos
docker-compose up postgres -d

# Ejecutar con pgAdmin (desarrollo)
docker-compose --profile development up postgres pgadmin -d

# Ejecutar todo el stack
docker-compose up -d
```

## 🔍 Debugging

### Verificar Estado del Sistema
```bash
curl http://localhost:8000/api/system/health
```

### Ver Datos Recientes
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/system/debug/recent-data
```

### Swagger UI
Visita `http://localhost:8000/docs` para la documentación interactiva de la API.

## 📈 Monitoreo

### Métricas Disponibles
- Datos de producción en tiempo real
- Estadísticas de calidad
- Estado de la línea de producción
- Eventos del sistema
- Logs de auditoría

### WebSocket Client
Visita `http://localhost:8000/client` para el cliente web en tiempo real.

## 🛠️ Desarrollo

### Estructura de Carpetas
```
docs/
├── backend/
│   ├── README.md         # Este archivo
│   ├── api.md           # Documentación de API
│   ├── architecture.md  # Arquitectura detallada
│   ├── deployment.md    # Guía de despliegue
│   └── troubleshooting.md # Solución de problemas
```

### Buenas Prácticas
1. **Separación de responsabilidades**: Cada capa tiene su responsabilidad específica
2. **Inyección de dependencias**: Facilita testing y mantenimiento
3. **Logging estructurado**: Logs consistentes y searchables
4. **Validación de datos**: Pydantic para validación robusta
5. **Manejo de errores**: Exception handling consistente

## 📞 Soporte

Para reportar bugs o solicitar features:
1. Crear issue en el repositorio
2. Incluir logs relevantes
3. Describir pasos para reproducir
4. Especificar versión y entorno

---

**Próximos archivos de documentación:**
- [📡 API Reference](./api.md)
- [🏗️ Architecture Guide](./architecture.md)
- [🚀 Deployment Guide](./deployment.md)
- [🔧 Troubleshooting](./troubleshooting.md) 