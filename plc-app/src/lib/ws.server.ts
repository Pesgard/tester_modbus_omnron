// src/lib/ws.server.ts
import { WebSocketServer } from 'ws';

const clients = new Set<WebSocket>();

export function startWebSocketServer(port = 4000) {
	const wss = new WebSocketServer({ port });

	wss.on('connection', (ws) => {
		console.log('🟢 Cliente WebSocket conectado');
		clients.add(ws);

		ws.on('close', () => {
			console.log('🔴 Cliente WebSocket desconectado');
			clients.delete(ws);
		});
	});

	return {
		broadcast: (data: any) => {
			const json = JSON.stringify(data);
			for (const client of clients) {
				if (client.readyState === client.OPEN) {
					client.send(json);
				}
			}
		}
	};
}
