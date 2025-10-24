// prisma/seed.js
import { PrismaClient } from '@prisma/client';
import { Argon2id } from 'oslo/password';
import crypto from 'crypto';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Iniciando seed...');

  try {
    // 1. Limpiar datos existentes (orden correcto para evitar FK errors)
    console.log('🧹 Limpiando datos existentes...');
    
    await prisma.historial.deleteMany();
    console.log('  ✅ Historial limpiado');
    
    await prisma.imagen.deleteMany();
    console.log('  ✅ Imágenes limpiadas');
    
    await prisma.pieza.deleteMany();
    console.log('  ✅ Piezas limpiadas');
    
    await prisma.lote.deleteMany();
    console.log('  ✅ Lotes limpiados');
    
    await prisma.receta.deleteMany();
    console.log('  ✅ Recetas limpiadas');
    
    await prisma.permisoRol.deleteMany();
    console.log('  ✅ Permisos-roles limpiados');
    
    await prisma.userRole.deleteMany();
    console.log('  ✅ Usuario-roles limpiados');
    
    await prisma.session.deleteMany();
    console.log('  ✅ Sesiones limpiadas');
    
    await prisma.user.deleteMany();
    console.log('  ✅ Usuarios limpiados');
    
    await prisma.permiso.deleteMany();
    console.log('  ✅ Permisos limpiados');
    
    await prisma.role.deleteMany();
    console.log('  ✅ Roles limpiados');

    // 2. Crear permisos granulares
    console.log('\n📋 Creando permisos granulares...');
    const permisos = [
      // ============================================
      // SECCIONES PRINCIPALES (Navegación)
      // ============================================
      { key: 'production.ver', description: 'Acceso a sección Production (Lote Activo)' },
      { key: 'history.ver', description: 'Acceso a sección History (Historial de Lotes)' },
      { key: 'management.ver', description: 'Acceso a sección Management (CRUD)' },

      // ============================================
      // PRODUCTION (Lote Activo en Tiempo Real)
      // ============================================
      { key: 'production.dashboard.ver', description: 'Ver dashboard de producción en tiempo real' },
      { key: 'production.metrics.ver', description: 'Ver métricas (rate, efficiency, accuracy)' },
      { key: 'production.status.ver', description: 'Ver estado de producción (running/stopped)' },
      { key: 'production.control.start', description: 'Iniciar producción' },
      { key: 'production.control.stop', description: 'Detener producción' },
      { key: 'production.control.pause', description: 'Pausar producción' },
      { key: 'production.control.resume', description: 'Reanudar producción' },
      { key: 'production.lote.select', description: 'Seleccionar lote activo' },
      { key: 'production.lote.info', description: 'Ver información del lote activo' },
      { key: 'production.pieces.ver', description: 'Ver piezas en tiempo real' },
      { key: 'production.pieces.last', description: 'Ver última pieza procesada' },
      { key: 'production.pieces.count', description: 'Ver contadores de piezas OK/NOK' },

      // ============================================
      // HISTORY (Historial de Lotes)
      // ============================================
      { key: 'history.lotes.ver', description: 'Ver lista de lotes históricos' },
      { key: 'history.lotes.filtrar', description: 'Filtrar lotes por fecha/estado/receta' },
      { key: 'history.lotes.buscar', description: 'Buscar lotes' },
      { key: 'history.lotes.detalles', description: 'Ver detalles de un lote' },
      { key: 'history.lotes.exportar', description: 'Exportar datos de lotes' },
      { key: 'history.piezas.ver', description: 'Ver piezas de un lote' },
      { key: 'history.piezas.filtrar', description: 'Filtrar piezas (OK/NOK)' },
      { key: 'history.piezas.detalles', description: 'Ver detalles de una pieza' },
      { key: 'history.imagenes.ver', description: 'Ver imágenes de fallas' },
      { key: 'history.imagenes.descargar', description: 'Descargar imágenes' },
      { key: 'history.reportes.generar', description: 'Generar reportes históricos' },
      { key: 'history.reportes.exportar', description: 'Exportar reportes' },
      { key: 'history.estadisticas.ver', description: 'Ver estadísticas históricas' },

      // ============================================
      // MANAGEMENT (CRUD de Entidades)
      // ============================================
      // Recetas
      { key: 'management.recetas.ver', description: 'Ver lista de recetas' },
      { key: 'management.recetas.crear', description: 'Crear nueva receta' },
      { key: 'management.recetas.editar', description: 'Editar receta existente' },
      { key: 'management.recetas.eliminar', description: 'Eliminar receta' },
      { key: 'management.recetas.activar', description: 'Activar/desactivar receta' },
      { key: 'management.recetas.importar', description: 'Importar recetas desde CSV/Excel' },
      { key: 'management.recetas.exportar', description: 'Exportar recetas' },

      // Lotes
      { key: 'management.lotes.ver', description: 'Ver lista de lotes' },
      { key: 'management.lotes.crear', description: 'Crear nuevo lote' },
      { key: 'management.lotes.editar', description: 'Editar lote' },
      { key: 'management.lotes.eliminar', description: 'Eliminar lote' },
      { key: 'management.lotes.cerrar', description: 'Cerrar lote manualmente' },
      { key: 'management.lotes.reabrir', description: 'Reabrir lote cerrado' },
      { key: 'management.lotes.pausar', description: 'Pausar lote' },
      { key: 'management.lotes.reanudar', description: 'Reanudar lote pausado' },

      // Usuarios
      { key: 'management.usuarios.ver', description: 'Ver lista de usuarios' },
      { key: 'management.usuarios.crear', description: 'Crear nuevo usuario' },
      { key: 'management.usuarios.editar', description: 'Editar usuario' },
      { key: 'management.usuarios.eliminar', description: 'Eliminar usuario' },
      { key: 'management.usuarios.activar', description: 'Activar/desactivar usuario' },
      { key: 'management.usuarios.password', description: 'Cambiar contraseña de usuario' },
      { key: 'management.usuarios.roles', description: 'Asignar/quitar roles' },

      // Roles y Permisos
      { key: 'management.roles.ver', description: 'Ver lista de roles' },
      { key: 'management.roles.crear', description: 'Crear nuevo rol' },
      { key: 'management.roles.editar', description: 'Editar rol' },
      { key: 'management.roles.eliminar', description: 'Eliminar rol' },
      { key: 'management.roles.permisos', description: 'Asignar/quitar permisos a rol' },

      // ============================================
      // CORE (Operaciones Básicas)
      // ============================================
      { key: 'core.lote.crear', description: 'Crear nuevo lote' },
      { key: 'core.lote.ver', description: 'Ver lotes' },
      { key: 'core.lote.editar', description: 'Editar lote' },
      { key: 'core.lote.cerrar', description: 'Cerrar lote' },
      { key: 'core.lote.eliminar', description: 'Eliminar lote' },
      { key: 'core.pieza.ver', description: 'Ver piezas' },
      { key: 'core.pieza.procesar', description: 'Procesar desde PLC' },
      { key: 'core.pieza.editar', description: 'Editar pieza manualmente' },
      { key: 'core.pieza.eliminar', description: 'Eliminar pieza' },

      // ============================================
      // SYSTEM (Configuración y Admin)
      // ============================================
      { key: 'system.config.ver', description: 'Ver configuración del sistema' },
      { key: 'system.config.editar', description: 'Editar configuración' },
      { key: 'system.logs.ver', description: 'Ver logs del sistema' },
      { key: 'system.logs.exportar', description: 'Exportar logs' },

      // ============================================
      // WILDCARDS (Accesos Globales)
      // ============================================
      { key: '*', description: 'Acceso total al sistema' },
      { key: 'production.*', description: 'Acceso completo a Production' },
      { key: 'history.*', description: 'Acceso completo a History' },
      { key: 'management.*', description: 'Acceso completo a Management' },
      { key: 'management.recetas.*', description: 'Gestión completa de recetas' },
      { key: 'management.lotes.*', description: 'Gestión completa de lotes' },
      { key: 'management.usuarios.*', description: 'Gestión completa de usuarios' },
      { key: 'management.roles.*', description: 'Gestión completa de roles' },
    ];

    for (const permisoData of permisos) {
      await prisma.permiso.create({ data: permisoData });
    }
    console.log(`  ✅ ${permisos.length} permisos creados`);

    // 3. Crear roles
    console.log('\n👥 Creando roles...');
    
    // Admin: Acceso total
    const adminRole = await prisma.role.create({
      data: {
        name: 'admin',
        description: 'Administrador - Acceso total al sistema'
      }
    });

    // Manager: Gestión completa + Ver producción e historial
    const managerRole = await prisma.role.create({
      data: {
        name: 'manager',
        description: 'Gerente - Gestión completa de lotes + Ver producción e historial'
      }
    });

    // Operador: Operar producción + Ver historial
    const operadorRole = await prisma.role.create({
      data: {
        name: 'operador',
        description: 'Operador - Operar línea de producción y consultar historial'
      }
    });

    // Viewer: Solo lectura
    const viewerRole = await prisma.role.create({
      data: {
        name: 'viewer',
        description: 'Visualizador - Solo lectura de producción e historial'
      }
    });

    console.log('  ✅ 4 roles creados');

    // 4. Asignar permisos a roles
    console.log('\n🔐 Asignando permisos a roles...');
    
    // Admin: Acceso total
    const adminPermisos = ['*'];
    for (const key of adminPermisos) {
      const permiso = await prisma.permiso.findUnique({ where: { key } });
      if (permiso) {
        await prisma.permisoRol.create({
          data: { roleId: adminRole.id, permisoId: permiso.id }
        });
      }
    }

    // Manager: Gestión completa + Visualización
    const managerPermisos = [
      // Ver todas las secciones
      'production.ver',
      'history.ver',
      'management.ver',
      
      // Ver producción pero NO controlarla
      'production.dashboard.ver',
      'production.metrics.ver',
      'production.status.ver',
      'production.lote.info',
      'production.pieces.ver',
      'production.pieces.last',
      'production.pieces.count',
      
      // History completo
      'history.*',
      
      // Management completo
      'management.*',
    ];
    for (const key of managerPermisos) {
      const permiso = await prisma.permiso.findUnique({ where: { key } });
      if (permiso) {
        await prisma.permisoRol.create({
          data: { roleId: managerRole.id, permisoId: permiso.id }
        });
      }
    }

    // Operador: Control de producción + Ver historial
    const operadorPermisos = [
      // Ver secciones
      'production.ver',
      'history.ver',
      
      // Production: Control completo
      'production.*',
      
      // History: Solo lectura
      'history.lotes.ver',
      'history.lotes.filtrar',
      'history.lotes.buscar',
      'history.lotes.detalles',
      'history.piezas.ver',
      'history.piezas.filtrar',
      'history.piezas.detalles',
      'history.imagenes.ver',
      'history.estadisticas.ver',
      
      // Core operations
      'core.pieza.procesar',
    ];
    for (const key of operadorPermisos) {
      const permiso = await prisma.permiso.findUnique({ where: { key } });
      if (permiso) {
        await prisma.permisoRol.create({
          data: { roleId: operadorRole.id, permisoId: permiso.id }
        });
      }
    }

    // Viewer: Solo lectura de producción e historial
    const viewerPermisos = [
      'production.ver',
      'history.ver',
      'production.dashboard.ver',
      'production.metrics.ver',
      'production.status.ver',
      'production.lote.info',
      'production.pieces.ver',
      'production.pieces.last',
      'production.pieces.count',
      'history.lotes.ver',
      'history.lotes.filtrar',
      'history.lotes.buscar',
      'history.lotes.detalles',
      'history.piezas.ver',
      'history.piezas.filtrar',
      'history.piezas.detalles',
      'history.imagenes.ver',
      'history.estadisticas.ver',
    ];
    for (const key of viewerPermisos) {
      const permiso = await prisma.permiso.findUnique({ where: { key } });
      if (permiso) {
        await prisma.permisoRol.create({
          data: { roleId: viewerRole.id, permisoId: permiso.id }
        });
      }
    }
    console.log('  ✅ Permisos asignados a roles');

    // 5. Crear usuarios
    console.log('\n👤 Creando usuarios...');
    const argon2id = new Argon2id();
    
    const adminPassword = await argon2id.hash('admin123');
    const managerPassword = await argon2id.hash('manager123');
    const operadorPassword = await argon2id.hash('operador123');
    const viewerPassword = await argon2id.hash('viewer123');

    const adminUser = await prisma.user.create({
      data: {
        id: crypto.randomUUID(),
        username: 'admin',
        hash_password: adminPassword,
        active: true
      }
    });

    const managerUser = await prisma.user.create({
      data: {
        id: crypto.randomUUID(),
        username: 'manager',
        hash_password: managerPassword,
        active: true
      }
    });

    const operadorUser = await prisma.user.create({
      data: {
        id: crypto.randomUUID(),
        username: 'operador',
        hash_password: operadorPassword,
        active: true
      }
    });

    const viewerUser = await prisma.user.create({
      data: {
        id: crypto.randomUUID(),
        username: 'viewer',
        hash_password: viewerPassword,
        active: true
      }
    });
    console.log('  ✅ 4 usuarios creados');

    // 6. Asignar roles a usuarios
    console.log('\n🔗 Asignando roles a usuarios...');
    await prisma.userRole.create({
      data: { userId: adminUser.id, roleId: adminRole.id }
    });

    await prisma.userRole.create({
      data: { userId: managerUser.id, roleId: managerRole.id }
    });

    await prisma.userRole.create({
      data: { userId: operadorUser.id, roleId: operadorRole.id }
    });

    await prisma.userRole.create({
      data: { userId: viewerUser.id, roleId: viewerRole.id }
    });
    console.log('  ✅ Roles asignados a usuarios');

    // 7. Crear recetas desde los datos reales
    console.log('\n📦 Creando recetas...');
    const recetas = [
      {
        ppn: '1020746',
        cable_np: '664030001',
        quantity: 16.0,
        u_of_m: 'FT',
        item_description: 'ASM CBL AC POWER WHIP IEC WIRE COLORS 4 AWG 156 IN. ELM #1020746 ISSUE 1.0 RC',
        cantidad_conductores: 5,
        l1_terminal: 'Ferrul',
        l2_terminal: 'Ferrul',
        activa: true
      },
      {
        ppn: '1020746-02',
        cable_np: '664030001',
        quantity: 16.5,
        u_of_m: 'FT',
        item_description: 'ASM CBL AC POWER WHIP IEC WIRE COLORS 4 AWG 152 IN. RA-RA ELM #1020746-02 ISSUE 2.1 RC',
        cantidad_conductores: 5,
        l1_terminal: 'Ferrul',
        l2_terminal: 'Ferrul',
        activa: true
      },
      {
        ppn: '1020747',
        cable_np: '664030001',
        quantity: 16.5,
        u_of_m: 'FT',
        item_description: 'ASM CBL AC POWER WHIP IEC WIRE COLORS 4 AWG 156 IN. ELM #1020746 ISSUE 1.0 RC',
        cantidad_conductores: 5,
        l1_terminal: 'Ferrul',
        l2_terminal: 'Ferrul',
        activa: true
      },
      {
        ppn: '683950001',
        cable_np: '664030001',
        quantity: 17.5,
        u_of_m: 'FT',
        item_description: 'ASM CBL AC POWER WHIP FOR JOLT51 WITH TERM BLOCKS 4 AWG 178 IN ELM 1040287-01 REV 1.7 RC',
        cantidad_conductores: 5,
        l1_terminal: 'Terminal',
        l2_terminal: 'Ferrul',
        activa: true
      },
      {
        ppn: '694030001',
        cable_np: '664030001',
        quantity: 20.666,
        u_of_m: 'FT',
        item_description: 'ASM CBL AC POWER WHIP FOR JOLT21/51/100 W/ TERMINAL BLOCKS 4 AWG 216 IN. ELM 1086740-01 REV 1.0 RC',
        cantidad_conductores: 5,
        l1_terminal: 'Terminal',
        l2_terminal: 'Ferrul',
        activa: true
      },
      {
        ppn: '717140001',
        cable_np: '664030001',
        quantity: 20.67,
        u_of_m: 'FT',
        item_description: 'ASM CBL AC POWER WHIP, DESCHUTES CDU UPS FEED , ELM 1147118-01 RCV 1.0 RC',
        cantidad_conductores: 5,
        l1_terminal: 'Ferrul',
        l2_terminal: 'Ferrul',
        activa: true
      },
      {
        ppn: '698330001',
        cable_np: '698340001',
        quantity: 20.2,
        u_of_m: 'FT',
        item_description: 'ASM, CBL, AC POWER WHIP, IEC COLOR SCHEME, RHINO, 4 AWG, ELM 1091039 RC',
        cantidad_conductores: 4,
        l1_terminal: 'Ferrul',
        l2_terminal: 'Ferrul',
        activa: true
      }
    ];

    for (const recetaData of recetas) {
      await prisma.receta.create({ data: recetaData });
    }
    console.log(`  ✅ ${recetas.length} recetas creadas`);

    // 8. Crear lote de ejemplo con primera receta
    console.log('\n📦 Creando lote de ejemplo...');
    const primeraReceta = await prisma.receta.findFirst({
      where: { ppn: '1020746' }
    });

    if (primeraReceta) {
      const loteEjemplo = await prisma.lote.create({
        data: {
          name: 'LOTE-001-' + new Date().toISOString().slice(0, 10),
          receta_id: primeraReceta.id,
          max_piezas_ok: 100,
          created_by: operadorUser.id,
          estado: 'OPEN'
        }
      });

      // Crear algunas piezas de ejemplo
      for (let i = 1; i <= 5; i++) {
        await prisma.pieza.create({
          data: {
            lote_id: loteEjemplo.id,
            resultado_bits: [1, 0, 0, 1, 0, 1, 1, 0], // Ejemplo de resultado OK
            ok: true,
            indice: i,
            imagen_path: `/images/lote-${loteEjemplo.id}/pieza-${i}.jpg`,
            processed_by: operadorUser.id,
            processed_at: new Date()
          }
        });
      }

      // Actualizar contadores del lote
      await prisma.lote.update({
        where: { id: loteEjemplo.id },
        data: {
          piezas_ok: 5,
          piezas_fallas: 0
        }
      });

      console.log(`  ✅ Lote ejemplo creado: ${loteEjemplo.name} con 5 piezas`);
    }

    console.log('\n🎉 Seed completado exitosamente');
    console.log('\n📊 Resumen:');
    console.log('  - Permisos:', permisos.length);
    console.log('  - Roles: 4 (admin, manager, operador, viewer)');
    console.log('  - Usuarios: 4');
    console.log('  - Recetas: 7');
    console.log('  - Lotes: 1 (con 5 piezas de ejemplo)');
    console.log('\n👥 Credenciales de acceso:');
    console.log('  🔑 admin / admin123 (Acceso total)');
    console.log('  👔 manager / manager123 (Gestión + Visualización)');
    console.log('  ⚙️ operador / operador123 (Control de producción)');
    console.log('  👁️ viewer / viewer123 (Solo lectura)');

  } catch (error) {
    console.error('❌ Error durante seed:', error);
    throw error;
  }
}

main()
  .catch((e) => {
    console.error('❌ Error en seed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
