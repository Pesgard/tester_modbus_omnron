import type { PageServerLoad } from './$types';

export const load: PageServerLoad = () => {
    // La autenticación se verifica en +layout.server.ts
    // Aquí podemos agregar datos específicos de esta página
    return {};
};