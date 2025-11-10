// src/lib/server/ws.service.ts
import { WebSocketServer } from 'ws';

let wss: WebSocketServer;

export function startWebSocketServer(port: number) {
	if (wss) return wss; // Evita reiniciar si ya existe

	wss = new WebSocketServer({ port });
	console.log(`🌐 WebSocket server escuchando en puerto ${port}`);

	wss.on('connection', (socket) => {
		console.log('🖥 Cliente WS conectado');
		socket.on('close', () => console.log('🖥 Cliente WS desconectado'));
	});

	return wss;
}

export function broadcast(message: any) {
	if (!wss) return;
	const data = JSON.stringify(message);
	wss.clients.forEach((client) => {
		if (client.readyState === 1) {
			client.send(data);
		}
	});
}
