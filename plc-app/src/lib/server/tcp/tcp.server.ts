// src/lib/server/tcp.service.ts
import net from 'net';
import { broadcast } from '../ws/ws.server';


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

		socket.on('data', (data) => {
			const bytes = Array.from(data);
			console.log('📥 Datos PLC:', bytes);
			broadcast({ type: 'tcp-data', payload: bytes });
		});

		const cleanup = () => clearInterval(heartbeatInterval);
		socket.on('end', cleanup);
		socket.on('error', cleanup);
		socket.on('close', cleanup);
	});

	server.listen(PORT, HOST, () => {
		console.log(`🚀 Servidor TCP escuchando en ${HOST}:${PORT}`);
	});

	return server;
}


