# 📄 Proyecto: Sistema de Tests en Tiempo Real (SvelteKit)

> **Tipo de sistema:** Monolito LAN con tiempo real y control de PLC  
> **Stack:** SvelteKit 2 + Skeleton UI, Node.js, PostgreSQL + Prisma, Lucia Auth, socket.io, basic-ftp

---

## 🚀 Resumen ejecutivo

Sistema que:
- Recibe resultados de pruebas desde un **PLC**.
- Procesa cada pieza como parte de un **lote**.
- Almacena resultados e imágenes (FTP).
- Notifica al frontend en **tiempo real** vía WebSockets.
- Controla el PLC (detener cuando el lote alcanzó la meta).

**Objetivo:** MVP funcional y robusto con trazabilidad completa, roles y permisos, UI operativa y lógica de lotes confiable.

---

## ⚙️ Arquitectura

**Componentes principales:**
- `PLCAdapter` (TCP / Modbus/TCP / Mock)
- `UseCases` (registrarPieza, cerrarLote, etc.)
- `Prisma` (PostgreSQL)
- `WSHub` (socket.io)
- `FTPAdapter` (basic-ftp)
- `Frontend` (SvelteKit + Skeleton UI)
- `hooks.server.ts` para auth y permisos

---

## 🗄️ Modelo de datos

**Entidades principales:**
- **Usuario** con roles y permisos.
- **Rol** y **Permiso** (customizables).
- **Lote** con estado, contadores y piezas.
- **Pieza** con bits de resultado e imágenes.
- **Historial** de acciones.
- **EventoExterno** para idempotencia y auditoría.

> Prisma schema completo en `prisma/schema.prisma`.

---

## 🔌 API y Eventos

### REST Endpoints (`src/routes/api/...`)
- `POST /api/auth/login|logout`
- `GET /api/lotes` y `POST /api/lotes`
- `GET /api/lotes/:id` y `/api/lotes/:id/close`
- `GET /api/piezas/:id/image`
- `GET /api/historial`

### WebSocket
- Emitidos: `pieza:procesada`, `lote:actualizado`, `lote:cerrado`, `system:alert`
- Recibidos: `lote:pause`, `lote:resume`, `request:loteDetalle`
- **Handshake** con cookie de sesión o token y validación de permisos.

---

## 🛠️ Casos de uso clave

### `registrarPieza(loteId, resultadoBits, meta)`
- Guarda pieza.
- Actualiza contadores en lote.
- Guarda en historial.
- Emite evento WS.
- Cierra lote si alcanza meta.

### `cerrarLote(loteId)`
- Cambia estado y `closedAt`.
- Emite evento WS y envía señal `stop` al PLC.

---

## 🔒 Seguridad
- Cookies httpOnly + SameSite.
- Validación de permisos en endpoints y eventos WS.
- Idempotencia con `externalId`.
- Protección de acceso FTP.

---

## 🧪 Testing
- Unit (Vitest).
- Integration (Prisma + Postgres docker o SQLite memoria).
- E2E (Playwright).
- Performance (simulación ráfaga PLC).

---

## 📝 Runbook rápido

**Instalación:**
```bash
pnpm install
npx prisma generate
npx prisma migrate dev --name init
node prisma/seed.js
pnpm run dev
```
