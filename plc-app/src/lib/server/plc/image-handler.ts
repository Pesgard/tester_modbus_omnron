/**
 * PLC Image Handler
 * 
 * Handles image reception, renaming, and organization when the PLC
 * detects a failure (failureCode > 0).
 */

import fs from 'fs/promises';
import path from 'path';
import { prisma } from '$lib/prisma';
import { broadcast } from '../ws/ws.server';

export interface ImageMetadata {
	originalPath: string;
	finalPath: string;
	filename: string;
	modelId: number;
	failureCode: number;
	timestamp: Date;
	loteId: string;
	loteName: string;
	piezaIndex: number;
	fileSize: number;
}

/**
 * Base directory for storing images
 */
const IMAGES_BASE_DIR = process.env.IMAGES_DIR || path.join(process.cwd(), 'static', 'images', 'lotes');

/**
 * Ensures the directory exists, creates it if not
 */
async function ensureDirectory(dirPath: string): Promise<void> {
	try {
		await fs.access(dirPath);
	} catch {
		await fs.mkdir(dirPath, { recursive: true });
		console.log(`📁 [Image Handler] Created directory: ${dirPath}`);
	}
}

/**
 * Generates the new filename according to the pattern:
 * <model_id>_<failureCode>_<timestamp>.jpg
 */
function generateFilename(modelId: number, failureCode: number, timestamp: Date): string {
	const ts = timestamp.getTime();
	const dateStr = timestamp.toISOString().replace(/[:.]/g, '-').slice(0, 19);
	return `${modelId}_${failureCode}_${ts}_${dateStr}.jpg`;
}

/**
 * Gets the lot-specific directory path
 */
function getLotDirectory(loteName: string): string {
	return path.join(IMAGES_BASE_DIR, loteName);
}

/**
 * Processes an image file from the PLC:
 * 1. Validates the file exists
 * 2. Generates new filename
 * 3. Creates lot directory if needed
 * 4. Moves and renames the file
 * 5. Updates database
 * 6. Broadcasts event
 */
export async function processPlcImage(
	originalPath: string,
	modelId: number,
	failureCode: number,
	loteId: string,
	loteName: string,
	piezaIndex: number
): Promise<ImageMetadata | null> {
	try {
		// Check if file exists
		const fileStats = await fs.stat(originalPath);
		if (!fileStats.isFile()) {
			console.error(`[Image Handler] Path is not a file: ${originalPath}`);
			return null;
		}

		// Generate new filename and paths
		const timestamp = new Date();
		const newFilename = generateFilename(modelId, failureCode, timestamp);
		const lotDirectory = getLotDirectory(loteName);
		const finalPath = path.join(lotDirectory, newFilename);

		// Ensure lot directory exists
		await ensureDirectory(lotDirectory);

		// Move and rename the file
		await fs.rename(originalPath, finalPath);
		
		console.log(`📸 [Image Handler] Image processed:`);
		console.log(`   Original: ${originalPath}`);
		console.log(`   New: ${finalPath}`);
		console.log(`   Model ID: ${modelId}, Failure Code: ${failureCode}`);

		const metadata: ImageMetadata = {
			originalPath,
			finalPath,
			filename: newFilename,
			modelId,
			failureCode,
			timestamp,
			loteId,
			loteName,
			piezaIndex,
			fileSize: fileStats.size
		};

		// Update piece record with image path
		await prisma.pieza.updateMany({
			where: {
				lote_id: loteId,
				indice: piezaIndex
			},
			data: {
				imagen_path: `/images/lotes/${loteName}/${newFilename}`
			}
		});

		// Create image record
		await prisma.imagen.create({
			data: {
				lote_id: loteId,
				path: `/images/lotes/${loteName}/${newFilename}`,
				tipo_falla: getFailureTypeName(failureCode),
				thumbnail_path: '',
				metadata: {
					originalPath,
					filename: newFilename,
					modelId,
					failureCode,
					piezaIndex,
					fileSize: fileStats.size
				}
			}
		});

		// Broadcast image processed event with all necessary data for modal
		broadcast({
			type: 'image-processed',
			payload: {
				loteId,
				loteName,
				piezaIndex,
				modelId,
				failureCode,
				imagePath: `/images/lotes/${loteName}/${newFilename}`,
				timestamp: timestamp.toISOString()
			}
		});

		return metadata;
	} catch (error) {
		console.error('[Image Handler] Error processing image:', error);
		console.error(`   Original path: ${originalPath}`);
		
		// Broadcast error
		broadcast({
			type: 'image-error',
			payload: {
				error: error instanceof Error ? error.message : 'Unknown error',
				originalPath,
				loteId,
				timestamp: new Date().toISOString()
			}
		});

		return null;
	}
}

/**
 * Watches a directory for new images and processes them automatically
 * Returns a function to stop watching
 */
export async function startImageWatcher(
	watchDirectory: string,
	getCurrentLotInfo: () => { loteId: string; loteName: string; modelId: number } | null
): Promise<() => void> {
	// Ensure watch directory exists
	await ensureDirectory(watchDirectory);

	// Use chokidar for watching (needs to be installed: npm install chokidar)
	const chokidar = await import('chokidar');
	
	const watcher = chokidar.watch(watchDirectory, {
		ignoreInitial: true,
		persistent: true,
		awaitWriteFinish: {
			stabilityThreshold: 2000, // Wait 2 seconds for file to be fully written
			pollInterval: 100
		}
	});

	watcher.on('add', async (filePath: string) => {
		const ext = path.extname(filePath).toLowerCase();
		
		// Only process image files
		if (!['.jpg', '.jpeg', '.png', '.bmp'].includes(ext)) {
			console.log(`[Image Watcher] Ignoring non-image file: ${path.basename(filePath)}`);
			return;
		}

		console.log(`📸 [Image Watcher] New image detected: ${path.basename(filePath)}`);

		const lotInfo = getCurrentLotInfo();
		if (!lotInfo) {
			console.warn('[Image Watcher] No active lot, cannot process image');
			return;
		}

		// Try to extract failure code from filename (e.g., "error_2_12345.jpg")
		const filename = path.basename(filePath, ext);
		const failureMatch = filename.match(/error[_-]?(\d+)/i);
		const failureCode = failureMatch ? parseInt(failureMatch[1]) : 1; // Default to 1 if not found

		// Get next piece index (or use current count + 1)
		const lote = await prisma.lote.findUnique({
			where: { id: lotInfo.loteId },
			select: { piezas_ok: true, piezas_fallas: true }
		});

		const piezaIndex = lote ? lote.piezas_ok + lote.piezas_fallas : 0;

		// Process the image
		await processPlcImage(
			filePath,
			lotInfo.modelId,
			failureCode,
			lotInfo.loteId,
			lotInfo.loteName,
			piezaIndex
		);
	});

	console.log(`👁️ [Image Watcher] Started watching: ${watchDirectory}`);

	// Return stop function
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

