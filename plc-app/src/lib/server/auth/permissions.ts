import { prisma } from '$lib/prisma';

/**
 * Verifica si un usuario tiene un permiso específico.
 *
 * - Soporta permisos con wildcard (`*`, `lote.*`, etc.)
 * - Los roles pueden otorgar permisos explícitos o globales.
 *
 * @param userId ID del usuario (string)
 * @param key Clave del permiso (ej: "lote.crear")
 * @returns Promise<boolean>
 */
export async function hasPermission(userId: string, key: string): Promise<boolean> {
    const user = await prisma.user.findUnique({
        where: { id: userId },
        include: {
            roles: {
                include: {
                    role: {
                        include: {
                            permisosRol: { include: { permiso: true } }
                        }
                    }
                }
            }
        }
    });

    if (!user) return false;

    // Extraer todas las claves de permisos de todos los roles
    const permisos = user.roles.flatMap(r =>
        r.role.permisosRol.map(pr => pr.permiso.key)
    );

    // Caso 1: admin global
    if (permisos.includes('*')) return true;

    // Caso 2: coincidencia exacta
    if (permisos.includes(key)) return true;

    // Caso 3: wildcard por namespace (ej: "lote.*")
    const [namespace] = key.split('.');
    if (permisos.includes(`${namespace}.*`)) return true;

    return false;
}


/**
 * Verifica si un usuario (ya cargado en locals) tiene un permiso específico.
 *
 * - Soporta permisos con wildcard (`*`, `lote.*`, etc.)
 * - Trabaja solo en memoria (no consulta DB).
 *
 * @param user Objeto user en locals, con roles y permisos incluidos
 * @param key Clave del permiso (ej: "lote.crear")
 * @returns boolean
 */
export function hasPermissionSync(
    user: {
        id: string;
        username: string;
        roles: string[];
        permisos: string[];
    } | null,
    key: string
): boolean {
    if (!user) return false;

    const permisos = user.permisos ?? [];

    // Caso 1: admin global
    if (permisos.includes('*')) return true;

    // Caso 2: coincidencia exacta
    if (permisos.includes(key)) return true;

    // Caso 3: wildcard por namespace (ej: "lote.*")
    const [namespace] = key.split('.');
    if (permisos.includes(`${namespace}.*`)) return true;

    return false;
}
