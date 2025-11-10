/**
 * API endpoint to get images for a specific lot
 * GET /api/images/[loteId]
 */

import { json, error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { requirePermission } from '$lib/server/auth/guards';
import { getLotImages, getImagesByFailureType } from '$lib/server/plc/image-handler';

export const GET: RequestHandler = async ({ params, url, locals }) => {
	requirePermission({ locals } as any, 'history.ver');

	const { loteId } = params;
	
	// Optional filter by failure type
	const failureCodeParam = url.searchParams.get('failureCode');
	
	if (!loteId) {
		error(400, 'loteId is required');
	}

	try {
		let images;
		
		if (failureCodeParam) {
			const failureCode = parseInt(failureCodeParam);
			if (isNaN(failureCode)) {
				error(400, 'Invalid failureCode');
			}
			images = await getImagesByFailureType(loteId, failureCode);
		} else {
			images = await getLotImages(loteId);
		}

		return json({
			loteId,
			count: images.length,
			images
		});
	} catch (err) {
		console.error('[API Images] Error fetching images:', err);
		error(500, 'Failed to fetch images');
	}
};

