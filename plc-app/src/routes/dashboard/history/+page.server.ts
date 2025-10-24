import type { PageServerLoad } from './$types';
import { requirePermission } from '$lib/server/auth/guards';
import { prisma } from '$lib/prisma';

export const load: PageServerLoad = async (event) => {
	requirePermission(event, 'history.ver');

	// Get recent closed lots with their stats
	const lotes = await prisma.lote.findMany({
		where: {
			estado: { in: ['CLOSED', 'PAUSED'] }
		},
		include: {
			receta: true,
			creator: {
				select: {
					username: true
				}
			},
			_count: {
				select: {
					piezas: true
				}
			}
		},
		orderBy: {
			closed_at: 'desc'
		},
		take: 50
	});

	return {
		lotes,
		user: event.locals.userWithPerms
	};
};

