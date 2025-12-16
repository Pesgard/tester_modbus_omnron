/**
 * API endpoint to serve images from the data/images directory
 * GET /api/images/serve/[...path]
 * 
 * This endpoint serves images that are stored outside the static directory
 * to avoid build issues. Images are stored in data/images/ directory.
 */

import { error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import fs from 'fs/promises';
import path from 'path';

// Base directory where images are stored (outside static)
const IMAGES_BASE_DIR = process.env.IMAGES_BASE_DIR || path.join(process.cwd(), 'data', 'images');

// Allowed image extensions
const ALLOWED_EXTENSIONS = new Set(['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']);

export const GET: RequestHandler = async ({ params }) => {
	const { path: imagePath } = params;

	if (!imagePath) {
		error(400, 'Image path is required');
	}

	// Security: Prevent directory traversal
	if (imagePath.includes('..') || path.isAbsolute(imagePath)) {
		error(400, 'Invalid image path');
	}

	// Construct full file path
	const fullPath = path.join(IMAGES_BASE_DIR, imagePath);

	// Verify file extension
	const ext = path.extname(fullPath).toLowerCase();
	if (!ALLOWED_EXTENSIONS.has(ext)) {
		error(400, 'Invalid file type');
	}

	try {
		// Check if file exists
		await fs.access(fullPath);

		// Read file
		const fileBuffer = await fs.readFile(fullPath);

		// Determine content type based on extension
		const contentTypeMap: Record<string, string> = {
			'.jpg': 'image/jpeg',
			'.jpeg': 'image/jpeg',
			'.png': 'image/png',
			'.bmp': 'image/bmp',
			'.gif': 'image/gif',
			'.webp': 'image/webp'
		};

		const contentType = contentTypeMap[ext] || 'application/octet-stream';

		// Return image with appropriate headers
		return new Response(fileBuffer, {
			headers: {
				'Content-Type': contentType,
				'Cache-Control': 'public, max-age=31536000, immutable', // Cache for 1 year
				'Content-Length': fileBuffer.length.toString()
			}
		});
	} catch (err) {
		const errorObj = err as NodeJS.ErrnoException;
		
		if (errorObj.code === 'ENOENT') {
			error(404, 'Image not found');
		}

		console.error('[API Images Serve] Error serving image:', err);
		error(500, 'Failed to serve image');
	}
};
