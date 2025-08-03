# 🏭 AXME Production System - Frontend

Una aplicación moderna de monitoreo de producción industrial construida con **SvelteKit** y **Skeleton UI**.

## 🚀 Características

- **🔐 Autenticación JWT**: Sistema de login seguro con roles de usuario
- **📊 Dashboard en Tiempo Real**: Monitoreo de datos de producción con WebSockets
- **📈 Historial de Producción**: Visualización y filtrado de datos históricos
- **👥 Panel de Administración**: Gestión de usuarios (solo para administradores)
- **🎨 Interfaz Moderna**: Diseño responsivo con Skeleton UI y Tailwind CSS
- **⚡ Tiempo Real**: Conexión WebSocket para actualizaciones en vivo

## 🛠️ Tecnologías

- **[SvelteKit](https://kit.svelte.dev/)**: Framework web moderno
- **[Skeleton UI](https://skeleton.dev/)**: Sistema de componentes UI
- **[Tailwind CSS](https://tailwindcss.com/)**: Framework de CSS utility-first
- **[TypeScript](https://www.typescriptlang.org/)**: Tipado estático
- **[Vite](https://vitejs.dev/)**: Herramienta de build rápida

## 📦 Instalación

### Prerrequisitos

- Node.js (v18 o superior)
- pnpm (recomendado) o npm

### Pasos de Instalación

1. **Instalar dependencias:**
   ```bash
   pnpm install
   ```

2. **Configurar variables de entorno:**
   
   Crear archivo `.env.local`:
   ```bash
   # URL del backend API
   API_BASE_URL=http://localhost:8000/api
   
   # URL del WebSocket
   WS_BASE_URL=ws://localhost:8000/ws
   ```

3. **Ejecutar en modo desarrollo:**
   ```bash
   pnpm dev
   ```

4. **Abrir en el navegador:**
   ```
   http://localhost:5173
   ```

## 🏗️ Estructura del Proyecto

```
src/
├── lib/
│   ├── components/          # Componentes reutilizables
│   │   ├── ConnectionStatus.svelte
│   │   └── MetricCard.svelte
│   ├── services/           # Servicios API y WebSocket
│   │   ├── api.ts         # Cliente API REST
│   │   └── websocket.ts   # Cliente WebSocket
│   └── stores/            # Gestión de estado Svelte
│       ├── auth.ts        # Estado de autenticación
│       └── production.ts  # Estado de producción
├── routes/                # Páginas de la aplicación
│   ├── +layout.svelte    # Layout principal
│   ├── +page.svelte      # Dashboard principal
│   ├── login/            # Página de login
│   ├── history/          # Historial de producción
│   └── admin/            # Panel de administración
├── app.css              # Estilos globales
└── app.html             # Template HTML base
```

## 🔐 Usuarios de Demostración

La aplicación incluye usuarios de demostración para pruebas:

| Usuario | Contraseña | Rol | Permisos |
|---------|------------|-----|----------|
| `admin` | `admin123` | Administrador | Acceso completo + gestión usuarios |
| `supervisor` | `sup123` | Supervisor | Dashboard + historial + gestión |
| `operator` | `op123` | Operador | Dashboard + historial |
| `viewer` | `view123` | Visualizador | Solo dashboard (lectura) |

## 📱 Páginas y Funcionalidades

### 🏠 Dashboard Principal (`/`)
- **Métricas en tiempo real**: Total productos, tasa de calidad, tiempo de ciclo promedio
- **Estado actual de producción**: ID producto, estado línea, calidad, parámetros del proceso
- **Estado de conexión**: Indicador visual de conexión WebSocket
- **Actualización automática**: Datos refreshed cada 30 segundos

### 📈 Historial de Producción (`/history`)
- **Filtros avanzados**: Por fecha, estado de calidad, estado de línea
- **Tabla paginada**: Historial completo de productos procesados
- **Exportación CSV**: Descarga de datos para análisis externo
- **Búsqueda en tiempo real**: Filtrado instantáneo de resultados

### 👥 Panel de Administración (`/admin`)
- **Gestión de usuarios**: Crear, listar usuarios del sistema
- **Control de roles**: Asignación de permisos por usuario
- **Estados de cuenta**: Visualización de usuarios activos/inactivos
- **Acceso restringido**: Solo disponible para administradores

### 🔐 Login (`/login`)
- **Autenticación JWT**: Login seguro con tokens
- **Validación en tiempo real**: Feedback inmediato de errores
- **Persistencia de sesión**: Auto-login en visitas subsecuentes
- **Credenciales demo**: Usuarios de prueba pre-configurados

## 🌐 Integración con Backend

### API REST
- **Base URL**: `http://localhost:8000/api`
- **Autenticación**: Bearer token JWT
- **Endpoints principales**:
  - `POST /auth/login` - Autenticación
  - `GET /auth/me` - Información usuario actual
  - `GET /production/current` - Datos actuales de producción
  - `GET /production/history` - Historial de producción
  - `GET /production/stats` - Estadísticas agregadas
  - `GET /admin/users` - Lista de usuarios (admin)
  - `POST /admin/users` - Crear usuario (admin)

### WebSocket en Tiempo Real
- **URL**: `ws://localhost:8000/ws/production`
- **Mensajes recibidos**:
  - `connection` - Confirmación de conexión
  - `production_data` - Datos nuevos de producción
  - `current_data` - Estado actual del sistema
  - `pong` - Respuesta a ping
- **Mensajes enviados**:
  - `ping` - Heartbeat cada 30 segundos

## 🎨 Personalización de Tema

El proyecto usa **Skeleton UI** con el tema "Cerberus". Para personalizar:

1. **Modificar tema en `app.html`:**
   ```html
   <html lang="en" data-theme="cerberus">
   ```

2. **Temas disponibles**: `cerberus`, `rose`, `blue`, `green`, `orange`, `red`

3. **CSS personalizado en `app.css`:**
   ```css
   /* Personalizaciones adicionales */
   :root {
     --color-primary-500: #your-color;
   }
   ```

## 🔧 Scripts Disponibles

```bash
# Desarrollo
pnpm dev              # Servidor de desarrollo
pnpm dev --host       # Exponer en red local

# Build
pnpm build            # Build para producción
pnpm preview          # Preview del build

# Calidad de código
pnpm lint             # Verificar código
pnpm format           # Formatear código
pnpm check            # Verificar tipos TypeScript

# Testing
pnpm test             # Ejecutar tests unitarios
pnpm test:e2e         # Tests end-to-end
```

## 🚀 Despliegue en Producción

### Build para Producción
```bash
pnpm build
```

### Variables de Entorno de Producción
```bash
API_BASE_URL=https://your-api-domain.com/api
WS_BASE_URL=wss://your-api-domain.com/ws
```

### Servidor Node.js
```bash
# Después del build
node build
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install
COPY . .
RUN pnpm build
EXPOSE 3000
CMD ["node", "build"]
```

## 📚 Desarrollo

### Agregar Nueva Página
1. Crear archivo en `src/routes/nueva-pagina/+page.svelte`
2. Agregar navegación en `src/routes/+layout.svelte`
3. Implementar lógica y UI

### Crear Nuevo Componente
1. Crear archivo en `src/lib/components/MiComponente.svelte`
2. Exportar desde `src/lib/index.ts` (opcional)
3. Importar donde se necesite

### Agregar Nueva Store
1. Crear archivo en `src/lib/stores/miStore.ts`
2. Implementar con patrón Svelte stores
3. Usar en componentes con `$miStore`

## 🐛 Troubleshooting

### Problemas Comunes

1. **Error de conexión WebSocket:**
   - Verificar que el backend esté ejecutándose
   - Comprobar URL del WebSocket en configuración

2. **Error de autenticación:**
   - Verificar credenciales de usuario demo
   - Limpiar localStorage: `localStorage.clear()`

3. **Error de dependencias:**
   - Reinstalar: `rm -rf node_modules && pnpm install`

4. **Error de build:**
   - Verificar tipos TypeScript: `pnpm check`
   - Revisar imports y exports

### Debug Mode
```bash
# Habilitar logs detallados
DEBUG=1 pnpm dev
```

## 📞 Soporte

Para soporte técnico o preguntas:
- **Documentación**: Ver archivos en `/docs`
- **Issues**: Crear issue en el repositorio
- **API Reference**: Consultar documentación del backend

---

**Construido con ❤️ para AXME Production System**