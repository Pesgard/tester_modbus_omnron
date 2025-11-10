import type { PageServerLoad } from './$types';
import { requirePermission } from '$lib/server/auth/guards';
import { prisma } from '$lib/prisma';

export const load: PageServerLoad = async (event) => {
	requirePermission(event, 'management.ver');

	// Get counts for dashboard
	const [recetasCount, lotesCount, usersCount] = await Promise.all([
		prisma.receta.count(),
		prisma.lote.count(),
		prisma.user.count()
	]);

	return {
		stats: {
			recetas: recetasCount,
			lotes: lotesCount,
			users: usersCount
		},
		user: event.locals.userWithPerms
	};
};

