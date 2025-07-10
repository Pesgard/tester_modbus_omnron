# 🏭 Sistema de Producción Industrial - Backend API

Un sistema completo de monitoreo de producción industrial que se comunica con PLCs via Modbus TCP y proporciona datos en tiempo real a través de API REST y WebSockets.

## 📋 Tabla de Contenidos

- [🔧 Tecnologías](#-tecnologías)
- [🏗️ Arquitectura](#️-arquitectura)
- [🚀 Instalación y Ejecución](#-instalación-y-ejecución)
- [🔐 Autenticación](#-autenticación)
- [📡 API REST Endpoints](#-api-rest-endpoints)
- [📊 WebSocket en Tiempo Real](#-websocket-en-tiempo-real)
- [📈 Modelos de Datos](#-modelos-de-datos)
- [💻 Ejemplos para Frontend](#-ejemplos-para-frontend)
- [🐳 Docker](#-docker)
- [📚 Documentación](#-documentación)

## 🔧 Tecnologías

- **FastAPI** - Framework web moderno y rápido
- **Modbus TCP** - Comunicación con equipos industriales (PLCs)
- **WebSockets** - Datos en tiempo real
- **SQLAlchemy + AsyncPG** - Base de datos asíncrona
- **JWT** - Autenticación segura
- **Pydantic** - Validación automática de datos

## 🏗️ Arquitectura

### Comunicación con PLC (Modbus)
- **Servidor Modbus TCP** en puerto `502`
- Recibe datos de producción cada 2-3 segundos
- **Direcciones principales**:
  - `Dirección 1`: Datos principales de producción
  - `Dirección 21`: Datos de calidad 
  - `Dirección 41`: Datos de proceso (temperatura, presión)

### Flujo de Datos
```
PLC → Modbus TCP → Backend → WebSocket → Frontend
                      ↓
                  Base de Datos
```

## 🚀 Instalación y Ejecución

### Requisitos Previos
- Python 3.8+
- PostgreSQL (opcional, usa SQLite por defecto)

### Instalación

```bash
# Clonar repositorio
git clone <repository-url>
cd tester_modbus_omnron

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### Ejecución

```bash
# Desarrollo
python -m app.main

# o con uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Variables de Entorno

Crear archivo `.env`:

```bash
# Base de datos
DATABASE_URL=postgresql+asyncpg://postgres:admin@localhost:5432/production_system

# Servidor
API_HOST=0.0.0.0
API_PORT=8000

# Modbus
MODBUS_HOST=0.0.0.0
MODBUS_PORT=502

# Seguridad
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (para desarrollo)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

## 🔐 Autenticación

### Roles de Usuario
- **Admin**: Acceso completo + gestión de usuarios
- **Supervisor**: Supervisión de producción + reportes  
- **Operator**: Monitoreo y control de producción
- **Viewer**: Solo lectura de datos

### Credenciales por Defecto
- **Usuario**: `admin`
- **Contraseña**: `admin123`

### Flujo de Autenticación
1. **Login**: `POST /api/auth/login`
2. **Recibir JWT token**
3. **Incluir en headers**: `Authorization: Bearer <token>`

## 📡 API REST Endpoints

### Base URL: `http://localhost:8000`

### 🔐 Autenticación

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/auth/login` | Iniciar sesión | No |
| `GET` | `/api/auth/me` | Perfil del usuario actual | Sí |

### 📊 Producción

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/production/current` | Datos actuales de producción | Sí |
| `GET` | `/api/production/history` | Historial con filtros | Sí |
| `GET` | `/api/production/stats` | Estadísticas de producción | Sí |
| `POST` | `/api/production/batch/new` | Crear nuevo lote | Sí |

### 👥 Administración (Solo Admin)

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/admin/users` | Listar usuarios | Admin |
| `POST` | `/api/admin/users` | Crear usuario | Admin |

### 🔧 Sistema

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/system/health` | Estado del sistema | No |
| `GET` | `/api/system/debug/recent-data` | Datos de debug | Sí |

## 📊 WebSocket en Tiempo Real

### Conexión
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/production');
```

### Tipos de Mensajes

#### Conexión Establecida
```json
{
  "type": "connection",
  "message": "Connected to production system real-time monitoring",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Datos de Producción en Tiempo Real
```json
{
  "type": "production_data",
  "data": {
    "timestamp": "2024-01-01T12:00:00Z",
    "product_id": 12345,
    "quality_status": "OK",
    "production_count": 100,
    "line_status": "RUNNING",
    "error_code": 0,
    "cycle_time_ms": 2500,
    "temperature": 25.5,
    "pressure": 4.2,
    "operator_id": 1,
    "batch_id": "BATCH_20240101_001"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Ping/Pong (Mantener Conexión)
```json
// Enviar
{ "type": "ping" }

// Recibir
{ "type": "pong", "timestamp": "2024-01-01T12:00:00Z" }
```

## 📈 Modelos de Datos

### ProductionData
```typescript
interface ProductionData {
  timestamp: string;           // ISO 8601
  product_id: number;          // ID único del producto
  quality_status: "OK" | "NOK" | "PENDING";
  production_count: number;    // Contador total
  line_status: "STOPPED" | "RUNNING" | "ERROR" | "MAINTENANCE";
  error_code: number;          // 0 = sin error
  cycle_time_ms: number;       // Tiempo de ciclo en ms
  temperature: number;         // Temperatura en °C
  pressure: number;            // Presión en bar
  operator_id: number;         // ID del operador
  batch_id: string;            // ID del lote
}
```

### ProductionStats
```typescript
interface ProductionStats {
  total_products: number;
  quality_ok_count: number;
  quality_nok_count: number;
  quality_pending_count: number;
  quality_rate_percentage: number;
  average_cycle_time_ms: number;
  last_update: string;
}
```

### User
```typescript
interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  role: "admin" | "supervisor" | "operator" | "viewer";
  is_active: boolean;
  last_login?: string;
  created_at: string;
}
```

## 💻 Ejemplos para Frontend

### 1. Autenticación

```javascript
// Login
async function login(username, password) {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  
  if (response.ok) {
    const { access_token, user } = await response.json();
    localStorage.setItem('token', access_token);
    return { token: access_token, user };
  }
  throw new Error('Login failed');
}

// Headers para requests autenticados
function getAuthHeaders() {
  const token = localStorage.getItem('token');
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };
}
```

### 2. Obtener Datos

```javascript
// Datos actuales
async function getCurrentProduction() {
  const response = await fetch('/api/production/current', {
    headers: getAuthHeaders()
  });
  return response.json();
}

// Historial con filtros
async function getProductionHistory(startDate, endDate, limit = 100) {
  const params = new URLSearchParams({
    start_date: startDate,
    end_date: endDate,
    limit: limit.toString()
  });
  
  const response = await fetch(`/api/production/history?${params}`, {
    headers: getAuthHeaders()
  });
  return response.json();
}

// Estadísticas
async function getProductionStats() {
  const response = await fetch('/api/production/stats', {
    headers: getAuthHeaders()
  });
  return response.json();
}
```

### 3. WebSocket en Tiempo Real

```javascript
class ProductionWebSocket {
  constructor(onData, onError) {
    this.ws = null;
    this.onData = onData;
    this.onError = onError;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect() {
    this.ws = new WebSocket('ws://localhost:8000/ws/production');
    
    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };
    
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      switch (message.type) {
        case 'production_data':
          this.onData(message.data);
          break;
        case 'connection':
          console.log('Connected:', message.message);
          break;
        case 'pong':
          console.log('Pong received');
          break;
      }
    };
    
    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.reconnect();
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.onError(error);
    };
  }

  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => this.connect(), 5000);
    }
  }

  ping() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'ping' }));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// Uso
const websocket = new ProductionWebSocket(
  (data) => {
    // Actualizar UI con nuevos datos
    updateDashboard(data);
  },
  (error) => {
    console.error('WebSocket error:', error);
  }
);

websocket.connect();

// Ping cada 30 segundos
setInterval(() => websocket.ping(), 30000);
```

### 4. React Hook Ejemplo

```javascript
import { useState, useEffect } from 'react';

function useProductionData() {
  const [currentData, setCurrentData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/production');
    
    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);
    ws.onerror = (err) => setError(err);
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'production_data') {
        setCurrentData(message.data);
        setError(null);
      }
    };

    return () => ws.close();
  }, []);

  return { currentData, isConnected, error };
}
```

## 🐳 Docker

### docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
      - "502:502"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:admin@db:5432/production_system
    depends_on:
      - db
    volumes:
      - ./app:/app

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=production_system
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=admin
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### Ejecutar con Docker
```bash
# Construir y ejecutar
docker-compose up --build

# Solo ejecutar
docker-compose up

# En background
docker-compose up -d
```

## 📚 Documentación

### URLs Importantes
- **API Docs (Swagger)**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Dashboard Web**: `http://localhost:8000/`
- **Cliente Tiempo Real**: `http://localhost:8000/client`
- **Health Check**: `http://localhost:8000/api/system/health`

### Simulador PLC
El sistema incluye un simulador PLC para pruebas:

```bash
# Ejecutar simulador
python -m app.simulator.plc_client

# El simulador envía datos cada 2 segundos a las direcciones:
# - Dirección 1: Datos principales
# - Dirección 21: Datos de calidad  
# - Dirección 41: Datos de proceso
```

## 🔍 Troubleshooting

### Problemas Comunes

1. **Puerto 502 en uso**
   ```bash
   # Verificar qué usa el puerto
   lsof -i :502
   
   # Cambiar puerto en .env
   MODBUS_PORT=5020
   ```

2. **Error de conexión a base de datos**
   ```bash
   # Verificar PostgreSQL
   pg_isready -h localhost -p 5432
   
   # Usar SQLite (por defecto)
   DATABASE_URL=sqlite:///./production_system.db
   ```

3. **WebSocket no conecta**
   - Verificar CORS en `.env`
   - Comprobar firewall
   - Usar `ws://` no `wss://` en desarrollo

## 📞 Soporte

Para problemas o preguntas:
1. Revisar logs en `production_system.log`
2. Usar endpoint `/api/system/health` para diagnóstico
3. Verificar `/api/system/debug/recent-data` para datos recientes

---

## 🎯 Resumen para Frontend

### ✅ Lo que está listo:
- ✅ API REST completa con documentación
- ✅ WebSockets para tiempo real
- ✅ Autenticación JWT
- ✅ Validación automática de datos
- ✅ CORS configurado
- ✅ Manejo de errores

### 🚀 Próximos pasos:
1. Implementar autenticación en tu frontend
2. Conectar WebSocket para datos en tiempo real
3. Crear dashboard con los datos de producción
4. Implementar filtros para historial
5. Añadir indicadores visuales de estado

**¡El backend está completamente funcional y listo para tu frontend!** 🎉 