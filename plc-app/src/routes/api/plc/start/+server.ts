/**
 * POST /api/plc/start
 * Start production with a specific lot
 */

import { json, error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { setActiveLot } from '$lib/server/plc/plc-handler';
import { requirePermission } from '$lib/server/auth/guards';
import { prisma } from '$lib/prisma';

export const POST: RequestHandler = async (event) => {
	requirePermission(event, 'production.control.start');

	const { loteId } = await event.request.json();

	if (!loteId) {
		error(400, 'loteId is required');
	}

	// Verify lot exists and is open
	const lote = await prisma.lote.findUnique({
		where: { id: loteId },
		include: { receta: true }
	});

	if (!lote) {
		error(404, 'Lote not found');
	}

	if (lote.estado !== 'OPEN') {
		error(400, `Lote is ${lote.estado}, cannot start production`);
	}

	setActiveLot(lote.id, lote.receta_id, lote.name);

	return json({
		success: true,
		message: `Production started for lot ${lote.name}`,
		lote: {
			id: lote.id,
			name: lote.name,
			receta: lote.receta
		}
	});
};

