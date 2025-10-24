import type { LayoutServerLoad } from './$types';
import { requireAuth } from '$lib/server/auth/guards';

export const load: LayoutServerLoad = (event) => {
    // Proteger todas las rutas dentro de /dashboard
    requireAuth(event);

    return {
        user: event.locals.userWithPerms
    };
};

