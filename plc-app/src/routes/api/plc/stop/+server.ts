/**
 * DELETE /api/plc/stop
 * Stop production and clear active lot
 */

import { json, error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getActiveLot, clearActiveLot } from '$lib/server/plc/plc-handler';
import { requirePermission } from '$lib/server/auth/guards';

export const DELETE: RequestHandler = async (event) => {
	requirePermission(event, 'production.control.stop');

	const activeLot = getActiveLot();

	if (!activeLot) {
		error(400, 'No active lot to stop');
	}

	clearActiveLot();

	return json({
		success: true,
		message: 'Production stopped'
	});
};

