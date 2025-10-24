# 🏭 Sistema de Trazabilidad y Control de Calidad Industrial

Sistema integral de monitoreo y control de calidad para líneas de producción con integración PLC, desarrollado con SvelteKit 5 y diseñado para uso en dispositivos táctiles industriales.

## 📋 Tabla de Contenidos

- [Descripción General](#-descripción-general)
- [Contrato de Comunicación PLC](#-contrato-de-comunicación-plc)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Base de Datos](#-base-de-datos)
- [Sistema de Permisos](#-sistema-de-permisos)
- [Módulos del Sistema](#-módulos-del-sistema)
- [API y WebSockets](#-api-y-websockets)
- [Despliegue](#-despliegue)

---

## 🎯 Descripción General

Sistema de trazabilidad y control de calidad diseñado para monitorear en tiempo real la producción de cables industriales. El sistema recibe datos desde un PLC mediante comunicación TCP, procesa información de cada pieza producida, captura imágenes de defectos y mantiene un registro completo de la producción.

### Características Principales

✅ **Monitoreo en Tiempo Real**
- Comunicación bidireccional con PLC vía TCP Socket
- Actualización instantánea de métricas de producción
- WebSocket para actualizaciones en vivo en el frontend

✅ **Control de Calidad**
- Detección automática de defectos
- Captura y almacenamiento de imágenes de fallos
- Clasificación de tipos de falla
- Trazabilidad completa de cada pieza

✅ **Sistema de Gestión**
- Control de lotes de producción
- Gestión de recetas (modelos de cables)
- Administración de usuarios y roles
- Exportación de datos a CSV

✅ **Interfaz Táctil Optimizada**
- Diseño responsive para dispositivos táctiles
- Botones grandes (≥48px) según estándares WCAG
- Modales informativos en lugar de alertas nativas
- Iconografía profesional con Lucide Svelte

✅ **Seguridad y Permisos**
- Sistema RBAC (Role-Based Access Control) granular
- Autenticación con Lucia Auth
- 71 permisos específicos por módulo
- 4 roles predefinidos (Admin, Manager, Operador, Viewer)

---

## 🔌 Contrato de Comunicación PLC

### Protocolo de Comunicación

**Tipo:** TCP Socket  
**Puerto:** 3000 (configurable)  
**Formato:** Array de 8 enteros (0-9)  
**Dirección:** Unidireccional (PLC → Backend)

### Estructura del Array de Bits

El PLC envía un array de 8 enteros por cada pieza producida:

```javascript
[índice_0, índice_1, índice_2, índice_3, índice_4, índice_5, índice_6, índice_7]
```

### Tabla de Contrato de Bits

| Índice | Campo | Descripción | Valores Posibles | Notas |
|--------|-------|-------------|------------------|-------|
| **0** | `general_status` | Estado global del sistema | `0` = Detenido<br>`1` = Activo<br>`2` = Error<br>`3` = Mantenimiento | Indica el estado general de la línea |
| **1** | `piece_status` | Estado de la pieza | `0` = NOK (Falla)<br>`1` = OK (Aprobada) | Resultado final de la prueba |
| **2** | `failure_code` | Código de falla | `0` = Sin falla<br>`1` = Test hipot falla<br>`2` = Etiqueta incorrecta<br>`3` = Modelo incorrecto<br>`4` = Terminal incorrecta<br>`5-9` = Reservado | Solo válido si `piece_status = 0` |
| **3** | `model_id` | ID de receta/modelo | `1-9` | Referencia a la receta activa en BD |
| **4** | `camera_status` | Estado inspección visual | `0` = OK<br>`1` = Defecto visual detectado | Indica si se capturó imagen |
| **5** | `electrical_status` | Estado prueba eléctrica | `0` = OK<br>`1` = Falla eléctrica | Resultado de test hipot |
| **6** | `ready_flag` | Bandera de datos válidos | `0` = Datos incompletos<br>`1` = Paquete válido | Solo procesar si `ready_flag = 1` |
| **7** | `reserved` | Campo reservado | `0-9` | Para futuras expansiones |

### Códigos de Falla Detallados

#### 0 - Sin Falla
✅ **Descripción:** La pieza pasó todas las pruebas correctamente.  
**Acción:** Incrementar contador de piezas OK.  
**Imagen:** No se captura.

#### 1 - Test Hipot Falla
⚠️ **Descripción:** Falla en la prueba de aislamiento eléctrico (test hipot).  
**Causa Común:** 
- Aislamiento insuficiente
- Cortocircuito entre conductores
- Daño en el recubrimiento
**Acción:** Capturar imagen del terminal, pausar producción.  
**Imagen:** Terminal eléctrico con identificación de falla.

#### 2 - Etiqueta Incorrecta
⚠️ **Descripción:** La etiqueta no coincide con el modelo esperado.  
**Causa Común:**
- Etiqueta mal colocada
- Código QR/barcode incorrecto
- Falta de etiqueta
**Acción:** Capturar imagen de la etiqueta, pausar producción.  
**Imagen:** Vista de la etiqueta y código.

#### 3 - Modelo Incorrecto
⚠️ **Descripción:** El `model_id` no corresponde a ninguna receta activa en la base de datos.  
**Causa Común:**
- PLC configurado con modelo no registrado
- Receta no creada en el sistema
- Error de sincronización
**Acción:** Marcar como error crítico, notificar a supervisor.  
**Imagen:** Foto general del ensamble.

#### 4 - Terminal Incorrecta
⚠️ **Descripción:** El tipo de terminal no coincide con la especificación de la receta.  
**Causa Común:**
- Terminal mal instalado
- Tipo de ferrul incorrecto
- Orientación incorrecta
**Acción:** Capturar imagen del terminal, pausar producción.  
**Imagen:** Close-up del terminal defectuoso.

#### 5-9 - Reservado
🔒 **Descripción:** Códigos reservados para futuras implementaciones.  
**Acción:** Registrar como "Falla desconocida", notificar a desarrollo.

### Ejemplos de Paquetes

#### Ejemplo 1: Pieza Correcta
```javascript
[1, 1, 0, 3, 0, 0, 1, 0]
```
**Interpretación:**
- Sistema activo (`general_status = 1`)
- Pieza OK (`piece_status = 1`)
- Sin falla (`failure_code = 0`)
- Modelo/Receta ID 3 (`model_id = 3`)
- Inspección visual OK (`camera_status = 0`)
- Prueba eléctrica OK (`electrical_status = 0`)
- Datos válidos (`ready_flag = 1`)
- Campo reservado (`reserved = 0`)

**Resultado:** ✅ Pieza aprobada, continuar producción.

---

#### Ejemplo 2: Falla en Test Hipot
```javascript
[1, 0, 1, 3, 0, 1, 1, 0]
```
**Interpretación:**
- Sistema activo (`general_status = 1`)
- Pieza NOK (`piece_status = 0`)
- Falla hipot (`failure_code = 1`)
- Modelo/Receta ID 3 (`model_id = 3`)
- Inspección visual OK (`camera_status = 0`)
- Prueba eléctrica falló (`electrical_status = 1`)
- Datos válidos (`ready_flag = 1`)

**Resultado:** ❌ Pieza rechazada, se esperará imagen del defecto, producción pausada.

---

#### Ejemplo 3: Etiqueta Incorrecta con Imagen
```javascript
[1, 0, 2, 5, 1, 0, 1, 0]
```
**Interpretación:**
- Sistema activo (`general_status = 1`)
- Pieza NOK (`piece_status = 0`)
- Etiqueta incorrecta (`failure_code = 2`)
- Modelo/Receta ID 5 (`model_id = 5`)
- Defecto visual detectado (`camera_status = 1`)
- Prueba eléctrica OK (`electrical_status = 0`)
- Datos válidos (`ready_flag = 1`)

**Resultado:** ❌ Pieza rechazada, sistema esperará imagen de la etiqueta, producción pausada automáticamente.

---

#### Ejemplo 4: Datos No Válidos (Ignorar)
```javascript
[1, 0, 2, 3, 1, 0, 0, 0]
```
**Interpretación:**
- `ready_flag = 0` → Datos incompletos o en proceso

**Resultado:** ⏭️ Paquete descartado, no se procesa ni se registra.

---

### Flujo de Procesamiento

```mermaid
graph TD
    A[PLC envía array de 8 bits] --> B{ready_flag = 1?}
    B -->|No| C[Descartar paquete]
    B -->|Sí| D[Validar estructura]
    D --> E{piece_status?}
    E -->|1 OK| F[Registrar pieza OK]
    E -->|0 NOK| G{failure_code > 0?}
    G -->|Sí| H[Registrar falla]
    H --> I{camera_status = 1?}
    I -->|Sí| J[Esperar imagen]
    I -->|No| K[Continuar producción]
    J --> L[Procesar imagen]
    L --> M[Pausar producción automáticamente]
    M --> N[Mostrar modal de error]
    F --> K
    N --> O[Usuario revisa]
    O --> P[Reiniciar manualmente]
```

### Configuración del PLC

Para integrar correctamente el PLC con el sistema:

1. **IP del Backend:** Configurar en PLC (por defecto: `localhost`)
2. **Puerto TCP:** `3000` (configurable en `TCP_PORT` env)
3. **Timeout:** Recomendado 5000ms
4. **Retry:** 3 intentos antes de marcar como error
5. **Frecuencia:** Enviar solo cuando `ready_flag = 1`

### Manejo de Imágenes

Cuando `failure_code > 0`:

1. **PLC dispara captura** de imagen del defecto
2. **Backend recibe imagen** vía FTP o filesystem watch
3. **Renombrado automático:** `{model_id}_{failureCode}_{timestamp}.jpg`
4. **Ubicación:** `/static/images/lotes/{nombre_lote}/`
5. **Base de datos:** Se vincula a la pieza y lote correspondiente
6. **Notificación:** WebSocket emite evento `image-processed`
7. **UI:** Modal muestra imagen y detalles del error
8. **Producción:** Se pausa automáticamente

---

## 🚀 Tecnologías Utilizadas

### Frontend
- **SvelteKit 5** - Framework full-stack
- **Svelte 5** - UI reactivo con runes (`$state`, `$derived`, `$effect`)
- **Tailwind CSS 4** - Estilos utility-first
- **Skeleton UI** - Componentes y sistema de diseño
- **Lucide Svelte** - Iconografía profesional
- **date-fns** - Formateo de fechas

### Backend
- **Node.js** - Runtime
- **SvelteKit API Routes** - Endpoints REST
- **WebSocket (ws)** - Comunicación en tiempo real
- **TCP Socket (net)** - Comunicación con PLC
- **Chokidar** - File watcher para imágenes

### Base de Datos
- **PostgreSQL** / **SQLite** - Base de datos relacional
- **Prisma ORM** - Gestor de base de datos
- **Lucia Auth** - Sistema de autenticación

### Herramientas de Desarrollo
- **TypeScript** - Tipado estático
- **Prettier** - Formateo de código
- **ESLint** - Linting
- **Vite** - Build tool

---

## 🏗️ Arquitectura del Sistema

### Capas del Sistema

```
┌─────────────────────────────────────────────┐
│         Frontend (SvelteKit UI)              │
│  - Dashboard de Producción                   │
│  - Gestión de Lotes y Recetas                │
│  - Historial y Reportes                      │
└─────────────┬───────────────────────────────┘
              │ HTTP/WebSocket
┌─────────────▼───────────────────────────────┐
│      Backend (SvelteKit API Routes)          │
│  - Endpoints REST                            │
│  - WebSocket Server (puerto 4000)            │
│  - Sistema de Permisos                       │
└─────────────┬───────────────────────────────┘
              │
      ┌───────┴────────┐
      │                │
┌─────▼─────┐   ┌──────▼──────┐
│ TCP Server │   │ File Watcher│
│ (puerto    │   │ (Chokidar)  │
│  3000)     │   │             │
└─────┬──────┘   └──────┬──────┘
      │                 │
┌─────▼─────────────────▼──────┐
│          PLC Industrial       │
│  - Envía datos de piezas      │
│  - Dispara captura de imágenes│
└───────────────────────────────┘
```

### Flujo de Datos en Tiempo Real

```
PLC → TCP (puerto 3000) → Parser → Handler → WebSocket (puerto 4000) → UI
                                       ↓
                                   Database
                                       ↓
                                 Image Watcher → Process → Storage
```

---

## 📁 Estructura del Proyecto

```
plc-app/
├── prisma/
│   ├── schema.prisma        # Esquema de base de datos
│   └── seed.js              # Datos iniciales (usuarios, roles, permisos, recetas)
│
├── src/
│   ├── lib/
│   │   ├── components/
│   │   │   └── sidebar/     # Navegación lateral
│   │   ├── server/
│   │   │   ├── auth/        # Sistema de autenticación y guards
│   │   │   ├── plc/
│   │   │   │   ├── plc-parser.ts       # Parseo de datos PLC
│   │   │   │   ├── plc-handler.ts      # Lógica de negocio PLC
│   │   │   │   └── image-handler.ts    # Procesamiento de imágenes
│   │   │   ├── tcp/
│   │   │   │   └── tcp.server.ts       # Servidor TCP
│   │   │   ├── ws/
│   │   │   │   └── ws.server.ts        # Servidor WebSocket
│   │   │   └── startup.ts              # Inicialización de servicios
│   │   └── prisma.ts        # Cliente de Prisma
│   │
│   ├── routes/
│   │   ├── (auth)/
│   │   │   ├── login/       # Página de login
│   │   │   └── signup/      # Página de registro
│   │   ├── dashboard/
│   │   │   ├── production/  # Módulo de Producción
│   │   │   ├── history/     # Módulo de Historial
│   │   │   │   └── [id]/    # Detalles de lote
│   │   │   ├── management/  # Módulo de Gestión
│   │   │   │   ├── recetas/
│   │   │   │   ├── lotes/
│   │   │   │   ├── usuarios/
│   │   │   │   └── roles/
│   │   │   └── +layout.svelte
│   │   └── api/
│   │       ├── plc/
│   │       │   ├── +server.ts    # GET status
│   │       │   ├── start/        # POST iniciar lote
│   │       │   └── stop/         # DELETE detener producción
│   │       └── images/
│   │           └── [loteId]/     # GET imágenes de lote
│   │
│   ├── hooks.server.ts      # Hooks de SvelteKit (auth, permisos, servicios)
│   └── app.d.ts             # Tipos de TypeScript
│
├── static/
│   └── images/
│       └── lotes/           # Imágenes organizadas por lote
│
├── .env                     # Variables de entorno
├── package.json
├── tailwind.config.ts
├── vite.config.ts
└── tsconfig.json
```

---

## 💿 Instalación

### Requisitos Previos

- **Node.js** 18+ 
- **pnpm** (recomendado) o npm
- **PostgreSQL** 14+ o SQLite
- **Git**

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd plc-app
```

2. **Instalar dependencias**
```bash
pnpm install
```

3. **Configurar variables de entorno**
```bash
cp .env.example .env
```

Editar `.env` con tus configuraciones:
```env
# Database
DATABASE_URL="postgresql://user:password@localhost:5432/plc_db"

# TCP Server (PLC Communication)
TCP_PORT=3000

# WebSocket Server (Real-time Updates)
WS_PORT=4000

# Image Directories
PLC_IMAGE_DIR="/path/to/ftp/plc_images"
IMAGES_DIR="/path/to/static/images/lotes"

# Application
PUBLIC_APP_NAME="Control de Calidad Industrial"
```

4. **Configurar base de datos**
```bash
# Generar cliente de Prisma
pnpm prisma generate

# Ejecutar migraciones
pnpm prisma db push

# Seed de datos iniciales
pnpm db:seed
```

5. **Iniciar en desarrollo**
```bash
pnpm dev
```

La aplicación estará disponible en `http://localhost:5173`

### Usuarios por Defecto (después del seed)

| Usuario | Contraseña | Rol | Permisos |
|---------|-----------|-----|----------|
| admin | admin123 | Admin | Todos (*) |
| manager | manager123 | Manager | Gestión y visualización |
| operador | operador123 | Operador | Producción y lectura |
| viewer | viewer123 | Viewer | Solo lectura |

⚠️ **Importante:** Cambiar estas contraseñas en producción.

---

## ⚙️ Configuración

### Configuración del PLC

1. **Dirección IP del Backend:** Configurar en el PLC
2. **Puerto TCP:** `3000` (o el configurado en `TCP_PORT`)
3. **Formato de datos:** Array de 8 enteros separados por comas
4. **Timeout:** 5000ms recomendado

### Configuración de Imágenes (FTP/Filesystem)

El sistema soporta dos métodos para recibir imágenes:

#### Opción 1: FTP Server
```env
PLC_IMAGE_DIR="/home/ftp/plc_images"
```
El PLC sube imágenes vía FTP a este directorio.

#### Opción 2: Shared Filesystem
```env
PLC_IMAGE_DIR="/mnt/shared/plc_images"
```
El PLC y el backend comparten un filesystem.

El sistema automáticamente:
1. Detecta nuevas imágenes (chokidar)
2. Renombra: `{model_id}_{failureCode}_{timestamp}.jpg`
3. Mueve a: `/static/images/lotes/{lote_name}/`
4. Actualiza base de datos
5. Emite evento WebSocket

---

## 🗄️ Base de Datos

### Modelos Principales

#### **User**
```prisma
model User {
  id            String    @id @default(uuid())
  username      String    @unique
  password_hash String
  role_id       String
  created_at    DateTime  @default(now())
}
```

#### **Receta** (Modelo de Cable)
```prisma
model Receta {
  id                    String  @id @default(uuid())
  ppn                   String  @unique
  item_description      String
  cantidad_conductores  Int
  L1                    String  # Tipo de terminal L1
  L2                    String  # Tipo de terminal L2
  L3                    String?
  N                     String?
  T                     String?
}
```

#### **Lote** (Lote de Producción)
```prisma
model Lote {
  id            String     @id @default(uuid())
  name          String     @unique
  receta_id     String
  max_piezas_ok Int
  piezas_ok     Int        @default(0)
  piezas_fallas Int        @default(0)
  estado        EstadoLote @default(OPEN)
  started_at    DateTime   @default(now())
  closed_at     DateTime?
  created_by    String
  
  receta    Receta      @relation(fields: [receta_id], references: [id])
  piezas    Pieza[]
  imagenes  Imagen[]
}

enum EstadoLote {
  OPEN
  CLOSED
  PAUSED
}
```

#### **Pieza** (Pieza Individual)
```prisma
model Pieza {
  id              String   @id @default(uuid())
  lote_id         String
  indice          Int
  ok              Boolean
  resultado_bits  Int[]
  imagen_path     String
  processed_at    DateTime @default(now())
  
  lote Lote @relation(fields: [lote_id], references: [id])
}
```

#### **Imagen** (Imagen de Defecto)
```prisma
model Imagen {
  id             String   @id @default(uuid())
  lote_id        String
  pieza_id       String?
  path           String
  tipo_falla     String
  metadata       Json?
  thumbnail_path String   @default("")
  uploaded_at    DateTime @default(now())
  
  lote  Lote   @relation(fields: [lote_id], references: [id])
  pieza Pieza? @relation(fields: [pieza_id], references: [id])
}
```

### Migraciones

```bash
# Crear nueva migración
pnpm prisma migrate dev --name nombre_migracion

# Aplicar migraciones
pnpm prisma migrate deploy

# Resetear base de datos (⚠️ CUIDADO: Borra todos los datos)
pnpm prisma migrate reset

# Ver estado de migraciones
pnpm prisma migrate status
```

---

## 🔐 Sistema de Permisos

### Estructura de Permisos

El sistema utiliza RBAC (Role-Based Access Control) con 71 permisos granulares organizados en 3 módulos:

#### **Módulo Production** (22 permisos)
```
production.*
├── production.ver
├── production.dashboard.ver
├── production.metrics.ver
├── production.control.*
│   ├── production.control.start
│   ├── production.control.stop
│   └── production.control.pause
└── production.images.*
    ├── production.images.ver
    └── production.images.descargar
```

#### **Módulo History** (24 permisos)
```
history.*
├── history.ver
├── history.lotes.*
│   ├── history.lotes.ver
│   ├── history.lotes.detalles
│   └── history.lotes.exportar
└── history.reportes.*
    ├── history.reportes.generar
    └── history.reportes.exportar
```

#### **Módulo Management** (25 permisos)
```
management.*
├── management.ver
├── management.recetas.*
│   ├── management.recetas.ver
│   ├── management.recetas.crear
│   ├── management.recetas.editar
│   └── management.recetas.eliminar
├── management.lotes.*
│   ├── management.lotes.ver
│   ├── management.lotes.crear
│   ├── management.lotes.editar
│   └── management.lotes.cerrar
├── management.usuarios.*
│   ├── management.usuarios.ver
│   ├── management.usuarios.crear
│   ├── management.usuarios.editar
│   └── management.usuarios.eliminar
└── management.roles.*
    ├── management.roles.ver
    ├── management.roles.crear
    ├── management.roles.editar
    └── management.roles.eliminar
```

### Roles Predefinidos

| Rol | Permisos | Descripción |
|-----|----------|-------------|
| **Admin** | `*` (todos) | Acceso total al sistema |
| **Manager** | Gestión completa | Puede gestionar recetas, lotes, usuarios y ver todo |
| **Operador** | Producción + Lectura | Puede operar la línea y ver información |
| **Viewer** | Solo lectura | Puede ver pero no modificar |

### Uso en el Código

#### Server-side (guards)
```typescript
import { requirePermission } from '$lib/server/auth/guards';

export const load: PageServerLoad = async (event) => {
  requirePermission(event, 'production.control.start');
  // ...
};
```

#### Client-side (UI condicional)
```svelte
<script>
  const canControl = $derived(
    user?.permisos.includes('*') ||
    user?.permisos.includes('production.control.start')
  );
</script>

{#if canControl}
  <button onclick={startProduction}>Iniciar Producción</button>
{/if}
```

---

## 📦 Módulos del Sistema

### 1. Producción (`/dashboard/production`)

**Funcionalidades:**
- Visualización en tiempo real del estado de la línea
- Selección e inicio de lotes de producción
- Métricas en vivo (OK, NOK, eficiencia, precisión)
- Tabla de piezas recientes
- Visualización de datos crudos del PLC
- Auto-pausa en caso de error
- Modal de error con imagen del defecto

**Permisos Requeridos:**
- Ver: `production.ver`
- Iniciar: `production.control.start`
- Detener: `production.control.stop`

### 2. Historial (`/dashboard/history`)

**Funcionalidades:**
- Lista de lotes completados/pausados
- Filtros por estado y búsqueda
- Estadísticas por lote (OK, NOK, precisión)
- Exportación masiva a CSV
- Vista detallada de lote:
  - Información completa
  - Galería de imágenes de defectos
  - Tabla de todas las piezas
  - Gráficos de fallas por tipo
  - Exportación individual a CSV

**Permisos Requeridos:**
- Ver lista: `history.ver`
- Ver detalles: `history.lotes.detalles`
- Exportar: `history.lotes.exportar`

### 3. Gestión (`/dashboard/management`)

#### 3.1 Recetas
- CRUD completo de recetas/modelos
- Especificación de conductores y terminales
- Asignación de PPN (Part Number)

**Permisos:** `management.recetas.*`

#### 3.2 Lotes
- Creación de lotes de producción
- Asignación de receta y objetivo
- Cierre manual de lotes
- Edición de parámetros

**Permisos:** `management.lotes.*`

#### 3.3 Usuarios
- Gestión de usuarios del sistema
- Asignación de roles
- Cambio de contraseñas
- Activación/desactivación

**Permisos:** `management.usuarios.*`

#### 3.4 Roles y Permisos
- Creación de roles personalizados
- Asignación granular de permisos
- Gestión de permisos por módulo

**Permisos:** `management.roles.*`

---

## 🌐 API y WebSockets

### REST API Endpoints

#### PLC Status
```http
GET /api/plc
Response: {
  status: 'active' | 'idle' | 'error',
  lote: { ... } | null,
  availableLotes: [...]
}
```

#### Iniciar Lote
```http
POST /api/plc/start
Body: { loteId: string }
Response: { success: true, lote: { ... } }
```

#### Detener Producción
```http
DELETE /api/plc/stop
Response: { success: true }
```

#### Obtener Imágenes de Lote
```http
GET /api/images/{loteId}?failureCode=1
Response: [{ path, tipo_falla, uploaded_at, metadata }]
```

### WebSocket Events (Puerto 4000)

#### Eventos del Servidor → Cliente

**plc-data**
```json
{
  "type": "plc-data",
  "payload": {
    "rawData": [1, 1, 0, 3, 0, 0, 1, 0],
    "pieceStatus": "OK",
    "failureType": "Sin falla",
    "lineStatus": "RUNNING"
  }
}
```

**piece-created**
```json
{
  "type": "piece-created",
  "payload": {
    "loteId": "uuid",
    "piezaId": "uuid",
    "index": 15,
    "ok": true,
    "failureCode": 0
  }
}
```

**awaiting-image**
```json
{
  "type": "awaiting-image",
  "payload": {
    "loteId": "uuid",
    "piezaId": "uuid",
    "piezaIndex": 15,
    "failureCode": 2
  }
}
```

**image-processed**
```json
{
  "type": "image-processed",
  "payload": {
    "loteId": "uuid",
    "loteName": "LOTE-001",
    "piezaIndex": 15,
    "failureCode": 2,
    "imagePath": "/images/lotes/LOTE-001/3_2_1234567890.jpg"
  }
}
```

**lot-started / lot-stopped / lot-completed**
```json
{
  "type": "lot-started",
  "payload": {
    "id": "uuid",
    "name": "LOTE-001",
    "recetaId": "uuid"
  }
}
```

---

## 🚀 Despliegue

### Build de Producción

```bash
# Generar build optimizado
pnpm build

# Preview del build
pnpm preview
```

### Despliegue con Docker

```dockerfile
# Dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile
COPY . .
RUN pnpm prisma generate
RUN pnpm build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/build ./build
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
EXPOSE 3000 4000
CMD ["node", "build"]
```

```bash
# Build imagen
docker build -t plc-app .

# Ejecutar contenedor
docker run -p 3000:3000 -p 4000:4000 \
  -e DATABASE_URL="postgresql://..." \
  -e TCP_PORT=3000 \
  -e WS_PORT=4000 \
  plc-app
```

### Variables de Entorno de Producción

```env
NODE_ENV=production
DATABASE_URL=postgresql://user:pass@host:5432/db
TCP_PORT=3000
WS_PORT=4000
PLC_IMAGE_DIR=/app/ftp/plc_images
IMAGES_DIR=/app/static/images/lotes
PUBLIC_APP_NAME="Sistema de Calidad"
```

### Consideraciones de Producción

1. **Base de Datos:**
   - Usar PostgreSQL en producción (no SQLite)
   - Configurar backups automáticos
   - Índices en tablas grandes

2. **Seguridad:**
   - Cambiar contraseñas por defecto
   - Usar HTTPS (certificado SSL)
   - Configurar firewall para puertos 3000 y 4000
   - Variables de entorno seguras

3. **Performance:**
   - Configurar PM2 o similar para auto-restart
   - Límite de conexiones WebSocket
   - Compresión de imágenes
   - CDN para assets estáticos

4. **Monitoreo:**
   - Logs estructurados
   - Alertas de errores
   - Métricas de uptime
   - Dashboard de sistema

---

## 📄 Licencia

Proyecto propietario - Todos los derechos reservados © 2025

---

## 👥 Soporte

Para soporte técnico o consultas:
- **Email:** soporte@empresa.com
- **Documentación:** Ver archivos en `/docs`
- **Issues:** Reportar en el sistema de gestión interno

---

**Versión:** 1.0.0  
**Última actualización:** Enero 2025  
**Desarrollado con:** ❤️ y ☕

