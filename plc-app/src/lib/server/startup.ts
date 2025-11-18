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
		imageWatcherStop = await startImageWatcher(imageWatchDir);
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
