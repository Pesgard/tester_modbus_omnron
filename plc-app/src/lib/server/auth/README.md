# Sistema de Role Guards y Permisos

Este sistema permite proteger rutas y recursos basándose en roles y permisos de usuario.

## Estructura

### 1. Hooks (`hooks.server.ts`)
Carga automáticamente los roles y permisos del usuario en cada request y los almacena en `event.locals.userWithPerms`.

### 2. Guards (`guards.ts`)
Funciones utilitarias para proteger rutas del servidor:

- **`requireAuth(event)`**: Verifica que el usuario esté autenticado
- **`requirePermission(event, permission)`**: Verifica un permiso específico
- **`requireAnyPermission(event, permissions[])`**: Verifica al menos uno de los permisos
- **`requireAllPermissions(event, permissions[])`**: Verifica todos los permisos
- **`checkPermission(event, permission)`**: Verifica permiso sin lanzar error (retorna boolean)

### 3. Permissions (`permissions.ts`)
Funciones para verificar permisos:

- **`hasPermission(userId, key)`**: Verifica permiso consultando DB (async)
- **`hasPermissionSync(user, key)`**: Verifica permiso en memoria (sync)

## Uso en Rutas del Servidor

### Ejemplo 1: Proteger todas las subrutas con Layout (RECOMENDADO)

```typescript
// src/routes/dashboard/+layout.server.ts
import type { LayoutServerLoad } from './$types';
import { requireAuth } from '$lib/server/auth/guards';

export const load: LayoutServerLoad = (event) => {
    // Protege /dashboard y todas sus subrutas automáticamente
    requireAuth(event);
    
    return {
        user: event.locals.userWithPerms
    };
};
```

**Beneficio:** Todas las páginas dentro de `/dashboard/*` quedan protegidas sin necesidad de repetir `requireAuth()` en cada una.

### Ejemplo 1b: Proteger ruta individual

```typescript
// src/routes/dashboard/+page.server.ts
import type { PageServerLoad } from './$types';
import { requireAuth } from '$lib/server/auth/guards';

export const load: PageServerLoad = (event) => {
    requireAuth(event);
    
    return {
        user: event.locals.userWithPerms
    };
};
```

### Ejemplo 2: Proteger ruta con permiso específico

```typescript
// src/routes/dashboard/lotes/+page.server.ts
import type { PageServerLoad } from './$types';
import { requirePermission } from '$lib/server/auth/guards';

export const load: PageServerLoad = (event) => {
    requirePermission(event, 'lote.ver');
    
    return {
        user: event.locals.userWithPerms
    };
};
```

### Ejemplo 3: Proteger action con permiso

```typescript
// src/routes/dashboard/lotes/+page.server.ts
import type { Actions } from './$types';
import { requirePermission } from '$lib/server/auth/guards';
import { fail } from '@sveltejs/kit';

export const actions: Actions = {
    crear: async (event) => {
        requirePermission(event, 'lote.crear');
        
        // Lógica para crear lote
        // ...
        
        return { success: true };
    },
    
    eliminar: async (event) => {
        requirePermission(event, 'lote.eliminar');
        
        // Lógica para eliminar lote
        // ...
        
        return { success: true };
    }
};
```

### Ejemplo 4: Proteger API endpoint

```typescript
// src/routes/api/lotes/+server.ts
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { requirePermission } from '$lib/server/auth/guards';

export const GET: RequestHandler = async (event) => {
    requirePermission(event, 'lote.ver');
    
    // Lógica para obtener lotes
    const lotes = await prisma.lote.findMany();
    
    return json({ lotes });
};

export const POST: RequestHandler = async (event) => {
    requirePermission(event, 'lote.crear');
    
    const data = await event.request.json();
    // Lógica para crear lote
    
    return json({ success: true });
};
```

### Ejemplo 5: Verificar múltiples permisos

```typescript
// src/routes/dashboard/admin/+page.server.ts
import type { PageServerLoad } from './$types';
import { requireAllPermissions } from '$lib/server/auth/guards';

export const load: PageServerLoad = (event) => {
    // Usuario necesita TODOS estos permisos
    requireAllPermissions(event, ['usuario.ver', 'rol.ver']);
    
    return {
        user: event.locals.userWithPerms
    };
};
```

### Ejemplo 6: Verificar permiso opcionalm ente

```typescript
// src/routes/dashboard/reportes/+page.server.ts
import type { PageServerLoad } from './$types';
import { requireAuth, checkPermission } from '$lib/server/auth/guards';

export const load: PageServerLoad = (event) => {
    requireAuth(event);
    
    const canExport = checkPermission(event, 'reporte.exportar');
    const canGenerate = checkPermission(event, 'reporte.generar');
    
    return {
        user: event.locals.userWithPerms,
        canExport,
        canGenerate
    };
};
```

## Sistema de Permisos

### Formato de Permisos
Los permisos siguen el formato: `namespace.accion`

Ejemplos:
- `lote.ver`
- `lote.crear`
- `pieza.editar`
- `usuario.eliminar`

### Wildcards
- `*` = Acceso total al sistema
- `lote.*` = Acceso completo a lotes (ver, crear, editar, eliminar)
- `pieza.*` = Acceso completo a piezas

### Permisos Disponibles

#### Lotes
- `lote.*` - Acceso completo a lotes
- `lote.ver` - Ver lotes
- `lote.crear` - Crear lotes
- `lote.editar` - Editar lotes
- `lote.eliminar` - Eliminar lotes
- `lote.cerrar` - Cerrar lotes
- `lote.pausar` - Pausar/reanudar lotes

#### Piezas
- `pieza.*` - Acceso completo a piezas
- `pieza.ver` - Ver piezas
- `pieza.editar` - Editar piezas
- `pieza.procesar` - Procesar piezas desde PLC
- `pieza.imagen` - Ver imágenes de piezas

#### Historial
- `historial.ver` - Ver historial
- `historial.exportar` - Exportar historial

#### Dashboard
- `dashboard.realtime` - Acceso al dashboard en tiempo real
- `dashboard.reportes` - Generar reportes

## Roles por Defecto

### Admin
- Permiso: `*` (acceso total)
- Usuario: `admin` / `admin123`

### Operador
- Permisos: `lote.*`, `pieza.*`, `historial.ver`, `dashboard.realtime`
- Usuario: `operador` / `operador123`

### Viewer
- Permisos: `lote.ver`, `pieza.ver`, `pieza.imagen`, `historial.ver`, `dashboard.realtime`
- Usuario: `viewer` / `viewer123`

## Manejo de Errores

### Redirect 302
Si el usuario no está autenticado, `requireAuth()` redirige a `/login`:
```typescript
throw redirect(302, '/login');
```

### Error 403
Si el usuario no tiene el permiso requerido:
```typescript
throw error(403, 'Permiso requerido: lote.crear');
```

Estos errores se pueden manejar en `+error.svelte` para mostrar páginas personalizadas.

