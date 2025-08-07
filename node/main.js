const net = require('net');

// Configuración del servidor
const HOST = '0.0.0.0';
const PORT = 900;

// Crear el servidor
const server = net.createServer((socket) => {
    console.log(`Conexión aceptada de ${socket.remoteAddress}:${socket.remotePort}`);

    socket.on('data', (data) => {
        console.log(`\nDatos recibidos (${data.length} bytes):`);
        
        // Mostrar como array de bytes individuales
        const byteArray = Array.from(data);
        console.log(`Array de bytes: [${byteArray.join(', ')}]`);
        
        // Como bits individuales
        console.log('Índices y bits:');
        byteArray.forEach((byte, index) => {
            const bits = byte.toString(2).padStart(8, '0');
            console.log(`  [${index}] = ${byte} → Bits: ${bits}`);
        });
    });

    socket.on('end', () => {
        console.log('Cliente desconectado');
    });

    socket.on('error', (err) => {
        console.error('Error en socket:', err);
    });
});

// Iniciar el servidor
server.listen(PORT, HOST, () => {
    console.log(`Servidor TCP escuchando en ${HOST}:${PORT}...`);
});

// Manejar cierre del servidor
process.on('SIGINT', () => {
    console.log('\nServidor detenido manualmente.');
    server.close(() => {
        process.exit(0);
    });
});

server.on('error', (err) => {
    console.error('Error del servidor:', err);
});