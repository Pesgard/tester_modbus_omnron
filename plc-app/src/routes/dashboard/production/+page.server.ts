import type { PageServerLoad } from './$types';
import { requirePermission } from '$lib/server/auth/guards';
import { prisma } from '$lib/prisma';
import { getActiveLot, getLineStatus } from '$lib/server/plc/plc-handler';

export const load: PageServerLoad = async (event) => {
	requirePermission(event, 'production.ver');

	// Get current line status
	const lineStatus = await getLineStatus();
	const activeLot = getActiveLot();

	// Get available open lots for selection
	const availableLotes = await prisma.lote.findMany({
		where: {
			estado: 'OPEN'
		},
		include: {
			receta: true
		},
		orderBy: {
			started_at: 'desc'
		},
		take: 10
	});

	// Get recent pieces if there's an active lot
	let recentPieces = [];
	if (activeLot) {
		recentPieces = await prisma.pieza.findMany({
			where: {
				lote_id: activeLot.id
			},
			orderBy: {
				processed_at: 'desc'
			},
			take: 20
		});
	}

	return {
		lineStatus,
		activeLot,
		availableLotes,
		recentPieces,
		user: event.locals.userWithPerms
	};
};

