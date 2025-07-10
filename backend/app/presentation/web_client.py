"""
Web client HTML templates for the production system.
"""
from fastapi.responses import HTMLResponse


def get_home_page() -> HTMLResponse:
    """Get the home page HTML."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sistema de Producción</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; margin-bottom: 20px; }
            .btn { background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 10px; display: inline-block; }
            .btn:hover { background: #5a6fd8; }
            .info { background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏭 Sistema de Producción Modbus</h1>
            <div class="info">
                <p>Sistema de monitoreo en tiempo real para datos de producción via Modbus TCP</p>
            </div>
            <a href="/client" class="btn">🖥️ Abrir Monitor en Tiempo Real</a>
            <a href="/docs" class="btn">📚 Documentación API</a>
            <a href="/api/system/health" class="btn">💚 Estado del Sistema</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


def get_realtime_client() -> HTMLResponse:
    """Get the real-time monitoring client HTML."""
    html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Producción - Tiempo Real</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .status-panel {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        .connection-status {
            padding: 10px 20px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
        }
        .connected { background-color: #4CAF50; }
        .disconnected { background-color: #f44336; }
        .connecting { background-color: #ff9800; }

        .data-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }
        .data-item {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            border-left: 3px solid #28a745;
        }
        .data-label {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            font-weight: bold;
        }
        .data-value {
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin-top: 2px;
        }

        .quality-ok { color: #28a745; }
        .quality-nok { color: #dc3545; }
        .quality-pending { color: #ffc107; }

        .status-running { color: #28a745; }
        .status-stopped { color: #dc3545; }
        .status-error { color: #fd7e14; }
        .status-maintenance { color: #6f42c1; }

        .log-container {
            background: #1e1e1e;
            color: #00ff00;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            height: 200px;
            overflow-y: auto;
            margin-top: 20px;
        }

        .controls {
            text-align: center;
            margin: 20px 0;
        }
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 0 5px;
            font-size: 14px;
        }
        .btn:hover {
            background: #5a6fd8;
        }
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏭 Sistema de Producción - Monitor en Tiempo Real</h1>
            <p>Monitoreo de datos desde el servidor Modbus</p>
        </div>

        <div id="connectionStatus" class="connection-status connecting">
            🔄 Conectando al servidor...
        </div>

        <div class="controls">
            <button id="connectBtn" class="btn" onclick="connect()">Conectar</button>
            <button id="disconnectBtn" class="btn" onclick="disconnect()" disabled>Desconectar</button>
            <button class="btn" onclick="clearLog()">Limpiar Log</button>
            <button class="btn" onclick="sendPing()">Ping</button>
            <button class="btn" onclick="checkRecentData()">🔍 Diagnóstico</button>
        </div>

        <div class="status-panel">
            <div class="card">
                <h3>📊 Datos de Producción Actuales</h3>
                <div id="productionData" class="data-grid">
                    <div class="data-item">
                        <div class="data-label">Estado</div>
                        <div class="data-value">Esperando datos...</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h3>📈 Estadísticas de Sesión</h3>
                <div class="data-grid">
                    <div class="data-item">
                        <div class="data-label">Mensajes Recibidos</div>
                        <div class="data-value" id="messageCount">0</div>
                    </div>
                    <div class="data-item">
                        <div class="data-label">Productos Procesados</div>
                        <div class="data-value" id="productCount">0</div>
                    </div>
                    <div class="data-item">
                        <div class="data-label">Tiempo Conectado</div>
                        <div class="data-value" id="connectionTime">00:00:00</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card">
            <h3>📝 Log de Eventos</h3>
            <div id="log" class="log-container"></div>
        </div>
    </div>

    <script>
        let socket = null;
        let messageCount = 0;
        let productCount = 0;
        let connectionStartTime = null;
        let connectionTimer = null;

        const statusMapping = {
            0: { text: 'Detenido', class: 'status-stopped' },
            1: { text: 'En Funcionamiento', class: 'status-running' },
            2: { text: 'Error', class: 'status-error' },
            3: { text: 'Mantenimiento', class: 'status-maintenance' }
        };

        const qualityMapping = {
            0: { text: 'NOK', class: 'quality-nok' },
            1: { text: 'OK', class: 'quality-ok' },
            2: { text: 'Pendiente', class: 'quality-pending' }
        };

        function addLog(message, type = 'info') {
            const log = document.getElementById('log');
            const timestamp = new Date().toLocaleTimeString();
            const colorMap = {
                'info': '#00ff00',
                'warning': '#ffff00',
                'error': '#ff0000',
                'success': '#00ffff'
            };

            log.innerHTML += `<div style="color: ${colorMap[type] || '#00ff00'}">[${timestamp}] ${message}</div>`;
            log.scrollTop = log.scrollHeight;
        }

        function updateConnectionStatus(status, message) {
            const statusEl = document.getElementById('connectionStatus');
            statusEl.className = `connection-status ${status}`;

            const statusText = {
                'connected': '✅ Conectado al servidor',
                'disconnected': '❌ Desconectado del servidor',
                'connecting': '🔄 Conectando al servidor...'
            };

            statusEl.textContent = statusText[status] || message;
        }

        function updateConnectionTime() {
            if (connectionStartTime) {
                const elapsed = Date.now() - connectionStartTime;
                const hours = Math.floor(elapsed / 3600000);
                const minutes = Math.floor((elapsed % 3600000) / 60000);
                const seconds = Math.floor((elapsed % 60000) / 1000);

                document.getElementById('connectionTime').textContent = 
                    `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }
        }

        function connect() {
            if (socket && socket.readyState === WebSocket.OPEN) {
                addLog('Ya existe una conexión activa', 'warning');
                return;
            }

            updateConnectionStatus('connecting');
            addLog('Intentando conectar al servidor WebSocket...', 'info');

            socket = new WebSocket(`ws://${window.location.host}/ws/production`);

            socket.onopen = function(event) {
                updateConnectionStatus('connected');
                addLog('✅ Conexión WebSocket establecida', 'success');
                connectionStartTime = Date.now();
                connectionTimer = setInterval(updateConnectionTime, 1000);

                document.getElementById('connectBtn').disabled = true;
                document.getElementById('disconnectBtn').disabled = false;
            };

            socket.onmessage = function(event) {
                messageCount++;
                document.getElementById('messageCount').textContent = messageCount;

                try {
                    const data = JSON.parse(event.data);
                    handleMessage(data);
                } catch (e) {
                    addLog(`Error parseando mensaje: ${e}`, 'error');
                }
            };

            socket.onclose = function(event) {
                updateConnectionStatus('disconnected');
                addLog(`❌ Conexión cerrada. Código: ${event.code}`, 'warning');

                if (connectionTimer) {
                    clearInterval(connectionTimer);
                    connectionTimer = null;
                }

                document.getElementById('connectBtn').disabled = false;
                document.getElementById('disconnectBtn').disabled = true;
            };

            socket.onerror = function(error) {
                addLog(`❌ Error en WebSocket: ${error}`, 'error');
                updateConnectionStatus('disconnected', 'Error de conexión');
            };
        }

        function disconnect() {
            if (socket) {
                socket.close();
                socket = null;
            }
        }

        function sendPing() {
            if (socket && socket.readyState === WebSocket.OPEN) {
                const ping = { type: 'ping', timestamp: new Date().toISOString() };
                socket.send(JSON.stringify(ping));
                addLog('📡 Ping enviado', 'info');
            } else {
                addLog('❌ No hay conexión activa para enviar ping', 'error');
            }
        }

        function clearLog() {
            document.getElementById('log').innerHTML = '';
        }

        async function checkRecentData() {
            addLog('🔍 Verificando datos recientes...', 'info');
            try {
                const response = await fetch('/api/debug/recent-data');
                const data = await response.json();
                
                if (data.status === 'success') {
                    addLog(`✅ Diagnóstico exitoso:`, 'success');
                    addLog(`📊 Registros recientes: ${data.system_info.recent_records_count}`, 'info');
                    addLog(`🏭 Línea saludable: ${data.system_info.line_healthy}`, 'info');
                    addLog(`📦 Lote actual: ${data.system_info.current_batch}`, 'info');
                    
                    if (data.recent_data && data.recent_data.length > 0) {
                        const latest = data.recent_data[0];
                        addLog(`🆕 Último registro: Producto ${latest.product_id}, Calidad ${latest.quality_status}`, 'success');
                        addLog(`⏰ Timestamp: ${latest.timestamp}`, 'info');
                    } else {
                        addLog('⚠️ No hay datos recientes en la base de datos', 'warning');
                    }
                } else {
                    addLog(`❌ Error en diagnóstico: ${data.error}`, 'error');
                }
            } catch (error) {
                addLog(`❌ Error conectando con API: ${error}`, 'error');
            }
        }

        function handleMessage(data) {
            switch (data.type) {
                case 'connection':
                    addLog(`🔗 ${data.message}`, 'success');
                    break;

                case 'production_data':
                    productCount++;
                    document.getElementById('productCount').textContent = productCount;
                    updateProductionData(data.data);
                    addLog(`📦 Producto procesado: ID ${data.data.product_id}`, 'info');
                    break;

                case 'current_data':
                    updateProductionData(data.data);
                    addLog('📊 Datos actuales recibidos', 'info');
                    break;

                case 'pong':
                    addLog('📡 Pong recibido', 'success');
                    break;

                default:
                    addLog(`📨 Mensaje recibido: ${JSON.stringify(data)}`, 'info');
            }
        }

        function updateProductionData(data) {
            const container = document.getElementById('productionData');

            const qualityInfo = qualityMapping[data.quality_status] || { text: 'Desconocido', class: '' };
            const statusInfo = statusMapping[data.line_status] || { text: 'Desconocido', class: '' };

            container.innerHTML = `
                <div class="data-item">
                    <div class="data-label">ID Producto</div>
                    <div class="data-value">${data.product_id}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Calidad</div>
                    <div class="data-value ${qualityInfo.class}">${qualityInfo.text}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Contador Producción</div>
                    <div class="data-value">${data.production_count}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Estado Línea</div>
                    <div class="data-value ${statusInfo.class}">${statusInfo.text}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Código Error</div>
                    <div class="data-value">${data.error_code}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Tiempo Ciclo</div>
                    <div class="data-value">${data.cycle_time_ms} ms</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Temperatura</div>
                    <div class="data-value">${data.temperature}°C</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Presión</div>
                    <div class="data-value">${data.pressure} bar</div>
                </div>
                <div class="data-item">
                    <div class="data-label">ID Operador</div>
                    <div class="data-value">${data.operator_id}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">ID Lote</div>
                    <div class="data-value">${data.batch_id}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">Última Actualización</div>
                    <div class="data-value">${new Date(data.timestamp).toLocaleTimeString()}</div>
                </div>
            `;
        }

        // Auto-conectar al cargar la página
        window.onload = function() {
            addLog('🚀 Aplicación iniciada', 'success');
            connect();
        };

        // Manejar cierre de ventana
        window.onbeforeunload = function() {
            if (socket) {
                socket.close();
            }
        };
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content) 