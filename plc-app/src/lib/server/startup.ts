import { startTcpServer } from './tcp/tcp.server';
import { startWebSocketServer } from './ws/ws.server';
import { startImageWatcher } from './plc/image-handler';
import path from 'path';
import os from 'os';

let imageWatcherStop: (() => void) | null = null;

export async function initializeServers() {
	console.log('🚀 [Startup] Initializing servers...');

	// Start TCP Server for PLC communication
	await startTcpServer();

	// Start WebSocket Server for real-time updates
	await startWebSocketServer(4000);

	// Start Image Watcher for PLC images
	const imageWatchDir = process.env.PLC_IMAGE_DIR || path.join(os.homedir(), 'ftp', 'plc_images');
	console.log(`📸 [Startup] Initializing image watcher: ${imageWatchDir}`);
	
	try {
		// Import getCurrentLotInfo dynamically to avoid circular dependencies
		const { getCurrentLotInfo } = await import('./plc/plc-handler');
		
		// Wrap to match expected signature
		const getLotInfoForImageHandler = () => {
			const info = getCurrentLotInfo();
			if (!info) return null;
			
			// Parse modelId - handle both string and number
			const modelId = typeof info.modelId === 'string' 
				? parseInt(info.modelId, 10) 
				: info.modelId;
			
			return {
				loteId: info.loteId,
				loteName: info.loteName,
				modelId: isNaN(modelId) ? 1 : modelId // Default to 1 if invalid
			};
		};
		
		imageWatcherStop = await startImageWatcher(imageWatchDir, getLotInfoForImageHandler);
		console.log('✅ [Startup] Image watcher initialized');
	} catch (error) {
		console.error('❌ [Startup] Failed to initialize image watcher:', error);
	}

	console.log('✅ [Startup] All servers initialized successfully');
}

// Cleanup on shutdown
process.on('SIGINT', () => {
	console.log('\n🛑 [Shutdown] Stopping servers...');
	if (imageWatcherStop) {
		imageWatcherStop();
	}
	process.exit(0);
});

process.on('SIGTERM', () => {
	console.log('\n🛑 [Shutdown] Stopping servers...');
	if (imageWatcherStop) {
		imageWatcherStop();
	}
	process.exit(0);
});
