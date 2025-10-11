# 🏭 Sistema de Tests en Tiempo Real - PLC Control & Quality Management

> **Sistema de monitoreo industrial** para control de calidad en tiempo real con integración PLC, gestión de lotes y trazabilidad completa.

---

## 📋 Tabla de Contenidos

- [🎯 Resumen Ejecutivo](#-resumen-ejecutivo)
- [🏗️ Arquitectura del Sistema](#️-arquitectura-del-sistema)
- [💻 Stack Tecnológico](#-stack-tecnológico)
- [📊 Modelo de Datos](#-modelo-de-datos)
- [🔌 APIs y Eventos](#-apis-y-eventos)
- [📁 Estructura del Proyecto](#-estructura-del-proyecto)
- [✅ Estado Actual de Implementación](#-estado-actual-de-implementación)
- [🚀 Roadmap de Desarrollo](#-roadmap-de-desarrollo)
- [⚙️ Configuración e Instalación](#️-configuración-e-instalación)
- [🔒 Seguridad y Permisos](#-seguridad-y-permisos)
- [📖 Guías de Desarrollo](#-guías-de-desarrollo)

---

## 🎯 Resumen Ejecutivo

### Problema que Resuelve
Este sistema automatiza el control de calidad industrial integrando un **PLC (Controlador Lógico Programable)** con una aplicación web moderna para:

- **Recibir datos de pruebas** desde el PLC vía TCP/Modbus
- **Procesar piezas** organizadas en lotes de producción
- **Almacenar resultados** con trazabilidad completa
- **Capturar imágenes** de fallas vía FTP
- **Notificar en tiempo real** al dashboard operativo
- **Controlar el PLC** (señales de pausa/stop cuando se alcanza la meta)

### Objetivos del MVP
- ✅ **Trazabilidad completa** con historial de acciones
- ✅ **Sistema robusto** de roles y permisos
- ✅ **Interface operativa** en tiempo real
- ✅ **Confiabilidad** en la lógica de lotes
- ✅ **Integración industrial** estable

---

## 🏗️ Arquitectura del Sistema

```mermaid
flowchart LR
    PLC[🏭 PLC/Omron] 
    TCP[🔌 TCP Server<br/>Puerto 900]
    PLCAdapter[⚙️ PLC Adapter<br/>Procesamiento datos]
    UseCases[📋 Use Cases<br/>registrarPieza<br/>cerrarLote]
    DB[(🗄️ PostgreSQL<br/>Prisma ORM)]
    WS[📡 WebSocket Hub<br/>Socket.IO]
    FTP[📁 FTP Server<br/>Imágenes]
    FTPAdapter[🖼️ FTP Adapter<br/>Chokidar Watch]
    Frontend[🌐 Dashboard<br/>SvelteKit + Skeleton UI]
    Auth[🔐 Auth System<br/>Lucia + Hooks]

    PLC -->|Datos TCP| TCP
    TCP --> PLCAdapter
    PLCAdapter --> UseCases
    UseCases --> DB
    UseCases --> WS
    WS --> Frontend
    FTP --> FTPAdapter
    FTPAdapter --> UseCases
    Frontend --> Auth
    Auth --> UseCases
    
    classDef plc fill:#ff6b6b,stroke:#ff5252,color:#fff
    classDef core fill:#4ecdc4,stroke:#26a69a,color:#fff
    classDef ui fill:#45b7d1,stroke:#2196f3,color:#fff
    classDef data fill:#96ceb4,stroke:#4caf50,color:#fff
    
    class PLC,TCP plc
    class PLCAdapter,UseCases,Auth core
    class Frontend,WS ui
    class DB,FTP,FTPAdapter data
```

### Componentes Principales

#### 🔌 **Capa de Comunicación**
- **TCP Server** (`tcp.server.ts`): Recibe datos del PLC en puerto 900
- **WebSocket Hub** (`ws.server.ts`): Comunicación bidireccional con frontend
- **FTP Watcher** (`ftp-image-watcher.server.ts`): Monitoreo de imágenes

#### ⚙️ **Capa de Negocio**
- **Use Cases**: Lógica de negocio pura y testeable
- **Adaptadores**: Integración con sistemas externos (PLC, FTP)
- **Repositorios**: Acceso a datos vía Prisma

#### 🎨 **Capa de Presentación**
- **SvelteKit Frontend**: Dashboard operativo
- **Skeleton UI**: Sistema de componentes
- **Hooks Server**: Autenticación y autorización

---

## 💻 Stack Tecnológico

### **Backend**
- **🟢 Node.js** con TypeScript
- **⚡ SvelteKit 2** (SSR + SPA)
- **🗄️ PostgreSQL** con Prisma ORM
- **🔐 Lucia Auth** con adaptador Prisma
- **📡 Socket.IO** para WebSockets
- **📁 basic-ftp** + Chokidar para FTP

### **Frontend**
- **🎨 Svelte 5** con Runes
- **🎭 Skeleton UI v3** (componentes)
- **🎨 TailwindCSS v4** (estilos)
- **📱 Responsive Design**

### **Base de Datos**
```sql
🗄️ PostgreSQL Schema:
├── Users & Auth (User, Session, Role, Permiso)
├── Production (Lote, Pieza, Imagen)
├── Audit (Historial, EventoExterno)
└── Indices optimizados para consultas frecuentes
```

### **Desarrollo**
- **📦 PNPM** (gestor de paquetes)
- **🔧 Vite** (build tool)
- **✅ ESLint + Prettier** (calidad de código)
- **🧪 Vitest** (testing unitario)
- **🎭 Playwright** (testing E2E)

---

## 📊 Modelo de Datos

### Entidades Principales

```typescript
// 👤 AUTENTICACIÓN
User {
  id: string
  username: string (unique)
  hash_password: string
  active: boolean
  roles: UserRole[]
}

// 🏷️ AUTORIZACIÓN  
Role {
  id: string
  name: string (unique) // "admin", "operador", "viewer"
  permissions: PermisoRol[]
}

// 📦 PRODUCCIÓN
Lote {
  id: string
  name: string
  estado: "OPEN" | "CLOSED" | "PAUSED"
  piezasOk: number
  piezasFallas: number
  maxPiezasOk: number
  startedAt: DateTime
  closedAt?: DateTime
  piezas: Pieza[]
}

// 🔧 PIEZAS
Pieza {
  id: string
  loteId: string
  resultadoBits: Json // [true, false, true, false, true, false]
  ok: boolean // evaluado de resultadoBits
  imagenPath?: string
  processedAt: DateTime
  processedBy?: string
}

// 📸 IMÁGENES
Imagen {
  id: string
  piezaId: string
  path: string
  thumbnailPath?: string
  uploadedAt: DateTime
}

// 📋 TRAZABILIDAD
Historial {
  id: string
  loteId?: string
  piezaId?: string
  userId?: string
  actionKey: string // "pieza.registrada", "lote.cerrado", etc.
  meta: Json
  createdAt: DateTime
}
```

### Relaciones Clave
- **Usuario ↔ Roles**: Muchos a muchos
- **Lote ↔ Piezas**: Uno a muchos
- **Pieza ↔ Imágenes**: Uno a muchos
- **Historial**: Referencias opcionales a User, Lote, Pieza

---

## 🔌 APIs y Eventos

### 🌐 REST Endpoints
```typescript
// 🔐 AUTENTICACIÓN
POST   /api/auth/login    // { username, password }
POST   /api/auth/logout   // Cierra sesión

// 📦 LOTES
GET    /api/lotes         // Lista lotes (filtros, paginación)
POST   /api/lotes         // Crear lote { name, maxPiezasOk }
GET    /api/lotes/:id     // Detalle lote + piezas
POST   /api/lotes/:id/close // Cerrar lote manualmente

// 🔧 PIEZAS
GET    /api/piezas/:id/image // Proxy seguro para imagen FTP

// 📋 HISTORIAL
GET    /api/historial     // Eventos de auditoría
```

### 📡 WebSocket Events

#### **📤 Emitidos por el servidor:**
```typescript
'pieza:procesada' → {
  piezaId: string,
  loteId: string,
  ok: boolean,
  resultadoBits: boolean[],
  processedAt: DateTime
}

'lote:actualizado' → {
  loteId: string,
  piezasOk: number,
  piezasFallas: number,
  estado: string
}

'lote:cerrado' → {
  loteId: string,
  closedAt: DateTime
}

'system:alert' → {
  level: 'info' | 'warning' | 'error',
  message: string
}
```

#### **📥 Recibidos del cliente:**
```typescript
'lote:pause'  → { loteId: string }
'lote:resume' → { loteId: string }
'request:loteDetalle' → { loteId: string }
```

---

## 📁 Estructura del Proyecto

```
plc-app/
├── 📄 prisma/
│   ├── schema.prisma           # Modelo de datos
│   ├── migrations/             # Migraciones SQL
│   └── seed.js                 # Datos iniciales
├── 🎯 src/
│   ├── 🎨 routes/             # Páginas SvelteKit
│   │   ├── +layout.svelte     # Layout principal
│   │   ├── +page.svelte       # Dashboard principal
│   │   ├── login/+page.svelte # Login
│   │   ├── dashboard/         # Dashboard operativo
│   │   └── api/               # ❌ PENDIENTE: Endpoints REST
│   ├── 📚 lib/
│   │   ├── prisma.ts          # Cliente Prisma
│   │   └── 🔧 server/
│   │       ├── startup.ts     # Inicialización servicios
│   │       ├── 🔐 auth/
│   │       │   └── Auth.ts    # Configuración Lucia
│   │       ├── 🌐 tcp/
│   │       │   └── tcp.server.ts # Servidor TCP
│   │       ├── 📡 ws/
│   │       │   └── ws.server.ts  # WebSocket básico
│   │       ├── 📁 ftp/
│   │       │   └── ftp-image-watcher.server.ts
│   │       ├── ⚙️ adapters/   # ❌ PENDIENTE
│   │       ├── 📋 usecases/   # ❌ PENDIENTE
│   │       └── 🏪 repositories/ # ❌ PENDIENTE
│   ├── hooks.server.ts        # Auth middleware
│   └── app.d.ts              # Tipos globales
├── 📦 ftp/                   # Directorio FTP watched
├── 🐳 docker-compose.yml     # PostgreSQL local
└── 📋 package.json           # Dependencies
```

---

## ✅ Estado Actual de Implementación

### 🟢 **COMPLETADO**

#### 🔐 **Autenticación & Seguridad**
- ✅ Lucia Auth configurado con Prisma
- ✅ Sistema de sesiones con cookies httpOnly
- ✅ Hooks de servidor para validación
- ✅ Páginas de login/register funcionales

#### 🗄️ **Base de Datos**
- ✅ Schema Prisma completo y migrado
- ✅ Relaciones entre entidades definidas
- ✅ Índices para optimización
- ✅ Tipos TypeScript generados

#### 🔌 **Infraestructura de Comunicación**
- ✅ Servidor TCP (puerto 900) para PLC
- ✅ WebSocket básico con broadcast
- ✅ FTP Image Watcher funcional
- ✅ Startup service orchestration

#### 🎨 **Frontend Base**
- ✅ SvelteKit 2 + Skeleton UI configurado
- ✅ Layout principal y rutas básicas
- ✅ Páginas de autenticación
- ✅ Estilos TailwindCSS

### 🔴 **PENDIENTE DE IMPLEMENTAR**

#### 📋 **Casos de Uso (Critical Path)**
```
❌ src/lib/server/usecases/
├── registrarPieza.ts     # Core: procesar pieza del PLC
├── cerrarLote.ts         # Core: finalizar lote
├── crearLote.ts          # Admin: crear nuevo lote
└── obtenerHistorial.ts   # Query: auditoría
```

#### 🌐 **API REST Endpoints**
```
❌ src/routes/api/
├── auth/login|logout/+server.ts
├── lotes/+server.ts (GET/POST)
├── lotes/[id]/+server.ts
├── lotes/[id]/close/+server.ts
├── piezas/[id]/image/+server.ts
└── historial/+server.ts
```

#### ⚙️ **Adaptadores de Integración**
```
❌ src/lib/server/adapters/
├── PLCAdapter.ts         # Procesar datos TCP del PLC
└── FTPAdapter.ts         # Gestión avanzada de imágenes
```

#### 📡 **WebSocket Hub Completo**
- ❌ Upgrade a Socket.IO con rooms
- ❌ Autenticación en handshake
- ❌ Sistema de permisos por evento
- ❌ Emisores para casos de uso

#### 🎨 **Dashboard Operativo**
- ❌ UI en tiempo real para lotes
- ❌ Visualización de piezas procesadas
- ❌ Gestión de estados de lote
- ❌ Historial y reportes

#### 🔒 **Sistema de Permisos**
- ❌ Función `hasPermission` helper
- ❌ Middleware de autorización
- ❌ Seed de roles y permisos iniciales

---

## 🚀 Roadmap de Desarrollo

### **📅 Sprint 1: Core Backend (Semana 1)**
**Objetivo**: Implementar la lógica de negocio central

#### Tasks:
1. **📋 Use Cases Principales**
   ```typescript
   // Prioridad ALTA
   - registrarPieza(loteId, resultadoBits, meta)
   - cerrarLote(loteId, userId)
   - crearLote(name, maxPiezasOk, userId)
   ```

2. **🌐 API REST Core**
   ```typescript
   // Endpoints críticos
   - POST /api/lotes (crear)
   - GET  /api/lotes (listar)
   - GET  /api/lotes/:id (detalle)
   - POST /api/lotes/:id/close (cerrar)
   ```

3. **🔒 Sistema de Permisos**
   ```typescript
   // Helper y middleware
   - hasPermission(user, permisoKey)
   - Seed roles: admin, operador, viewer
   - Middleware de autorización en endpoints
   ```

#### Entregables:
- ✅ Use cases testeados unitariamente
- ✅ Endpoints REST funcionais
- ✅ Sistema de permisos operativo

---

### **📅 Sprint 2: Tiempo Real (Semana 2)**
**Objetivo**: Integrar comunicación en tiempo real

#### Tasks:
1. **📡 WebSocket Hub Avanzado**
   ```typescript
   // Upgrade a Socket.IO
   - Autenticación en handshake
   - Rooms por usuario/rol
   - Emisores desde use cases
   ```

2. **⚙️ PLC Integration**
   ```typescript
   // PLCAdapter completo
   - Parsing de datos TCP
   - Validación y normalización
   - Delegación a registrarPieza
   - Señales de control al PLC
   ```

3. **📁 FTP Integration**
   ```typescript
   // FTPAdapter avanzado
   - Asociación imagen → pieza
   - Procesamiento y thumbnails
   - Cache y proxy seguro
   ```

#### Entregables:
- ✅ Pipeline PLC → UseCase → WebSocket funcional
- ✅ Imágenes asociadas a piezas automáticamente
- ✅ Dashboard recibe eventos en tiempo real

---

### **📅 Sprint 3: Frontend Operativo (Semana 3)**
**Objetivo**: Dashboard completo y funcional

#### Tasks:
1. **🎨 Dashboard en Tiempo Real**
   ```svelte
   // Componentes principales
   - LoteActual (estado, contadores, progreso)
   - ListaPiezas (últimas procesadas, OK/NOK)
   - AlertasOperativas (sistema, errores)
   ```

2. **📊 Gestión de Lotes**
   ```svelte
   // CRUD lotes
   - Crear nuevo lote
   - Ver historial de lotes
   - Detalle de lote con piezas
   - Acciones: pausar, reanudar, cerrar
   ```

3. **🖼️ Visualización de Imágenes**
   ```svelte
   // Gallery y viewer
   - Thumbnail grid
   - Modal viewer con zoom
   - Filtros por estado (OK/NOK)
   ```

#### Entregables:
- ✅ Dashboard operativo completo
- ✅ UX fluida y responsive
- ✅ Todas las funcionalidades principales

---

### **📅 Sprint 4: Pulimiento y Testing (Semana 4)**
**Objetivo**: Sistema robusto y production-ready

#### Tasks:
1. **🧪 Testing Integral**
   ```typescript
   // Cobertura completa
   - Unit tests: use cases
   - Integration tests: endpoints + DB
   - E2E tests: flujos completos
   - Performance tests: carga PLC
   ```

2. **🔧 Optimización**
   ```typescript
   // Performance y confiabilidad
   - Indices DB optimizados
   - Connection pooling
   - Rate limiting
   - Error handling robusto
   ```

3. **📖 Documentación**
   ```markdown
   // Docs completas
   - API documentation
   - Deployment guide
   - User manual
   - Troubleshooting guide
   ```

#### Entregables:
- ✅ Sistema completamente testeado
- ✅ Performance optimizada
- ✅ Documentación completa
- ✅ Ready for production

---

## ⚙️ Configuración e Instalación

### **🔧 Requisitos Previos**
- Node.js 18+ 
- PostgreSQL 14+
- PNPM 8+

### **📦 Instalación Inicial**

```bash
# Clonar e instalar dependencias
git clone <repository>
cd plc-app
pnpm install

# Configurar base de datos
cp .env.example .env
# Editar DATABASE_URL en .env

# Levantar PostgreSQL (Docker)
docker-compose up -d

# Migrar base de datos
npx prisma generate
npx prisma migrate dev --name init

# Seed datos iniciales
node prisma/seed.js

# Iniciar desarrollo
pnpm run dev
```

### **🌍 Variables de Entorno**
```bash
# .env
DATABASE_URL="postgresql://postgres:password@localhost:5432/plc_app"
FTP_WATCH_DIR="/home/user/ftp"
FTP_BASE_DIR="/home/user/ftp/processed"
QC_DEST_DIR="/home/user/ftp/quality_control"
NODE_ENV="development"
```

### **🐳 Docker Development**
```yaml
# docker-compose.yml incluido
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: plc_app
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
```

---

## 🔒 Seguridad y Permisos

### **🛡️ Autenticación**
- **Lucia Auth** con sesiones seguras
- **Cookies httpOnly** + SameSite
- **Hashing Argon2id** para passwords
- **Session timeout** configurable

### **🔐 Autorización**
```typescript
// Sistema de permisos granular
Permisos = {
  'lote.crear',
  'lote.cerrar', 
  'lote.pausar',
  'pieza.ver',
  'pieza.procesar',
  'historial.ver',
  'admin.users',
  'admin.config'
}

Roles = {
  admin: ['*'],
  operador: ['lote.*', 'pieza.*', 'historial.ver'],
  viewer: ['pieza.ver', 'historial.ver']
}
```

### **🛡️ Validaciones**
- **Input sanitization** en todos los endpoints
- **Rate limiting** para APIs
- **CSRF protection** automático (SvelteKit)
- **SQL injection** prevention (Prisma)

---

## 📖 Guías de Desarrollo

### **🔧 Añadir Nuevo Use Case**
```typescript
// 1. Crear archivo en src/lib/server/usecases/
export async function miNuevoUseCase(params: MiParams) {
  return await prisma.$transaction(async (tx) => {
    // Lógica de negocio
    // Validaciones
    // Persistencia
    // Eventos
  });
}

// 2. Añadir endpoint en src/routes/api/
export const POST: RequestHandler = async ({ request }) => {
  const data = await request.json();
  const result = await miNuevoUseCase(data);
  return json(result);
};

// 3. Añadir test unitario
test('miNuevoUseCase should...', async () => {
  // Arrange, Act, Assert
});
```

### **📡 Añadir Evento WebSocket**
```typescript
// 1. En use case, emitir evento
import { emitCustomEvent } from '$lib/server/ws/wsHub';

// En el use case
emitCustomEvent('mi:evento', payload);

// 2. En cliente, escuchar evento
socket.on('mi:evento', (data) => {
  // Actualizar UI
});
```

### **🎨 Nuevo Componente UI**
```svelte
<!-- src/lib/components/MiComponente.svelte -->
<script lang="ts">
  interface Props {
    data: MiData;
  }
  
  let { data }: Props = $props();
</script>

<div class="card">
  <!-- Skeleton UI components -->
</div>
```

### **🧪 Testing Guidelines**
```typescript
// Unit Test (Vitest)
import { describe, test, expect, beforeEach } from 'vitest';

describe('registrarPieza', () => {
  beforeEach(() => {
    // Setup test DB
  });
  
  test('should register piece successfully', async () => {
    // Test logic
  });
});

// E2E Test (Playwright)  
test('usuario puede crear lote', async ({ page }) => {
  await page.goto('/dashboard');
  await page.click('[data-testid="crear-lote"]');
  // ...
});
```

---

## 🎯 Próximos Pasos Inmediatos

### **🔥 Crítico (Esta Semana)**
1. **✅ Confirmar protocolo PLC** - ¿Modbus/TCP o TCP raw?
2. **📋 Implementar registrarPieza** - Use case central
3. **🌐 Crear endpoints /api/lotes** - CRUD básico
4. **🔒 Sistema de permisos** - hasPermission helper

### **📋 Siguiente (Semana 2)**
1. **📡 Upgrade WebSocket a Socket.IO** - Tiempo real
2. **⚙️ PLCAdapter completo** - Integración real
3. **🎨 Dashboard básico** - UI operativa

### **🔄 Flujo de Trabajo**
```mermaid
graph LR
    A[📝 Crear Issue] --> B[🌿 Feature Branch]
    B --> C[💻 Desarrollo]
    C --> D[🧪 Tests]
    D --> E[📋 PR Review]
    E --> F[🚀 Deploy]
```

---

## 📞 Contacto y Soporte

**Equipo de Desarrollo**: 
- 👨‍💻 **Lead Developer**: [Nombre]
- 🏭 **Industrial Engineer**: [Nombre] 
- 🎨 **Frontend Developer**: [Nombre]

**Documentación Adicional**:
- 📋 [API Documentation](./docs/api.md)
- 🔧 [Deployment Guide](./docs/deployment.md)
- 🏭 [PLC Integration Guide](./docs/plc-integration.md)

---

**🏁 ¡Listos para comenzar el desarrollo! El sistema está bien estructurado y solo faltan implementar los casos de uso principales para tener un MVP funcional.**