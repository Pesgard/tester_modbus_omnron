// src/hooks.server.ts
import type { Handle } from '@sveltejs/kit';
import net from 'net';
import { startWebSocketServer } from '$lib/ws.server';

const ws = startWebSocketServer(4000); // Puerto local WebSocket

let started = false;

export const handle: Handle = async ({ event, resolve }) => {
	if (!started) {
		started = true;

		const HOST = '0.0.0.0';
		const PORT = 900;
		const HEARTBEAT_INTERVAL = 1000;

		const server = net.createServer((socket) => {
			console.log(`Conexión aceptada de ${socket.remoteAddress}:${socket.remotePort}`);
			socket.setKeepAlive(true, 1000);

			const sendHeartbeat = () => {
				if (socket.writable) {
					const heartbeatData = Buffer.from([0xFF]);
					socket.write(heartbeatData);
					console.log('❤️  Heartbeat enviado al PLC');
				}
			};

			const heartbeatInterval = setInterval(sendHeartbeat, HEARTBEAT_INTERVAL);

			socket.on('data', (data) => {
				const bytes = Array.from(data);
				console.log('📥 Datos recibidos:', bytes);

				// ✅ Aquí envías a todos los clientes conectados por WebSocket
				ws.broadcast({ type: 'tcp-data', payload: bytes });
			});

			socket.on('end', () => clearInterval(heartbeatInterval));
			socket.on('error', () => clearInterval(heartbeatInterval));
			socket.on('close', () => clearInterval(heartbeatInterval));
		});

		server.listen(PORT, HOST, () => {
			console.log(`🚀 Servidor TCP escuchando en ${HOST}:${PORT}`);
		});

		process.on('SIGINT', () => {
			server.close(() => process.exit(0));
		});
		process.on('SIGTERM', () => {
			server.close(() => process.exit(0));
		});
	}

	return resolve(event);
};
