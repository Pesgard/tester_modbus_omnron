// src/routes/api/auth/login/+server.ts
import type { RequestHandler } from './$types';
import { lucia } from '$lib/server/auth/Auth';
import { prisma } from '$lib/prisma';
import { Argon2id } from 'oslo/password';
import { error, json } from '@sveltejs/kit';

export const POST: RequestHandler = async ({ request, cookies }) => {
    const { username, password } = await request.json();

    const user = await prisma.user.findUnique({
        where: { username },
    });

    if (!user || !user.active) throw error(400, 'Usuario o contraseña inválidos');

    const valid = await new Argon2id().verify(user.hash_password, password);
    if (!valid) throw error(400, 'Usuario o contraseña inválidos');

    const session = await lucia.createSession(user.id, {});
    const sessionCookie = lucia.createSessionCookie(session.id);

    cookies.set(sessionCookie.name, sessionCookie.value, {
        path: '.',
        ...sessionCookie.attributes
    });

    return json({ user: { id: user.id, username: user.username } });
};
