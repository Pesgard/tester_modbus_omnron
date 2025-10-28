/**
 * PLC Data Handler
 * 
 * Handles incoming PLC data, validates it, stores in database,
 * and broadcasts to connected clients via WebSocket.
 */

import { prisma } from '$lib/prisma';
import { broadcast } from '../ws/ws.server';
import { processPLCData } from './plc-parser';
import { setActiveModelId } from '../tcp/tcp.server';

/**
 * Tracks the current active lot for production
 */
let currentActiveLot: { id: string; recetaId: string; name: string } | null = null;

/**
 * Sets the active lot for receiving PLC data
 */
export function setActiveLot(loteId: string, recetaId: string, name: string) {
	currentActiveLot = { id: loteId, recetaId, name };
	console.log(`[PLC Handler] Active lot set: ${name} (${loteId})`);
	
	// Broadcast lot started event to all connected clients
	broadcast({
		type: 'lot-started',
		payload: { id: loteId, name, recetaId }
	});
}

/**
 * Gets the current active lot
 */
export function getActiveLot() {
	return currentActiveLot;
}

/**
 * Gets current lot info for image processing
 */
export function getCurrentLotInfo(): { loteId: string; loteName: string; modelId: string } | null {
	if (!currentActiveLot) return null;
	
	return {
		loteId: currentActiveLot.id,
		loteName: currentActiveLot.name,
		modelId: currentActiveLot.recetaId
	};
}

/**
 * Clears the active lot
 */
export function clearActiveLot() {
	const previousLot = currentActiveLot;
	console.log('[PLC Handler] Active lot cleared');
	currentActiveLot = null;
	
	// Stop sending model_id to PLC
	setActiveModelId(null);
	
	// Broadcast lot stopped event
	if (previousLot) {
		broadcast({
			type: 'lot-stopped',
			payload: { id: previousLot.id, name: previousLot.name }
		});
	}
}

/**
 * Processes incoming PLC data packet
 */
export async function handlePLCData(rawData: number[]): Promise<void> {
	try {
		// Parse and validate the packet
		const parsed = processPLCData(rawData);

		if (!parsed) {
			console.error('[PLC Handler] Failed to parse PLC data');
			return;
		}

		// Broadcast raw data immediately to all connected clients
		broadcast({
			type: 'plc-data',
			payload: {
				...parsed,
				hasActiveLot: !!currentActiveLot
			}
		});

		// Only store in database if we have an active lot and data is valid
		if (!currentActiveLot) {
			console.warn('[PLC Handler] No active lot, data not persisted');
			return;
		}

		if (!parsed.isValid) {
			console.warn('[PLC Handler] Invalid data (ready flag = 0), not persisted');
			return;
		}

		// Validate model matches the recipe
		const lote = await prisma.lote.findUnique({
			where: { id: currentActiveLot.id },
			include: { receta: true }
		});

		if (!lote) {
			console.error('[PLC Handler] Active lot not found in database');
			clearActiveLot();
			return;
		}

		// Check if lot is still open
		if (lote.estado !== 'OPEN') {
			console.warn(`[PLC Handler] Lot ${lote.name} is ${lote.estado}, cannot add pieces`);
			return;
		}

	// Create piece record
	const nextIndex = lote.piezas_ok + lote.piezas_fallas + 1;
	const isOK = parsed.pieceStatus === 'OK' && parsed.failureType === 'Sin falla';
	const failureCode = parsed.rawData[2]; // Index 2 is failure_code

	const pieza = await prisma.pieza.create({
		data: {
			lote_id: lote.id,
			resultado_bits: parsed.rawData,
			ok: isOK,
			indice: nextIndex,
			imagen_path: '', // Empty string initially, will be updated when image is received
			processed_at: parsed.timestamp
		}
	});

		// Update lot counters
		await prisma.lote.update({
			where: { id: lote.id },
			data: {
				piezas_ok: isOK ? { increment: 1 } : undefined,
				piezas_fallas: !isOK ? { increment: 1 } : undefined
			}
		});

		// Create history entry
		await prisma.historial.create({
			data: {
				lote_id: lote.id,
				pieza_id: pieza.id,
				user_id: lote.created_by, // System user or operator
				action_key: isOK ? 'pieza.procesada.ok' : 'pieza.procesada.nok',
				meta: {
					...parsed,
					piezaIndex: nextIndex
				}
			}
		});

	// If there's a failure, prepare to receive image
	if (failureCode > 0 && !isOK) {
		console.log(`📸 [PLC Handler] Failure detected (code: ${failureCode}). Expecting image for piece ${nextIndex}`);
		
		// Store pending image info (the actual image will be processed by image-handler)
		// The image watcher will automatically process incoming images
		broadcast({
			type: 'awaiting-image',
			payload: {
				loteId: lote.id,
				loteName: lote.name,
				piezaId: pieza.id,
				piezaIndex: nextIndex,
				modelId: parsed.modelId,
				failureCode,
				failureType: parsed.failureType
			}
		});
	}

	// Broadcast piece created event
	broadcast({
		type: 'piece-created',
		payload: {
			loteId: lote.id,
			loteName: lote.name,
			piezaId: pieza.id,
			index: nextIndex,
			ok: isOK,
			failureCode,
			hasImage: failureCode > 0 && !isOK,
			parsed
		}
	});

		// Check if lot should be auto-closed
		if (lote.piezas_ok + (isOK ? 1 : 0) >= lote.max_piezas_ok) {
			await prisma.lote.update({
				where: { id: lote.id },
				data: {
					estado: 'CLOSED',
					closed_at: new Date()
				}
			});

			broadcast({
				type: 'lot-completed',
				payload: {
					loteId: lote.id,
					loteName: lote.name,
					piezasOk: lote.piezas_ok + (isOK ? 1 : 0),
					piezasFallas: lote.piezas_fallas + (!isOK ? 1 : 0)
				}
			});

			clearActiveLot();
			console.log(`[PLC Handler] Lot ${lote.name} auto-closed (reached max_piezas_ok)`);
		}

		console.log(
			`[PLC Handler] Piece ${nextIndex} ${isOK ? 'OK' : 'NOK'} added to lot ${lote.name}`
		);
	} catch (error) {
		console.error('[PLC Handler] Error handling PLC data:', error);
		
		// Broadcast error to clients
		broadcast({
			type: 'plc-error',
			payload: {
				error: error instanceof Error ? error.message : 'Unknown error',
				timestamp: new Date()
			}
		});
	}
}

/**
 * Gets current line status
 */
export async function getLineStatus() {
	if (!currentActiveLot) {
		return {
			status: 'idle',
			message: 'No active lot'
		};
	}

	const lote = await prisma.lote.findUnique({
		where: { id: currentActiveLot.id },
		include: {
			receta: true,
			piezas: {
				orderBy: { processed_at: 'desc' },
				take: 1
			}
		}
	});

	if (!lote) {
		return {
			status: 'error',
			message: 'Active lot not found'
		};
	}

	return {
		status: 'active',
		lote: {
			id: lote.id,
			name: lote.name,
			receta: lote.receta,
			piezasOk: lote.piezas_ok,
			piezasFallas: lote.piezas_fallas,
			maxPiezasOk: lote.max_piezas_ok,
			progress: (lote.piezas_ok / lote.max_piezas_ok) * 100,
			lastPiece: lote.piezas[0] || null
		}
	};
}

