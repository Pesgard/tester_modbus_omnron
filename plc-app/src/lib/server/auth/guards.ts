import { redirect, error } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';
import { hasPermissionSync } from './permissions';

/**
 * Verifica que el usuario esté autenticado.
 * Redirige a /login si no está autenticado.
 */
export function requireAuth(event: RequestEvent) {
	if (!event.locals.user) {
		throw redirect(302, '/login');
	}
	return event.locals.user;
}

/**
 * Verifica que el usuario tenga un permiso específico.
 * Lanza error 403 si no tiene el permiso.
 */
export function requirePermission(event: RequestEvent, permission: string) {
	requireAuth(event);

	if (!event.locals.userWithPerms) {
		throw error(403, 'No tienes permisos suficientes');
	}

	if (!hasPermissionSync(event.locals.userWithPerms, permission)) {
		throw error(403, `Permiso requerido: ${permission}`);
	}

	return event.locals.userWithPerms;
}

/**
 * Verifica que el usuario tenga al menos uno de los permisos especificados.
 * Lanza error 403 si no tiene ninguno de los permisos.
 */
export function requireAnyPermission(event: RequestEvent, permissions: string[]) {
	requireAuth(event);

	if (!event.locals.userWithPerms) {
		throw error(403, 'No tienes permisos suficientes');
	}

	const hasAny = permissions.some(perm => 
		hasPermissionSync(event.locals.userWithPerms!, perm)
	);

	if (!hasAny) {
		throw error(403, `Requiere alguno de estos permisos: ${permissions.join(', ')}`);
	}

	return event.locals.userWithPerms;
}

/**
 * Verifica que el usuario tenga todos los permisos especificados.
 * Lanza error 403 si no tiene todos los permisos.
 */
export function requireAllPermissions(event: RequestEvent, permissions: string[]) {
	requireAuth(event);

	if (!event.locals.userWithPerms) {
		throw error(403, 'No tienes permisos suficientes');
	}

	const hasAll = permissions.every(perm => 
		hasPermissionSync(event.locals.userWithPerms!, perm)
	);

	if (!hasAll) {
		throw error(403, `Requiere todos estos permisos: ${permissions.join(', ')}`);
	}

	return event.locals.userWithPerms;
}

/**
 * Verifica si el usuario tiene un permiso específico.
 * Retorna boolean sin lanzar errores.
 */
export function checkPermission(event: RequestEvent, permission: string): boolean {
	if (!event.locals.userWithPerms) {
		return false;
	}
	return hasPermissionSync(event.locals.userWithPerms, permission);
}

