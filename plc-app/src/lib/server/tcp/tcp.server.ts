// src/lib/server/tcp/tcp.server.ts
import net from 'net';
import { handlePLCData } from '../plc/plc-handler';

/**
 * Tracks all connected PLC clients
 * Map: clientId -> Socket
 */
const connectedClients = new Map<string, net.Socket>();

/**
 * Current active model_id to send periodically
 * null when no production is active
 */
let currentModelId: number | null = null;

export function startTcpServer() {
	const HOST = '0.0.0.0';
	const PORT = 900;
	const HEARTBEAT_INTERVAL = 1000; // 1 segundo
	const MODEL_ID_INTERVAL = 2000;  // 2 segundos

	const server = net.createServer((socket) => {
		const clientId = `${socket.remoteAddress}:${socket.remotePort}`;
		console.log(`🔌 Cliente TCP conectado: ${clientId}`);
		
		// Track this client
		connectedClients.set(clientId, socket);
		socket.setKeepAlive(true, HEARTBEAT_INTERVAL);

		// Heartbeat interval (0xFF)
		const sendHeartbeat = () => {
			if (socket.writable) {
				socket.write(Buffer.from([0xFF]));
				// console.log('❤️ Heartbeat enviado al PLC');
			}
		};
		const heartbeatInterval = setInterval(sendHeartbeat, HEARTBEAT_INTERVAL);

		// Model ID periodic send interval
		const sendModelIdPeriodic = () => {
			if (socket.writable && currentModelId !== null) {
				socket.write(Buffer.from([currentModelId]));
				console.log(`📤 [Periodic] Model ID ${currentModelId} enviado a ${clientId}`);
			}
		};
		const modelIdInterval = setInterval(sendModelIdPeriodic, MODEL_ID_INTERVAL);

		// Send model_id immediately if production is active
		if (currentModelId !== null) {
			console.log(`🔄 [Reconnect] Enviando model_id actual (${currentModelId}) al nuevo cliente`);
			if (socket.writable) {
				socket.write(Buffer.from([currentModelId]));
			}
		}

		socket.on('data', async (data) => {
			const bytes = Array.from(data);
			console.log('📥 Datos PLC recibidos:', bytes);
			
			// Process the PLC data through the handler
			await handlePLCData(bytes);
		});

		const cleanup = () => {
			clearInterval(heartbeatInterval);
			clearInterval(modelIdInterval);
			connectedClients.delete(clientId);
		};
		
		socket.on('end', cleanup);
		socket.on('error', (err) => {
			console.error('❌ Error TCP:', err);
			cleanup();
		});
		socket.on('close', () => {
			console.log(`🔌 Cliente TCP desconectado: ${clientId}`);
			cleanup();
		});
	});

	server.listen(PORT, HOST, () => {
		console.log(`🚀 Servidor TCP escuchando en ${HOST}:${PORT}`);
	});

	return server;
}

/**
 * Sets the active model_id to be sent periodically to all connected PLCs
 * This is called when a lot is selected for production
 * The model_id will be sent every 2 seconds until production stops
 * 
 * @param modelId - The model_id (1-7) from the selected recipe, or null to stop sending
 */
export function setActiveModelId(modelId: number | null): void {
	if (modelId !== null && (modelId < 1 || modelId > 7)) {
		console.error(`❌ [TCP] Invalid model_id: ${modelId}. Must be between 1-7`);
		return;
	}

	const previousModelId = currentModelId;
	currentModelId = modelId;

	if (modelId === null) {
		console.log(`🛑 [TCP] Model ID transmission stopped (production inactive)`);
		return;
	}

	if (previousModelId !== modelId) {
		console.log(`🔄 [TCP] Model ID changed: ${previousModelId} → ${modelId}`);
		console.log(`📡 [TCP] Sending model_id ${modelId} periodically every 2 seconds to all clients`);
		
		// Send immediately to all connected clients
		sendModelIdImmediate(modelId);
	}
}

/**
 * Sends model_id immediately to all connected clients
 * Used for immediate synchronization when lot changes
 */
function sendModelIdImmediate(modelId: number): void {
	const buffer = Buffer.from([modelId]);
	let sentCount = 0;
	let errorCount = 0;

	for (const [clientId, socket] of connectedClients.entries()) {
		try {
			if (socket.writable) {
				socket.write(buffer);
				sentCount++;
				console.log(`✅ [TCP] Model ID ${modelId} enviado inmediatamente a: ${clientId}`);
			} else {
				console.warn(`⚠️ [TCP] Socket no escribible para cliente: ${clientId}`);
				errorCount++;
			}
		} catch (error) {
			console.error(`❌ [TCP] Error enviando model_id al cliente ${clientId}:`, error);
			errorCount++;
		}
	}

	if (sentCount === 0) {
		console.warn(`⚠️ [TCP] No hay clientes conectados para recibir model_id ${modelId}`);
	} else {
		console.log(`📤 [TCP] Model ID ${modelId} enviado a ${sentCount} cliente(s). Errores: ${errorCount}`);
	}
}

/**
 * Legacy function for backward compatibility
 * Now just calls setActiveModelId
 * @deprecated Use setActiveModelId instead
 */
export function sendModelIdToPLC(modelId: number): void {
	setActiveModelId(modelId);
}


