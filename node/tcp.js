const net = require('net');

// Configuración del servidor
const HOST = '0.0.0.0';
const PORT = 900;
const HEARTBEAT_INTERVAL = 1000; // Enviar heartbeat cada 1 segundo

// Crear el servidor
const server = net.createServer((socket) => {
    console.log(`Conexión aceptada de ${socket.remoteAddress}:${socket.remotePort}`);
    
    // Configurar keepalive en el socket TCP
    socket.setKeepAlive(true, 1000);
    
    // Variable para heartbeat
    let heartbeatInterval;
    
    // Función para enviar heartbeat al PLC
    const sendHeartbeat = () => {
        if (socket.writable) {
            // Enviar un byte simple como heartbeat (0xFF)
            const heartbeatData = Buffer.from([0xFF]);
            socket.write(heartbeatData);
            console.log('❤️  Heartbeat enviado al PLC');
        }
    };
    
    // Iniciar heartbeat automático
    heartbeatInterval = setInterval(sendHeartbeat, HEARTBEAT_INTERVAL);
    
    socket.on('data', (data) => {
        console.log(`\nDatos recibidos (${data.length} bytes):`);
        
        // Procesar datos normales
        const byteArray = Array.from(data);
        console.log(`Array de bytes: [${byteArray.join(', ')}]`);
        
        // Índices y bits
        console.log('Índices y bits:');
        byteArray.forEach((byte, index) => {
            const bits = byte.toString(2).padStart(8, '0');
            console.log(`  [${index}] = ${byte} → Bits: ${bits}`);
        });
    });

    socket.on('end', () => {
        console.log('🔌 Cliente desconectado normalmente');
        if (heartbeatInterval) {
            clearInterval(heartbeatInterval);
        }
    });

    socket.on('error', (err) => {
        console.error('❌ Error en socket:', err.message);
        if (heartbeatInterval) {
            clearInterval(heartbeatInterval);
        }
    });
    
    socket.on('close', () => {
        console.log('🔒 Socket cerrado');
        if (heartbeatInterval) {
            clearInterval(heartbeatInterval);
        }
    });
});

// Iniciar el servidor
server.listen(PORT, HOST, () => {
    console.log(`🚀 Servidor TCP escuchando en ${HOST}:${PORT}...`);
    console.log(`❤️  Heartbeat configurado cada ${HEARTBEAT_INTERVAL}ms`);
});

// Manejar cierre del servidor
process.on('SIGINT', () => {
    console.log('\n🛑 Servidor detenido manualmente.');
    server.close(() => {
        process.exit(0);
    });
});

// Manejar pérdida de energía/cierre abrupto
process.on('SIGTERM', () => {
    console.log('\n⚡ Servidor terminado por el sistema.');
    server.close(() => {
        process.exit(0);
    });
});

server.on('error', (err) => {
    console.error('❌ Error del servidor:', err);
});