import { productionStore } from '$lib/stores/production';
import type { ProductionData } from '$lib/stores/production';

export interface WebSocketMessage {
	type: 'connection' | 'production_data' | 'current_data' | 'pong';
	message?: string;
	data?: ProductionData;
	timestamp: string;
}

export class ProductionWebSocket {
	private ws: WebSocket | null = null;
	private reconnectAttempts = 0;
	private maxReconnectAttempts = 5;
	private reconnectInterval = 5000; // 5 seconds
	private pingInterval: number | null = null;
	private url: string;

	constructor(url: string = 'ws://localhost:8000/ws/production') {
		this.url = url;
	}

	connect(): void {
		if (this.ws && this.ws.readyState === WebSocket.OPEN) {
			console.log('WebSocket already connected');
			return;
		}

		console.log('Connecting to WebSocket...');
		productionStore.setConnectionStatus('connecting');

		try {
			this.ws = new WebSocket(this.url);
			this.setupEventHandlers();
		} catch (error) {
			console.error('Error creating WebSocket connection:', error);
			productionStore.setConnectionStatus('disconnected');
			productionStore.setError('Failed to create WebSocket connection');
			this.scheduleReconnect();
		}
	}

	private setupEventHandlers(): void {
		if (!this.ws) return;

		this.ws.onopen = () => {
			console.log('WebSocket connected');
			productionStore.setConnectionStatus('connected');
			productionStore.setError(null);
			this.reconnectAttempts = 0;
			this.startPing();
		};

		this.ws.onmessage = (event) => {
			try {
				const message: WebSocketMessage = JSON.parse(event.data);
				this.handleMessage(message);
			} catch (error) {
				console.error('Error parsing WebSocket message:', error, event.data);
				productionStore.setError('Invalid message received from server');
			}
		};

		this.ws.onclose = (event) => {
			console.log('WebSocket disconnected:', event.code, event.reason);
			productionStore.setConnectionStatus('disconnected');
			this.stopPing();
			
			if (event.code !== 1000) { // Not a normal closure
				productionStore.setError('Connection lost to server');
				this.scheduleReconnect();
			}
		};

		this.ws.onerror = (error) => {
			console.error('WebSocket error:', error);
			productionStore.setConnectionStatus('disconnected');
			productionStore.setError('WebSocket connection error');
		};
	}

	private handleMessage(message: WebSocketMessage): void {
		console.log('Received WebSocket message:', message.type);

		switch (message.type) {
			case 'connection':
				console.log('Connection confirmed:', message.message);
				break;

			case 'production_data':
				if (message.data) {
					productionStore.setCurrentData(message.data);
					productionStore.addToHistory(message.data);
				}
				break;

			case 'current_data':
				if (message.data) {
					productionStore.setCurrentData(message.data);
				}
				break;

			case 'pong':
				console.log('Pong received from server');
				break;

			default:
				console.log('Unknown message type:', message.type);
		}
	}

	private startPing(): void {
		this.pingInterval = window.setInterval(() => {
			this.ping();
		}, 30000); // Ping every 30 seconds
	}

	private stopPing(): void {
		if (this.pingInterval) {
			clearInterval(this.pingInterval);
			this.pingInterval = null;
		}
	}

	ping(): void {
		if (this.ws && this.ws.readyState === WebSocket.OPEN) {
			const pingMessage = {
				type: 'ping',
				timestamp: new Date().toISOString()
			};
			this.ws.send(JSON.stringify(pingMessage));
			console.log('Ping sent to server');
		}
	}

	private scheduleReconnect(): void {
		if (this.reconnectAttempts < this.maxReconnectAttempts) {
			this.reconnectAttempts++;
			console.log(`Scheduling reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${this.reconnectInterval}ms`);
			
			setTimeout(() => {
				this.connect();
			}, this.reconnectInterval);
		} else {
			console.error('Max reconnect attempts reached');
			productionStore.setError('Unable to reconnect to server. Please refresh the page.');
		}
	}

	disconnect(): void {
		this.stopPing();
		
		if (this.ws) {
			this.ws.close(1000, 'Client disconnecting');
			this.ws = null;
		}
		
		productionStore.setConnectionStatus('disconnected');
	}

	isConnected(): boolean {
		return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
	}
}

// Singleton instance
let wsInstance: ProductionWebSocket | null = null;

export function getWebSocketInstance(): ProductionWebSocket {
	if (!wsInstance) {
		wsInstance = new ProductionWebSocket();
	}
	return wsInstance;
}