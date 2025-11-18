/**
 * PLC Image Handler
 *
 * Handles image reception via FTP/SFTP, stores them temporarily until the
 * PLC data arrives, and exposes helpers to move/link them once the piece
 * information is available.
 */

import fs from 'fs/promises';
import path from 'path';
import { randomUUID } from 'crypto';
import type { PendingImage } from '@prisma/client';
import { prisma } from '$lib/prisma';
import { broadcast } from '../ws/ws.server';
import { imageBufferService, ImageBufferService } from './image-buffer.service';

const IMAGE_EXTENSIONS = new Set(['.jpg', '.jpeg', '.png', '.bmp']);
const LOT_IMAGES_BASE_DIR =
	process.env.IMAGES_DIR || path.join(process.cwd(), 'static', 'images', 'lotes');
const PENDING_IMAGES_DIR =
	process.env.PENDING_IMAGES_DIR || path.join(process.cwd(), 'static', 'images', 'pending');
const STATIC_BASE_DIR = path.join(process.cwd(), 'static');

async function ensureDirectory(dirPath: string): Promise<void> {
	try {
		await fs.access(dirPath);
	} catch {
		await fs.mkdir(dirPath, { recursive: true });
		console.log(`📁 [Image Handler] Created directory: ${dirPath}`);
	}
}

function convertToPublicPath(absolutePath: string): string {
	const relative = path.relative(STATIC_BASE_DIR, absolutePath);
	return `/${relative.split(path.sep).join('/')}`;
}

function extractTimestampFromFilename(filename: string, fallback: Date): Date {
	const numericMs = filename.match(/(\d{13,})/);
	if (numericMs) {
		const value = parseInt(numericMs[1], 10);
		const date = new Date(value);
		if (!Number.isNaN(date.getTime())) {
			return date;
		}
	}

	const numericSeconds = filename.match(/(\d{10})/);
	if (numericSeconds) {
		const value = parseInt(numericSeconds[1], 10);
		const date = new Date(value * 1000);
		if (!Number.isNaN(date.getTime())) {
			return date;
		}
	}

	const isoLike = filename.match(
		/(\d{4})[-_]?(\d{2})[-_]?(\d{2})[T_\- ]?(\d{2})[-_]?(\d{2})[-_]?(\d{2})/
	);
	if (isoLike) {
		const [year, month, day, hour, minute, second] = isoLike
			.slice(1)
			.map((part) => parseInt(part, 10));
		const date = new Date(year, month - 1, day, hour, minute, second);
		if (!Number.isNaN(date.getTime())) {
			return date;
		}
	}

	return fallback;
}

function generatePendingFilename(timestamp: Date, ext: string): string {
	const safeExt = ext ? (ext.startsWith('.') ? ext : `.${ext}`) : '.jpg';
	return `pending_${timestamp.getTime()}_${randomUUID()}${safeExt.toLowerCase()}`;
}

export function generateFinalImageFilename(
	modelId: number,
	failureCode: number,
	timestamp: Date,
	sequence = 0,
	ext = '.jpg'
): string {
	const ts = timestamp.getTime();
	const dateStr = timestamp.toISOString().replace(/[:.]/g, '-').slice(0, 19);
	const suffix = sequence > 0 ? `_img${sequence + 1}` : '';
	const safeExt = ext.startsWith('.') ? ext : `.${ext}`;
	return `${modelId}_${failureCode}_${ts}${suffix}_${dateStr}${safeExt.toLowerCase()}`;
}

export async function finalizePendingImage(
	pendingImage: PendingImage,
	loteName: string,
	filename: string
) {
	const lotDirectory = path.join(LOT_IMAGES_BASE_DIR, loteName);
	await ensureDirectory(lotDirectory);

	const destination = path.join(lotDirectory, filename);

	try {
		await fs.rename(pendingImage.finalPath, destination);
	} catch (error) {
		const err = error as NodeJS.ErrnoException;
		if (err.code === 'EXDEV') {
			await fs.copyFile(pendingImage.finalPath, destination);
			await fs.unlink(pendingImage.finalPath);
		} else {
			throw error;
		}
	}

	return {
		absolutePath: destination,
		publicPath: convertToPublicPath(destination)
	};
}

