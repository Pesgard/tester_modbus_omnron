/**
 * POST /api/plc/start
 * Start production with a specific lot
 */

import { json, error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { setActiveLot } from '$lib/server/plc/plc-handler';
import { requirePermission } from '$lib/server/auth/guards';
import { prisma } from '$lib/prisma';
import { sendModelIdToPLC } from '$lib/server/tcp/tcp.server';

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

	// Validate model_id exists
	if (!lote.receta.model_id) {
		error(500, 'Recipe does not have a valid model_id');
	}

	if (lote.receta.model_id < 1 || lote.receta.model_id > 7) {
		error(500, `Invalid model_id: ${lote.receta.model_id}. Must be between 1-7`);
	}

	// Set active lot in memory
	setActiveLot(lote.id, lote.receta_id, lote.name);

	// 📤 Send model_id byte to PLC via TCP
	// This informs the PLC which recipe/model configuration to use
	sendModelIdToPLC(lote.receta.model_id);

	return json({
		success: true,
		message: `Production started for lot ${lote.name}`,
		lote: {
			id: lote.id,
			name: lote.name,
			receta: lote.receta
		},
		modelIdSent: lote.receta.model_id
	});
};

