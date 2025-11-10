
// src/routes/api/auth/register/+server.ts
import type { RequestHandler } from './$types';
import { lucia } from '$lib/server/auth/Auth';
import { prisma } from '$lib/prisma';
import { json } from '@sveltejs/kit';
import { Argon2id } from 'oslo/password';
import { error } from '@sveltejs/kit';
import { hasPermission } from '$lib/server/auth/permissions';

export const POST: RequestHandler = async ({ request, locals }) => {
    if (!locals.user) throw error(401, 'No autenticado');
    if (!hasPermission(locals.user.id, 'admin.users')) throw error(403, 'No autorizado');

    const { username, password, roleId } = await request.json();

    if (!username || !password) throw error(400, 'Datos incompletos');

    const hashed = await new Argon2id().hash(password);

    const user = await prisma.user.create({
        data: {
            id: crypto.randomUUID(),
            username,
            hash_password: hashed,
            active: true,
            roles: roleId ? { create: { roleId } } : undefined
        }
    });

    return json({ id: user.id, username: user.username });
};
