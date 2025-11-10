// src/hooks.server.ts
import type { Handle } from '@sveltejs/kit';
import { lucia } from '$lib/server/auth/Auth';
import { prisma } from '$lib/prisma';
import { initializeServers } from '$lib/server/startup';

// Start tcp and WebSocket servers
// and FTP watcher when the server starts
initializeServers();

/**
 * Handles incoming requests and manages user session validation and cookies.
 *
 * This function is used as a hook in the SvelteKit application to process
 * each incoming request. It validates the user's session using Lucia authentication
 * and sets appropriate cookies for session management.
 *
 * @param {Object} context - The context object containing the event and resolve function.
 * @param {Object} context.event - The event object representing the incoming request.
 * @param {Function} context.resolve - The function to resolve the request and generate a response.
 *
 * @returns {Promise<Response>} The resolved response after processing the request.
 *
 * Functionality:
 * - Retrieves the session ID from cookies using `lucia.sessionCookieName`.
 * - If no session ID is found, sets `event.locals.session` and `event.locals.user` to `null`.
 * - Validates the session using `lucia.validateSession(sessionId)`.
 * - If the session is valid and fresh, creates a new session cookie and updates it in the response.
 * - If the session is invalid, creates a blank session cookie and updates it in the response.
 * - Sets `event.locals.user` and `event.locals.session` with the validated user and session data.
 * - Loads user roles and permissions for authorization.
 * - Resolves the request with the updated event object.
 */
export const handle: Handle = async ({ event, resolve }) => {

	// Validate session and set user in locals
	const sessionId = event.cookies.get(lucia.sessionCookieName);

	// If no session ID, set user and session to null
	if (!sessionId) {
		event.locals.session = null;
		event.locals.user = null;
		event.locals.userWithPerms = null;
		return resolve(event);
	}

	// Validate session and set user in locals
	const { user, session } = await lucia.validateSession(sessionId);

	if (session && session?.fresh) {
		// If session is valid and fresh, create a new session cookie
		const sessionCookie = lucia.createSessionCookie(session.id);

		event.cookies.set(sessionCookie.name, sessionCookie.value, {
			path: '.',
			...sessionCookie.attributes
		});
	}

	if (!session) {
		// If session is invalid, create a blank session cookie
		const sessionCookie = lucia.createBlankSessionCookie();
		event.cookies.set(sessionCookie.name, sessionCookie.value, {
			path: '.',
			...sessionCookie.attributes
		});
	}

	// Set user and session in event locals
	event.locals.user = user;
	event.locals.session = session;

	// Load user with roles and permissions if authenticated
	if (user) {
		const userWithRolesAndPerms = await prisma.user.findUnique({
			where: { id: user.id },
			include: {
				roles: {
					include: {
						role: {
							include: {
								permisosRol: {
									include: {
										permiso: true
									}
								}
							}
						}
					}
				}
			}
		});

		if (userWithRolesAndPerms) {
			// Extract roles and permissions
			const roles = userWithRolesAndPerms.roles.map(ur => ur.role.name);
			const permisos = userWithRolesAndPerms.roles.flatMap(ur =>
				ur.role.permisosRol.map(pr => pr.permiso.key)
			);

			event.locals.userWithPerms = {
				id: userWithRolesAndPerms.id,
				username: userWithRolesAndPerms.username,
				roles,
				permisos
			};
		} else {
			event.locals.userWithPerms = null;
		}
	} else {
		event.locals.userWithPerms = null;
	}

	// Resolve the request with the updated event
	return resolve(event);
};

