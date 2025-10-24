// src/lib/server/tcp/tcp.server.ts
import net from 'net';
import { handlePLCData } from '../plc/plc-handler';

export function startTcpServer() {
	const HOST = '0.0.0.0';
	const PORT = 900;
	const HEARTBEAT_INTERVAL = 1000;

	const server = net.createServer((socket) => {
		console.log(`🔌 Cliente TCP conectado: ${socket.remoteAddress}:${socket.remotePort}`);
		socket.setKeepAlive(true, HEARTBEAT_INTERVAL);

		const sendHeartbeat = () => {
			if (socket.writable) {
				socket.write(Buffer.from([0xFF]));
				console.log('❤️ Heartbeat enviado al PLC');
			}
		};
		const heartbeatInterval = setInterval(sendHeartbeat, HEARTBEAT_INTERVAL);

		socket.on('data', async (data) => {
			const bytes = Array.from(data);
			console.log('📥 Datos PLC recibidos:', bytes);
			
			// Process the PLC data through the handler
			await handlePLCData(bytes);
		});

		const cleanup = () => clearInterval(heartbeatInterval);
		socket.on('end', cleanup);
		socket.on('error', (err) => {
			console.error('❌ Error TCP:', err);
			cleanup();
		});
		socket.on('close', () => {
			console.log('🔌 Cliente TCP desconectado');
			cleanup();
		});
	});

	server.listen(PORT, HOST, () => {
		console.log(`🚀 Servidor TCP escuchando en ${HOST}:${PORT}`);
	});

	return server;
}