export async function handleIncomingImage(
	filePath: string,
	buffer: ImageBufferService = imageBufferService
) {
	const extension = path.extname(filePath).toLowerCase();

	if (!IMAGE_EXTENSIONS.has(extension)) {
		console.log(`[Image Watcher] Ignoring non-image file: ${path.basename(filePath)}`);
		return null;
	}

	const stats = await fs.stat(filePath);
	const fallbackTimestamp =
		stats.birthtimeMs && !Number.isNaN(stats.birthtimeMs)
			? new Date(stats.birthtimeMs)
			: new Date();
	const timestamp = extractTimestampFromFilename(path.basename(filePath), fallbackTimestamp);

	await ensureDirectory(PENDING_IMAGES_DIR);
	const newFilename = generatePendingFilename(timestamp, extension || '.jpg');
	const finalPath = path.join(PENDING_IMAGES_DIR, newFilename);

	try {
		await fs.rename(filePath, finalPath);
	} catch (error) {
		const err = error as NodeJS.ErrnoException;
		if (err.code === 'EXDEV') {
			await fs.copyFile(filePath, finalPath);
			await fs.unlink(filePath);
		} else {
			throw error;
		}
	}

	const record = await buffer.savePendingImage({
		timestamp,
		filename: newFilename,
		finalPath,
		size: stats.size
	});

	console.log(
		`🗂️ [Image Handler] Buffered image ${record.filename} at ${record.timestamp.toISOString()}`
	);

	broadcast({
		type: 'pending-image-buffered',
		payload: {
			id: record.id,
			filename: record.filename,
			size: record.size,
			timestamp: record.timestamp.toISOString()
		}
	});

	return record;
}

export async function startImageWatcher(watchDirectory: string): Promise<() => void> {
	await ensureDirectory(watchDirectory);
	await ensureDirectory(PENDING_IMAGES_DIR);

	const chokidar = await import('chokidar');
	const watcher = chokidar.watch(watchDirectory, {
		ignoreInitial: true,
		persistent: true,
		awaitWriteFinish: {
			stabilityThreshold: 2000,
			pollInterval: 100
		}
	});

	watcher.on('add', async (filePath: string) => {
		try {
			await handleIncomingImage(filePath);
		} catch (error) {
			console.error('[Image Watcher] Failed to buffer image:', error);
			broadcast({
				type: 'image-error',
				payload: {
					error: error instanceof Error ? error.message : 'Unknown error',
					originalPath: filePath,
					timestamp: new Date().toISOString()
				}
			});
		}
	});

	console.log(`👁️ [Image Watcher] Started watching: ${watchDirectory}`);

	return () => {
		watcher.close();
		console.log('[Image Watcher] Stopped');
	};
}

/**
 * Gets all images for a specific lot
 */
export async function getLotImages(loteId: string) {
	return prisma.imagen.findMany({
		where: {
			lote_id: loteId
		},
		orderBy: { uploaded_at: 'desc' }
	});
}

/**
 * Gets all images for a specific failure type
 */
export async function getImagesByFailureType(loteId: string, failureCode: number) {
	const failureType = getFailureTypeName(failureCode);

	return prisma.imagen.findMany({
		where: {
			lote_id: loteId,
			tipo_falla: failureType
		},
		orderBy: { uploaded_at: 'desc' }
	});
}

/**
 * Converts failure code to failure type name
 */
function getFailureTypeName(failureCode: number): string {
	const failureTypes: Record<number, string> = {
		0: 'Sin falla',
		1: 'Test hipot falla',
		2: 'Etiqueta incorrecta',
		3: 'Modelo incorrecto',
		4: 'Terminal incorrecta',
		99: 'Falla desconocida'
	};

	return failureTypes[failureCode] || 'Falla desconocida';
}
