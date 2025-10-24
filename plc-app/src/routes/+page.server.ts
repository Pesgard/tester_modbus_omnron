import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
    // Si el usuario tiene sesión iniciada, redirigir al dashboard
    if (locals.user) {
        throw redirect(302, '/dashboard');
    }
    
    // Si no tiene sesión, redirigir al login
    throw redirect(302, '/login');
};