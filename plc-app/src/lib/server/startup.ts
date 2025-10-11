// src/lib/server/startup.ts
import { startWebSocketServer } from './ws/ws.server';
import { startTcpServer } from './tcp/tcp.server';
import { startFtpWatcher } from './ftp/ftp-image-watcher.server';
import path from 'path';
import os from 'os';

let started = false;

export function startServices() {
	if (started) return;
	started = true;

	startWebSocketServer(4000);
	startTcpServer();
	
	// Cross-platform directory configuration
	const baseDir = process.env.FTP_BASE_DIR || path.join(os.homedir(), 'ftp');
	const destDir = process.env.QC_DEST_DIR || path.join(os.homedir(), 'control-calidad', 'imagenes');
	
	startFtpWatcher({
		directorioDestino: destDir,
		prefijoId: 'QC', // Quality Control
		formatoNombre: 'lote-pieza', // Genera nombres como QC_L001_P005_2024-08-13-14-30-22.jpg
		organizarPorFecha: true,
		organizarPorTipo: true
	});
	console.log('✅ Todos los servicios iniciados');
}
