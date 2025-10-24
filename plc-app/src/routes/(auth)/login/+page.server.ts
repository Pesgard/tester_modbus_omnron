import { fail, redirect, type Actions } from "@sveltejs/kit";
import type { PageServerLoad } from "./$types";
import prisma from "$lib/prisma";
import { Argon2id } from "oslo/password";
import { lucia } from "$lib/server/auth/Auth";

export const load: PageServerLoad = async (event) => {
    if (!event.locals.user) {
        // throw redirect(302, '/dashboard');
    }
    return {}
};

export const actions: Actions = {
    default: async ({ request, cookies }) => {
        const formData = await request.formData();
        const username = formData.get('username')?.toString().trim();
        const password = formData.get('password')?.toString();

        if (!username || !password) {
            return fail(400, {
                error: 'Por favor, completa todos los campos.'
            });
        }

        const user = await prisma.user.findUnique({
            where: { username },
            include: {
                roles: {
                    include: {
                        role: true,
                    }
                }
            }
        });

        if (!user) {
            return fail(400, {
                error: 'Usuario o contraseña incorrectos.'
            });
        }

        const validPassword = await new Argon2id().verify(user.hash_password, password);
        if (!validPassword) {
            return fail(400, {
                error: 'Usuario o contraseña incorrectos.'
            });
        }

        const session = await lucia.createSession(user.id, {});
        const sessionCookie = lucia.createSessionCookie(session.id);
        cookies.set(sessionCookie.name, sessionCookie.value, {
            path: '.',
            ...sessionCookie.attributes
        });

        throw redirect(302, '/dashboard');
    }
}