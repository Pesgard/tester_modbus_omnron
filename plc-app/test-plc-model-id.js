/**
 * Test PLC Client - Model ID Receiver
 * 
 * This script simulates a PLC that:
 * 1. Connects to the backend TCP server (port 900)
 * 2. Receives the model_id byte when a lot is selected
 * 3. Configures itself based on the model_id
 * 4. Sends a test piece with the correct model_id back to the backend
 */

import net from 'net'

const client = net.createConnection({ port: 900, host: 'localhost' }, () => {
  console.log('✅ [TEST PLC] Conectado al backend (puerto 900)');
  console.log('⏳ Esperando recibir model_id del backend...\n');
  console.log('💡 Desde el navegador: Dashboard → Production → Seleccionar un lote\n');
});

let currentModelId = 0;

client.on('data', (data) => {
  const bytes = Array.from(data);
  
  // Filtrar heartbeats (0xFF)
  if (bytes.length === 1 && bytes[0] === 0xFF) {
    process.stdout.write('💚'); // Heartbeat visual (sin salto de línea)
    return;
  }
  
  // Recibir model_id (SOLO 1 BYTE)
  if (bytes.length === 1 && bytes[0] >= 1 && bytes[0] <= 7) {
    const modelId = bytes[0];
    currentModelId = modelId;
    
    console.log(`\n\n${'='.repeat(50)}`);
    console.log(`📥 MODEL ID RECIBIDO: ${modelId} (1 byte: 0x${modelId.toString(16).padStart(2, '0').toUpperCase()})`);
    console.log('='.repeat(50));
    
    // Configurar PLC según model_id
    const config = getModelConfig(modelId);
    console.log(`\n🔧 Configurando PLC para modelo ${modelId}:`);
    console.log(`   📋 PPN: ${config.ppn}`);
    console.log(`   🔌 L1 Terminal: ${config.l1}`);
    console.log(`   🔌 L2 Terminal: ${config.l2}`);
    console.log(`   📊 Conductores: ${config.conductores}`);
    
    if (config.special) {
      console.log(`   ⚠️  NOTA ESPECIAL: ${config.special}`);
    }
    
    console.log(`\n✅ PLC listo para procesar piezas del modelo ${modelId}\n`);
    
    // Simular envío de pieza de prueba después de 2 segundos
    console.log('⏳ Enviando pieza de prueba en 2 segundos...\n');
    setTimeout(() => {
      sendTestPiece(modelId, config);
    }, 2000);
  } else {
    console.log(`\n⚠️ [TEST PLC] Byte recibido desconocido: ${bytes}`);
  }
});

client.on('error', (err) => {
  console.error('\n❌ [TEST PLC] Error de conexión:', err.message);
  console.error('💡 Asegúrate de que el backend esté corriendo en puerto 900\n');
});

client.on('close', () => {
  console.log('\n🔌 [TEST PLC] Conexión cerrada');
  process.exit(0);
});

/**
 * Retorna la configuración del modelo según el model_id
 */
function getModelConfig(modelId) {
  const configs = {
    1: { ppn: '1020746', l1: 'Ferrul', l2: 'Ferrul', conductores: 5 },
    2: { ppn: '1020746-02', l1: 'Ferrul', l2: 'Ferrul', conductores: 5 },
    3: { ppn: '1020747', l1: 'Ferrul', l2: 'Ferrul', conductores: 5 },
    4: { ppn: '683950001', l1: 'Terminal', l2: 'Ferrul', conductores: 5, special: 'L1 usa Terminal en lugar de Ferrul' },
    5: { ppn: '694030001', l1: 'Terminal', l2: 'Ferrul', conductores: 5, special: 'L1 usa Terminal en lugar de Ferrul' },
    6: { ppn: '717140001', l1: 'Ferrul', l2: 'Ferrul', conductores: 5 },
    7: { ppn: '698330001', l1: 'Ferrul', l2: 'Ferrul', conductores: 4, special: 'Solo 4 conductores (sin N)' }
  };
  
  return configs[modelId] || { 
    ppn: 'Unknown', 
    l1: 'Unknown', 
    l2: 'Unknown', 
    conductores: 0,
    special: 'Model ID no reconocido'
  };
}

/**
 * Simula el envío de una pieza de prueba al backend
 */
function sendTestPiece(modelId, config) {
  console.log(`${'='.repeat(50)}`);
  console.log(`📤 ENVIANDO PIEZA DE PRUEBA`);
  console.log('='.repeat(50));
  
  // Construir array de prueba según el formato del contrato
  // [line_status, piece_status, failure_code, model_id, L1_terminal, L2_terminal, hipot_test, label_ok]
  
  const l1Value = config.l1 === 'Terminal' ? 1 : 0; // 0=Ferrul, 1=Terminal
  
  const testPiece = [
    1,        // [0] line_status: 1 = ON
    1,        // [1] piece_status: 1 = OK
    0,        // [2] failure_code: 0 = Sin falla
    modelId,  // [3] model_id: el que recibimos del backend
    l1Value,  // [4] L1_terminal_type: según config
    0,        // [5] L2_terminal_type: 0 = Ferrul (siempre)
    1,        // [6] hipot_test: 1 = OK
    0         // [7] label_ok: 0 = OK
  ];
  
  console.log(`\n📊 Array construido:`);
  console.log(`   Índices: [0,  1,  2,  3,  4,  5,  6,  7]`);
  console.log(`   Valores: [${testPiece.join(', ')}]`);
  console.log(`\n📋 Interpretación:`);
  console.log(`   [0] Line Status: ON`);
  console.log(`   [1] Piece Status: OK`);
  console.log(`   [2] Failure Code: Sin falla`);
  console.log(`   [3] Model ID: ${modelId} (${config.ppn})`);
  console.log(`   [4] L1: ${config.l1}`);
  console.log(`   [5] L2: ${config.l2}`);
  console.log(`   [6] Hipot: OK`);
  console.log(`   [7] Label: OK`);
  
  // Enviar como JSON
  const jsonData = JSON.stringify(testPiece);
  client.write(jsonData);
  
  console.log(`\n✅ [TEST PLC] Pieza enviada al backend!`);
  console.log(`   Formato JSON: ${jsonData}`);
  console.log(`\n💡 Verifica en el Dashboard → Production que la pieza aparezca\n`);
}

// Manejar Ctrl+C para cerrar limpiamente
process.on('SIGINT', () => {
  console.log('\n\n👋 [TEST PLC] Cerrando conexión...');
  client.end();
  setTimeout(() => process.exit(0), 500);
});

console.log(`
╔════════════════════════════════════════════════════════════╗
║        TEST PLC CLIENT - MODEL ID RECEIVER                 ║
╚════════════════════════════════════════════════════════════╝

🎯 Propósito:
   - Simular un PLC que recibe model_id del backend
   - Configurar validaciones según model_id
   - Enviar pieza de prueba con model_id correcto

📡 Protocolo:
   - Conecta a: localhost:900 (TCP)
   - Recibe: SOLO 1 BYTE (0x01 - 0x07) ← ¡IMPORTANTE!
   - Envía: Array JSON de 8 enteros

💡 Instrucciones:
   1. Asegúrate de que el backend esté corriendo (npm run dev)
   2. Desde el navegador, ve a Dashboard → Production
   3. Selecciona cualquier lote disponible
   4. Este script recibirá el model_id (1 byte) y enviará una pieza de prueba

🚀 Esperando conexión...

`);

