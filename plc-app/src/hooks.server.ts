// src/hooks.server.ts
import type { Handle } from '@sveltejs/kit';
import { startServices } from '$lib/server/startup.js';

// Inicia servicios al levantar el servidor
startServices();

export const handle: Handle = async ({ event, resolve }) => {
	return resolve(event);
};
