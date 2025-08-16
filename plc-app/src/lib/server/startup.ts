// src/lib/server/startup.ts
import { startWebSocketServer } from './ws.server';
import { startTcpServer } from './tcp.server';
import { startFtpWatcher } from './ftp-image-watcher.server';

let started = false;

export function startServices() {
	if (started) return;
	started = true;

	startWebSocketServer(4000);
	startTcpServer();
	// Ejemplo 2: Configuración personalizada para control de calidad
	startFtpWatcher({
		directorioDestino: 'C:/control-calidad/imagenes',
		prefijoId: 'QC', // Quality Control
		formatoNombre: 'lote-pieza', // Genera nombres como QC_L001_P005_2024-08-13-14-30-22.jpg
		organizarPorFecha: true,
		organizarPorTipo: true
	});
	console.log('✅ Todos los servicios iniciados');
}
