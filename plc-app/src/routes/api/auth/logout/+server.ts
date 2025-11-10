// src/routes/api/auth/logout/+server.ts
import type { RequestHandler } from './$types';
import { lucia } from '$lib/server/auth/Auth';
import { error, json } from '@sveltejs/kit';

export const POST: RequestHandler = async ({ locals, cookies }) => {
    if (!locals.session) throw error(401, 'No autenticado');

    await lucia.invalidateSession(locals.session.id);

    const blank = lucia.createBlankSessionCookie();
    cookies.set(blank.name, blank.value, {
        path: '.',
        ...blank.attributes
    });

    return json({ success: true });
};
