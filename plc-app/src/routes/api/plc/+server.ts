/**
 * API endpoint for PLC status
 * GET /api/plc - Get current line status and available lots
 */

import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getLineStatus } from '$lib/server/plc/plc-handler';
import { requirePermission } from '$lib/server/auth/guards';
import { prisma } from '$lib/prisma';

export const GET: RequestHandler = async (event) => {
	requirePermission(event, 'production.dashboard.ver');

	const status = await getLineStatus();
	
	// Get available open lots
	const availableLotes = await prisma.lote.findMany({
		where: { estado: 'OPEN' },
		include: { receta: true },
		orderBy: { started_at: 'desc' },
		take: 10
	});

	return json({
		...status,
		availableLotes
	});
};

