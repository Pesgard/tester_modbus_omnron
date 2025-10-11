// prisma/seed.js
import { PrismaClient } from '@prisma/client';
import { Argon2id } from 'oslo/password';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Iniciando seed de la base de datos...');

  // ============================================
  // 1. CREAR PERMISOS
  // ============================================
  console.log('📋 Creando permisos...');
  
  const permisos = [
    // Admin
    { key: '*', description: 'Acceso total al sistema' },
    { key: 'admin.users', description: 'Gestionar usuarios' },
    { key: 'admin.config', description: 'Configuración del sistema' },
    
    // Lotes
    { key: 'lote.*', description: 'Acceso completo a lotes' },
    { key: 'lote.crear', description: 'Crear nuevos lotes' },
    { key: 'lote.ver', description: 'Ver lotes' },
    { key: 'lote.cerrar', description: 'Cerrar lotes' },
    { key: 'lote.pausar', description: 'Pausar/reanudar lotes' },
    
    // Piezas
    { key: 'pieza.*', description: 'Acceso completo a piezas' },
    { key: 'pieza.ver', description: 'Ver piezas y resultados' },
    { key: 'pieza.procesar', description: 'Procesar piezas desde PLC' },
    { key: 'pieza.imagen', description: 'Ver imágenes de piezas' },
    
    // Historial
    { key: 'historial.ver', description: 'Ver historial de acciones' },
    { key: 'historial.exportar', description: 'Exportar reportes' },
    
    // Dashboard
    { key: 'dashboard.realtime', description: 'Dashboard en tiempo real' },
    { key: 'dashboard.reportes', description: 'Generar reportes' }
  ];

  for (const permiso of permisos) {
    await prisma.permiso.upsert({
      where: { key: permiso.key },
      update: {},
      create: permiso
    });
  }

  // ============================================
  // 2. CREAR ROLES
  // ============================================
  console.log('👥 Creando roles...');

  // Rol: Administrador
  const adminRole = await prisma.role.upsert({
    where: { name: 'admin' },
    update: {},
    create: {
      name: 'admin',
      description: 'Administrador del sistema - Acceso total'
    }
  });

  // Rol: Operador
  const operadorRole = await prisma.role.upsert({
    where: { name: 'operador' },
    update: {},
    create: {
      name: 'operador',
      description: 'Operador de producción - Gestión de lotes y piezas'
    }
  });

  // Rol: Viewer
  const viewerRole = await prisma.role.upsert({
    where: { name: 'viewer' },
    update: {},
    create: {
      name: 'viewer',
      description: 'Solo lectura - Ver lotes, piezas e historial'
    }
  });

  // ============================================
  // 3. ASIGNAR PERMISOS A ROLES
  // ============================================
  console.log('🔗 Asignando permisos a roles...');

  // Admin: Acceso total
  const adminPermisos = await prisma.permiso.findMany({
    where: { key: { in: ['*'] } }
  });

  for (const permiso of adminPermisos) {
    await prisma.permisoRol.upsert({
      where: {
        roleId_permisoId: {
          roleId: adminRole.id,
          permisoId: permiso.id
        }
      },
      update: {},
      create: {
        roleId: adminRole.id,
        permisoId: permiso.id
      }
    });
  }

  // Operador: Gestión de lotes y piezas
  const operadorPermisosKeys = [
    'lote.*',
    'pieza.*',
    'historial.ver',
    'dashboard.realtime'
  ];
  
  const operadorPermisos = await prisma.permiso.findMany({
    where: { key: { in: operadorPermisosKeys } }
  });

  for (const permiso of operadorPermisos) {
    await prisma.permisoRol.upsert({
      where: {
        roleId_permisoId: {
          roleId: operadorRole.id,
          permisoId: permiso.id
        }
      },
      update: {},
      create: {
        roleId: operadorRole.id,
        permisoId: permiso.id
      }
    });
  }

  // Viewer: Solo lectura
  const viewerPermisosKeys = [
    'lote.ver',
    'pieza.ver',
    'pieza.imagen',
    'historial.ver',
    'dashboard.realtime'
  ];
  
  const viewerPermisos = await prisma.permiso.findMany({
    where: { key: { in: viewerPermisosKeys } }
  });

  for (const permiso of viewerPermisos) {
    await prisma.permisoRol.upsert({
      where: {
        roleId_permisoId: {
          roleId: viewerRole.id,
          permisoId: permiso.id
        }
      },
      update: {},
      create: {
        roleId: viewerRole.id,
        permisoId: permiso.id
      }
    });
  }

  // ============================================
  // 4. CREAR USUARIOS DE PRUEBA
  // ============================================
  console.log('👤 Creando usuarios de prueba...');

  const argon2id = new Argon2id();

  // Usuario Admin
  const adminPassword = await argon2id.hash('admin123');
  const adminUser = await prisma.user.upsert({
    where: { username: 'admin' },
    update: {},
    create: {
      id: crypto.randomUUID(),
      username: 'admin',
      hash_password: adminPassword,
      active: true
    }
  });

  // Asignar rol admin
  await prisma.userRole.upsert({
    where: {
      userId_roleId: {
        userId: adminUser.id,
        roleId: adminRole.id
      }
    },
    update: {},
    create: {
      userId: adminUser.id,
      roleId: adminRole.id
    }
  });

  // Usuario Operador
  const operadorPassword = await argon2id.hash('operador123');
  const operadorUser = await prisma.user.upsert({
    where: { username: 'operador' },
    update: {},
    create: {
      id: crypto.randomUUID(),
      username: 'operador',
      hash_password: operadorPassword,
      active: true
    }
  });

  // Asignar rol operador
  await prisma.userRole.upsert({
    where: {
      userId_roleId: {
        userId: operadorUser.id,
        roleId: operadorRole.id
      }
    },
    update: {},
    create: {
      userId: operadorUser.id,
      roleId: operadorRole.id
    }
  });

  // Usuario Viewer
  const viewerPassword = await argon2id.hash('viewer123');
  const viewerUser = await prisma.user.upsert({
    where: { username: 'viewer' },
    update: {},
    create: {
      id: crypto.randomUUID(),
      username: 'viewer',
      hash_password: viewerPassword,
      active: true
    }
  });

  // Asignar rol viewer
  await prisma.userRole.upsert({
    where: {
      userId_roleId: {
        userId: viewerUser.id,
        roleId: viewerRole.id
      }
    },
    update: {},
    create: {
      userId: viewerUser.id,
      roleId: viewerRole.id
    }
  });

  // Usuario de prueba adicional (operador)
  const testPassword = await argon2id.hash('test123');
  const testUser = await prisma.user.upsert({
    where: { username: 'test' },
    update: {},
    create: {
      id: crypto.randomUUID(),
      username: 'test',
      hash_password: testPassword,
      active: true
    }
  });

  // Asignar rol operador al usuario test
  await prisma.userRole.upsert({
    where: {
      userId_roleId: {
        userId: testUser.id,
        roleId: operadorRole.id
      }
    },
    update: {},
    create: {
      userId: testUser.id,
      roleId: operadorRole.id
    }
  });

  // ============================================
  // 5. CREAR LOTE DE EJEMPLO
  // ============================================
  console.log('📦 Creando lote de ejemplo...');

  const loteEjemplo = await prisma.lote.create({
    data: {
      name: 'Lote-Demo-001',
      estado: 'OPEN',
      max_piezas_ok: 100,
      piezas_ok: 0,
      piezas_fallas: 0,
      started_at: new Date(),
      created_by: adminUser.id
    }
  });

  // ============================================
  // 6. CREAR REGISTRO EN HISTORIAL
  // ============================================
  console.log('📋 Creando registro inicial en historial...');

  await prisma.historial.create({
    data: {
      lote_id: loteEjemplo.id,
      user_id: adminUser.id,
      action_key: 'lote.creado',
      meta: {
        message: 'Lote de ejemplo creado durante el seed',
        maxPiezasOk: 100
      }
    }
  });

  // ============================================
  // RESUMEN
  // ============================================
  console.log('\n✅ Seed completado exitosamente!');
  console.log('\n👥 Usuarios creados:');
  console.log('  🔑 admin    / admin123    (Administrador)');
  console.log('  ⚙️ operador / operador123 (Operador)');
  console.log('  👁️ viewer   / viewer123   (Solo lectura)');
  console.log('  🧪 test     / test123     (Operador - pruebas)');
  
  console.log('\n🏷️ Roles configurados:');
  console.log('  • admin    - Acceso total (*)');
  console.log('  • operador - Gestión lotes y piezas');
  console.log('  • viewer   - Solo lectura');
  
  console.log('\n📦 Datos de ejemplo:');
  console.log(`  • Lote: ${loteEjemplo.name} (ID: ${loteEjemplo.id})`);
  
  console.log('\n🚀 Para probar los endpoints:');
  console.log('  POST /api/auth/login { "username": "admin", "password": "admin123" }');
  console.log('  GET  /api/auth/me');
  console.log('  POST /api/auth/logout');
}

main()
  .catch((e) => {
    console.error('❌ Error durante el seed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });