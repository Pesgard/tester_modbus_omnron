// src/routes/api/auth/me/+server.ts
import type { RequestHandler } from './$types';
import { error, json } from '@sveltejs/kit';
import { prisma } from '$lib/prisma';

export const GET: RequestHandler = async ({ locals }) => {
    if (!locals.user) throw error(401, 'No autenticado');

    // cargar roles y permisos del usuario
    const user = await prisma.user.findUnique({
        where: { id: locals.user.id },
        include: {
            roles: {
                include: {
                    role: {
                        include: { permisosRol: { include: { permiso: true } } }
                    }
                }
            }
        }
    });

    if (!user) throw error(404, 'Usuario no encontrado');

    const roles = user.roles.map(r => r.role.name);
    const permisos = user.roles.flatMap(r => r.role.permisosRol.map(pr => pr.permiso.key));

    return json({
        id: user.id,
        username: user.username,
        roles,
        permisos
    });
};
