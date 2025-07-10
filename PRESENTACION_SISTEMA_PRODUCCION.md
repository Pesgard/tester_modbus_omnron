# 🏭 Sistema de Producción Industrial AXME
## Documentación Técnica para Presentación al Cliente

---

## 📋 Índice de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Base de Datos](#base-de-datos)
4. [Flujo de Datos](#flujo-de-datos)
5. [Protocolo Modbus](#protocolo-modbus)
6. [API REST](#api-rest)
7. [Frontend Web](#frontend-web)
8. [Roles y Seguridad](#roles-y-seguridad)
9. [Despliegue](#despliegue)
10. [Especificaciones Técnicas](#especificaciones-técnicas)
11. [Casos de Uso](#casos-de-uso)
12. [Roadmap y Mejoras](#roadmap-y-mejoras)

---

## 📊 Resumen Ejecutivo

### 🎯 Objetivo del Sistema
Sistema integral de monitoreo y control de producción industrial que integra equipos PLC mediante protocolo Modbus TCP, proporcionando visualización en tiempo real, análisis histórico y gestión de calidad.

### ✨ Características Principales
- **📡 Comunicación Industrial**: Protocolo Modbus TCP para integración con PLCs
- **⏱️ Tiempo Real**: Dashboard con datos en vivo mediante WebSockets
- **🎯 Control de Calidad**: Inspección visual con 2-3 cámaras por modelo
- **📊 Análisis Histórico**: Reportes detallados y análisis de tendencias
- **🔐 Seguridad**: Autenticación JWT con 4 niveles de acceso
- **🖥️ Despliegue**: Servidor único optimizado para producción

### 🏆 Beneficios Clave
- **Visibilidad Total**: Monitoreo 24/7 de líneas de producción
- **Calidad Asegurada**: Detección automática de defectos
- **Trazabilidad Completa**: Registro de todas las operaciones
- **Escalabilidad**: Arquitectura preparada para crecimiento
- **Integración**: Compatible con sistemas existentes

---

## 🏗️ Arquitectura del Sistema

El sistema utiliza una arquitectura optimizada para entornos industriales, desplegado en servidor único para máxima simplicidad y confiabilidad operativa.

### Diagrama de Arquitectura General
```mermaid
graph TB
    subgraph "🏭 PLC Externo (192.168.1.100)"
        PLC[PLC/Equipos] --> Sensors[Sensores/Cámaras]
        PLC --> ModbusTCP[Modbus TCP]
    end
    
    subgraph "🖥️ Servidor Principal (192.168.1.200)"
        ModbusTCP -.->|Puerto 502| Backend[Backend FastAPI]
        Backend --> PostgreSQL[(PostgreSQL Local)]
        Backend --> WebSocket[WebSocket Server]
        WebSocket --> Frontend[Frontend SvelteKit]
        Backend --> API[REST API]
        API --> Frontend
        
        subgraph "Servicios Sistema"
            SystemdBackend[backend.service]
            SystemdFrontend[frontend.service]
            SystemdDB[postgresql.service]
        end
    end
    
    subgraph "👥 Usuarios Finales"
        Frontend -.->|Puerto 3000| Users[Navegadores Web]
        Users --> Tablets[Tablets Industriales]
        Users --> Mobile[Dispositivos Móviles]
        Users --> Desktop[Estaciones Trabajo]
    end
```

### 🧩 Componentes Principales

#### 🏭 Hardware Industrial Externo
- **PLCs/Controladores**: Comunicación vía Modbus TCP (IP: 192.168.1.100)
- **Cámaras de Inspección**: Verificación automática de calidad integradas al PLC
- **Sensores de Proceso**: Temperatura, presión, vibración conectados al PLC
- **Red Industrial**: Switch Ethernet con QoS configurado

#### ⚙️ Backend (FastAPI) - Servidor
- **Servidor Modbus**: Puerto 502, recepción de datos industriales
- **Procesador de Datos**: Validación y transformación en tiempo real
- **API REST**: Puerto 8000, endpoints para frontend y terceros
- **WebSocket Manager**: Comunicación tiempo real bidireccional
- **Base de Datos**: PostgreSQL local para máximo rendimiento

#### 🖥️ Frontend (SvelteKit) - Servidor
- **Dashboard Tiempo Real**: Puerto 3000, monitoreo operativo
- **Análisis Histórico**: Reportes y tendencias interactivos
- **Gestión del Sistema**: Administración usuarios y configuración
- **Responsive Design**: Compatible con dispositivos móviles e industriales

#### 🖥️ Infraestructura del Servidor
- **Sistema Operativo**: Ubuntu 20.04 LTS con systemd
- **Python Runtime**: 3.11 con virtual environment
- **Node.js Runtime**: 18 LTS para frontend
- **Base de Datos**: PostgreSQL 15 local con backup automático
- **Monitoreo**: Health checks cada 15 minutos
- **Seguridad**: Firewall UFW configurado

### 🔄 Patrones de Diseño
- **Clean Architecture**: Separación clara de responsabilidades
- **Repository Pattern**: Abstracción de acceso a datos
- **Observer Pattern**: Notificaciones tiempo real
- **Factory Pattern**: Creación de servicios
- **Service Layer**: Lógica de negocio encapsulada

### 🏆 Ventajas de la Arquitectura de Servidor Único
- **Simplicidad**: Un solo punto de administración y mantenimiento
- **Rendimiento**: Comunicación directa entre componentes sin overhead
- **Confiabilidad**: Menos puntos de falla, mayor estabilidad
- **Costo**: Menor infraestructura requerida
- **Mantenimiento**: Updates y backups centralizados

---

## 🗄️ Base de Datos

### Esquema de Base de Datos
*[Ver diagrama ER creado anteriormente]*

### 📊 Tablas Principales

#### production_records
Registro principal de cada pieza producida
- **Datos básicos**: timestamp, product_id, quality_status
- **Métricas**: cycle_time_ms, production_count
- **Estado**: line_status, error_code
- **Proceso**: temperature, pressure
- **Trazabilidad**: operator_id, batch_id

#### quality_records
Datos detallados de inspección de calidad
- **Dimensiones**: medidas físicas en mm
- **Superficie**: rugosidad en μm
- **Dureza**: valores HRC
- **Inspección visual**: resultado booleano

#### process_records
Parámetros de proceso y monitoreo
- **Temperaturas**: múltiples líneas
- **Presiones**: hidráulica y neumática
- **Energía**: consumo y velocidad
- **Estado**: sensores y alarmas

### 👥 Gestión de Usuarios
- **users**: Credenciales y perfiles
- **permissions**: Control granular de acceso
- **audit_logs**: Trazabilidad de acciones
- **system_events**: Eventos del sistema

---

## 🔄 Flujo de Datos

### Diagrama de Secuencia
*[Ver diagrama de flujo de datos creado anteriormente]*

### 📥 Proceso de Ingesta
1. **PLC envía datos** vía Modbus TCP cada 2-3 segundos
2. **Servidor Modbus** recibe y valida datos
3. **Procesador** transforma y enriquece información
4. **Base de datos** almacena de forma asíncrona
5. **WebSocket** difunde a clientes conectados

### 🎯 Tipos de Datos
- **Dirección 0-1**: Datos principales de producción
- **Dirección 20-21**: Resultados de inspección de calidad
- **Dirección 40-41**: Parámetros de proceso operativo

### ⚡ Rendimiento
- **Buffer**: 1000 registros en memoria
- **Procesamiento**: Thread asíncrono dedicado
- **Base de datos**: Pool de 20 conexiones
- **WebSocket**: Hasta 200 conexiones simultáneas

---

## 📡 Protocolo Modbus

### Mapeo de Direcciones
*[Ver diagrama de mapeo Modbus creado anteriormente]*

### 🏭 Modelos de Producto Soportados

| Modelo | Cámaras | Color | Pruebas Eléctricas | Tiempo Ciclo |
|--------|---------|-------|-------------------|--------------|
| **Modelo 1** | 2 | Azul | High Pot + Continuidad | 2500ms |
| **Modelo 2** | 3 | Rojo | Solo High Pot | 3200ms |
| **Modelo 3** | 2 | Verde | Solo Continuidad | 1800ms |
| **Modelo 4** | 3 | Amarillo | High Pot + Continuidad | 4000ms |

### 🚨 Códigos de Falla
- **0**: Sin falla
- **1**: Componente faltante
- **2**: Error etiqueta
- **3**: Color incorrecto
- **4**: Falla eléctrica general
- **5**: Falla continuidad
- **6**: Falla High Pot
- **7**: Error cámara
- **8**: Error posicionamiento

### 📊 Registro de Datos
- **Principales (0-9)**: Estado general y producción
- **Calidad (20-29)**: Resultados inspección
- **Proceso (40-49)**: Parámetros operativos

---

## 🌐 API REST

### Documentación de Endpoints
*[Ver diagrama de API endpoints creado anteriormente]*

### 🔐 Autenticación
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Respuesta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "email": "admin@company.com"
  }
}
```

### 📊 Datos de Producción
```http
GET /api/production/current
Authorization: Bearer <token>
```

**Respuesta:**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "product_id": 12345,
  "quality_status": "OK",
  "production_count": 150,
  "line_status": "RUNNING",
  "error_code": 0,
  "cycle_time_ms": 2500,
  "temperature": 25.5,
  "pressure": 4.2,
  "operator_id": 101,
  "batch_id": "BATCH_20240115_001"
}
```

### 📈 Estadísticas
```http
GET /api/production/stats
Authorization: Bearer <token>
```

**Respuesta:**
```json
{
  "total_products": 1500,
  "quality_ok_count": 1425,
  "quality_nok_count": 75,
  "quality_rate_percentage": 95.0,
  "average_cycle_time_ms": 2450,
  "last_update": "2024-01-15T10:30:00Z"
}
```

### 📚 Documentación Interactiva
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 💻 Frontend Web

### Estructura del Frontend
*[Ver diagrama de estructura frontend creado anteriormente]*

### 🖥️ Páginas Principales

#### 🏠 Dashboard Principal
- **Estado en Tiempo Real**: Indicadores visuales de línea
- **KPIs Clave**: Producción, calidad, eficiencia
- **Gráficos**: Temperatura, presión, vibración
- **Alertas**: Notificaciones automáticas de problemas

#### 📈 Análisis Histórico
- **Filtros Avanzados**: Por fecha, modelo, operador
- **Análisis de Fallas**: Desglose por tipo y frecuencia
- **Tendencias**: Gráficos de productividad y calidad
- **Exportación**: CSV, PDF, Excel

#### ⚙️ Gestión del Sistema
- **Usuarios**: CRUD completo (solo admin)
- **Configuración**: Parámetros del sistema
- **Auditoría**: Logs de actividad
- **Mantenimiento**: Herramientas de diagnóstico

### 🎨 Tecnologías UI
- **SvelteKit 2.16**: Framework moderno y eficiente
- **Skeleton UI 3.1**: Componentes profesionales
- **TailwindCSS 4.0**: Diseño responsive
- **Lucide Icons**: Iconografía consistente

### 📱 Características UX
- **Responsive Design**: Adaptable a todos los dispositivos
- **Tiempo Real**: Actualizaciones automáticas
- **Offline Ready**: Funcionalidad sin conexión
- **Accesibilidad**: WCAG 2.1 AA compliant

---

## 🔐 Roles y Seguridad

### Flujo de Autenticación
*[Ver diagrama de roles y autenticación creado anteriormente]*

### 👥 Niveles de Acceso

#### 👨‍💼 Administrador
- **Acceso Total**: Todas las funcionalidades
- **Gestión Usuarios**: Crear, modificar, eliminar
- **Configuración**: Parámetros del sistema
- **Auditoría**: Logs completos de actividad

#### 👨‍🔧 Supervisor
- **Supervisión**: Oversight de producción
- **Reportes**: Análisis avanzados
- **Lotes**: Crear y gestionar lotes
- **Calidad**: Análisis detallado

#### 👨‍🏭 Operador
- **Monitoreo**: Dashboard tiempo real
- **Control**: Operación básica de línea
- **Historial**: Consulta datos producción
- **Alertas**: Notificaciones de problemas

#### 👀 Visualizador
- **Solo Lectura**: Sin modificaciones
- **Dashboard**: Visualización básica
- **Consultas**: Datos de producción
- **Reportes**: Acceso limitado

### 🛡️ Medidas de Seguridad
- **JWT Tokens**: Expiración 30 minutos
- **Bcrypt Hashing**: Contraseñas seguras
- **CORS Policy**: Protección cross-origin
- **Rate Limiting**: Prevención de ataques
- **Audit Trail**: Trazabilidad completa

---

## 🐳 Despliegue

### Arquitectura de Contenedores
*[Ver diagrama de despliegue creado anteriormente]*

### 📦 Componentes Docker

#### 🗄️ Base de Datos
```yaml
postgres:
  image: postgres:15-alpine
  ports: ["5432:5432"]
  environment:
    POSTGRES_DB: production_system
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: password
  volumes:
    - postgres_data:/var/lib/postgresql/data
    - ./init-db.sql:/docker-entrypoint-initdb.d/
```

#### 🚀 Backend API
```yaml
backend:
  build: ./backend
  ports: ["8000:8000", "502:502"]
  depends_on: [postgres]
  environment:
    DATABASE_URL: postgresql+asyncpg://postgres:password@postgres:5432/production_system
  volumes:
    - ./logs:/app/logs
```

#### 💻 Frontend
```yaml
frontend:
  build: ./frontend
  ports: ["3000:3000"]
  depends_on: [backend]
  environment:
    VITE_API_URL: http://localhost:8000
```

### ⚙️ Configuración de Producción
- **Health Checks**: Monitoreo automático
- **Restart Policies**: Alta disponibilidad
- **Resource Limits**: Control de recursos
- **Security Context**: Usuario no-root
- **Secrets Management**: Variables seguras

### 🔧 Comandos de Despliegue
```bash
# Desarrollo completo
docker-compose up -d

# Solo base de datos
docker-compose up postgres -d

# Con herramientas de desarrollo
docker-compose --profile development up -d

# Verificar estado
docker-compose ps
docker-compose logs -f
```

---

## 📋 Especificaciones Técnicas

### 🖥️ Requisitos del Sistema

#### Hardware Mínimo
- **CPU**: 4 cores, 2.5GHz
- **RAM**: 8GB DDR4
- **Almacenamiento**: 100GB SSD
- **Red**: Gigabit Ethernet

#### Software
- **OS**: Linux Ubuntu 20.04+ / Windows 10+ / macOS 11+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Python**: 3.11+ (para desarrollo)
- **Node.js**: 18+ (para frontend)

### 📊 Capacidad y Rendimiento

#### Datos de Producción
- **Frecuencia**: 2-3 segundos por registro
- **Almacenamiento**: ~2MB por día de operación
- **Retención**: 2 años (configurable)
- **Throughput**: 1000 registros/minuto

#### Usuarios Concurrentes
- **WebSocket**: 200 conexiones simultáneas
- **API REST**: 500 requests/minuto
- **Dashboard**: 50 usuarios activos
- **Base de datos**: 20 conexiones pool

### 🔧 Tecnologías Utilizadas

#### Backend
- **FastAPI 0.104**: Framework web asíncrono
- **SQLAlchemy 2.0**: ORM base de datos
- **PyModbus 3.5**: Comunicación industrial
- **Pydantic 2.0**: Validación de datos
- **Passlib**: Hashing contraseñas
- **AsyncPG**: Driver PostgreSQL asíncrono

#### Frontend
- **SvelteKit 2.16**: Framework web moderno
- **Skeleton UI 3.1**: Biblioteca componentes
- **TailwindCSS 4.0**: Framework CSS utility-first
- **TypeScript 5.0**: Tipado estático
- **Vite 6.2**: Build tool rápido

#### Base de Datos
- **PostgreSQL 15**: Base de datos principal
- **Redis 7**: Cache y sesiones
- **pgAdmin 4**: Herramienta gestión

---

## 📋 Casos de Uso

### 🏭 Escenario 1: Operación Normal
1. **PLC envía datos** cada 2 segundos
2. **Sistema procesa** y valida información
3. **Dashboard actualiza** indicadores en tiempo real
4. **Operador monitorea** estado de línea
5. **Base de datos almacena** histórico completo

### 🚨 Escenario 2: Detección de Falla
1. **Cámara detecta** componente faltante
2. **Sistema registra** código falla 1
3. **Alerta inmediata** en dashboard
4. **Supervisor recibe** notificación
5. **Acción correctiva** documentada

### 📊 Escenario 3: Análisis de Calidad
1. **Supervisor accede** a análisis histórico
2. **Filtra datos** por modelo y fecha
3. **Identifica tendencias** de calidad
4. **Genera reporte** detallado
5. **Implementa mejoras** en proceso

### 👥 Escenario 4: Gestión de Usuarios
1. **Admin crea** nuevo usuario operador
2. **Asigna permisos** específicos
3. **Usuario inicia sesión** con credenciales
4. **Sistema valida** rol y permisos
5. **Acceso limitado** según rol asignado

---

## 🚀 Roadmap y Mejoras

### 📅 Fase 1 (Actual) - Core System
- ✅ Comunicación Modbus TCP
- ✅ Dashboard tiempo real
- ✅ Base de datos PostgreSQL
- ✅ Autenticación JWT
- ✅ Análisis básico

### 📅 Fase 2 (Q2 2024) - Mejoras Operativas
- 🔄 **Machine Learning**: Predicción de fallas
- 🔄 **Móvil**: App iOS/Android
- 🔄 **Reportes**: Templates personalizables
- 🔄 **Integraciones**: ERP/MES systems
- 🔄 **APIs**: Webhooks y eventos

### 📅 Fase 3 (Q3 2024) - Escalabilidad
- 🔄 **Microservicios**: Arquitectura distribuida
- 🔄 **Kubernetes**: Orquestación avanzada
- 🔄 **Multi-tenant**: Múltiples clientes
- 🔄 **Edge Computing**: Procesamiento local
- 🔄 **Analytics**: BI y dashboards ejecutivos

### 📅 Fase 4 (Q4 2024) - IA y Automatización
- 🔄 **Computer Vision**: Inspección automática
- 🔄 **Predictive Analytics**: Mantenimiento preventivo
- 🔄 **Auto-scaling**: Capacidad dinámica
- 🔄 **Digital Twin**: Simulación virtual
- 🔄 **IoT Expansion**: Sensores adicionales

### 💡 Mejoras Propuestas
- **Performance**: Optimización consultas DB
- **Seguridad**: OAuth2 y SSO
- **Monitoreo**: Prometheus y Grafana
- **Backup**: Estrategia automática
- **Testing**: Cobertura 90%+

---

## 📞 Información de Contacto

### 👨‍💻 Equipo de Desarrollo
- **Arquitecto de Software**: Especialista en sistemas industriales
- **Desarrollador Backend**: Expert en FastAPI y bases de datos
- **Desarrollador Frontend**: Specialist en SvelteKit y UX
- **DevOps Engineer**: Docker y despliegue automático

### 📧 Soporte Técnico
- **Email**: support@axme-industrial.com
- **Documentación**: https://docs.axme-industrial.com
- **GitHub**: https://github.com/axme-industrial/production-system
- **Slack**: #production-system-support

### 🔧 Servicios Ofrecidos
- **Instalación**: Setup completo y configuración
- **Capacitación**: Training para usuarios finales
- **Soporte**: 24/7 durante primeros 3 meses
- **Mantenimiento**: Updates y mejoras continuas
- **Consultoría**: Optimización y nuevas funcionalidades

---

## 📝 Notas Finales

Este sistema representa una solución integral para el monitoreo y control de producción industrial, diseñado con las mejores prácticas de desarrollo de software y arquitectura de sistemas.

La implementación utiliza tecnologías modernas y probadas en la industria, garantizando escalabilidad, mantenibilidad y seguridad.

El enfoque modular permite adaptación a diferentes entornos industriales y facilita la integración con sistemas existentes.

**¿Preguntas o necesita más detalles sobre algún aspecto específico?**

---

*Documento generado para presentación al cliente - AXME Industrial Production System*
*Versión: 2.0 | Fecha: Enero 2024* 

