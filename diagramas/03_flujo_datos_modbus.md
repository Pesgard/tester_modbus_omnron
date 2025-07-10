# 📊 Flujo de Datos: PLC → Servidor → Frontend

## Descripción
Diagrama de secuencia del flujo completo de datos desde el PLC externo hasta la visualización en el frontend, mostrando todos los pasos y procesos intermedios.

## Actores del Sistema
- **PLC Externo**: Equipos industriales con datos de producción
- **Servidor Modbus**: Receptor y procesador de datos Modbus TCP
- **Base de Datos**: Almacenamiento persistente PostgreSQL
- **API REST**: Servicios web para consultas
- **WebSocket**: Comunicación tiempo real
- **Frontend**: Interfaz de usuario SvelteKit

## Flujo Principal de Datos

### 🔄 Ciclo Completo de Datos
1. **Captura**: PLC recolecta datos de sensores/cámaras
2. **Transmisión**: Envío vía Modbus TCP al servidor
3. **Procesamiento**: Validación y transformación de datos
4. **Almacenamiento**: Persistencia en PostgreSQL
5. **Distribución**: Broadcasting vía WebSocket
6. **Visualización**: Actualización en tiempo real del frontend

```mermaid
sequenceDiagram
    participant PLC as 🏭 PLC Externo<br/>(192.168.1.100)
    participant ModbusSrv as 📡 Servidor Modbus<br/>(Puerto 502)
    participant DataProc as ⚙️ Procesador Datos<br/>(Backend)
    participant DB as 🗄️ PostgreSQL<br/>(Puerto 5432)
    participant WS as 📡 WebSocket Manager<br/>(Puerto 8000)
    participant API as 🌐 API REST<br/>(Puerto 8000)
    participant Frontend as 💻 Frontend SvelteKit<br/>(Puerto 3000)
    participant User as 👤 Usuario Final

    Note over PLC: 🔍 Recolección de Datos
    PLC->>PLC: Lectura sensores temperatura
    PLC->>PLC: Captura datos cámaras inspección
    PLC->>PLC: Análisis calidad (OK/NOK)
    PLC->>PLC: Estado línea producción
    
    Note over PLC, ModbusSrv: 📤 Transmisión Modbus TCP
    loop Cada 2 segundos
        PLC->>+ModbusSrv: Write Multiple Registers<br/>Direcciones 0-49<br/>Función 0x10
        ModbusSrv-->>-PLC: ACK Modbus Response<br/>Status: OK
    end
    
    Note over ModbusSrv, DataProc: 🔄 Procesamiento Interno
    ModbusSrv->>+DataProc: Nuevos datos disponibles<br/>Raw Modbus registers
    DataProc->>DataProc: Validación formato<br/>Range checking
    DataProc->>DataProc: Transformación unidades<br/>Int16 → Float/String
    DataProc->>DataProc: Aplicar lógica negocio<br/>Cálculo estadísticas
    
    Note over DataProc, DB: 💾 Almacenamiento Persistente
    DataProc->>+DB: INSERT production_record<br/>timestamp, product_id, quality_status
    DB-->>-DataProc: Record ID: 12345
    
    alt Si hay datos de calidad detallados
        DataProc->>+DB: INSERT quality_record<br/>production_record_id: 12345
        DB-->>-DataProc: Quality record created
    end
    
    alt Si hay parámetros de proceso
        DataProc->>+DB: INSERT process_record<br/>temperature, pressure, vibration
        DB-->>-DataProc: Process record created
    end
    
    Note over DataProc, WS: 📡 Broadcasting Tiempo Real
    DataProc->>+WS: Broadcast new data<br/>JSON formatted
    WS->>WS: Formatear mensaje WebSocket<br/>{"type": "production_update"}
    
    Note over WS, Frontend: 🔗 Comunicación WebSocket
    WS->>+Frontend: WebSocket Message<br/>ws://server:8000/ws
    Frontend->>Frontend: Actualizar store Svelte<br/>Reactive data binding
    Frontend->>Frontend: Re-render componentes<br/>Dashboard updates
    Frontend-->>-WS: ACK WebSocket received
    WS-->>-DataProc: Broadcast completado
    DataProc-->>-ModbusSrv: Processing completado
    
    Note over User, Frontend: 👁️ Visualización Usuario
    User->>+Frontend: Acceso dashboard<br/>http://server:3000
    Frontend->>Frontend: Cargar página inicial<br/>SvelteKit SSR
    
    alt Carga inicial de datos históricos
        Frontend->>+API: GET /api/production/current<br/>Authorization: Bearer token
        API->>+DB: SELECT recent production_records<br/>LIMIT 50
        DB-->>-API: ResultSet datos históricos
        API-->>-Frontend: JSON response<br/>Initial data
    end
    
    Frontend->>Frontend: Renderizar gráficos<br/>Chart.js / D3.js
    Frontend->>Frontend: Mostrar KPIs tiempo real<br/>Quality rate, cycle time
    Frontend-->>-User: Dashboard actualizado<br/>Datos en tiempo real
    
    Note over PLC, User: 🔄 Ciclo Continuo
    Note right of User: El ciclo se repite cada 2-3 segundos<br/>manteniendo sincronización<br/>tiempo real entre PLC y Frontend
    
    rect rgb(255, 245, 245)
        Note over PLC, User: ⚠️ Manejo de Errores
        alt Error en comunicación Modbus
            ModbusSrv->>DataProc: Connection timeout<br/>PLC no responde
            DataProc->>WS: Alert message<br/>{"type": "connection_error"}
            WS->>Frontend: Error notification
            Frontend->>User: ⚠️ Alert: PLC desconectado
        end
        
        alt Error en base de datos
            DataProc->>DB: INSERT production_record
            DB-->>DataProc: ERROR: Connection failed
            DataProc->>DataProc: Buffer datos localmente<br/>Retry automático
            DataProc->>WS: System alert<br/>{"type": "db_error"}
        end
    end
    
    rect rgb(245, 255, 245)
        Note over ModbusSrv, Frontend: 📊 Métricas de Performance
        Note right of DataProc: • Throughput: 0.5 Hz (cada 2s)<br/>• Latencia PLC→Frontend: <500ms<br/>• Buffer capacity: 1000 registros<br/>• Concurrent users: 50+<br/>• Data retention: 1 año
    end
```

## Detalles Técnicos del Flujo

### 📡 Protocolo Modbus TCP
```
┌─────────────────┬─────────────────┬─────────────────┐
│   MBAP Header   │  Function Code  │      Data       │
├─────────────────┼─────────────────┼─────────────────┤
│ TID │ PID │ LEN │ UID │   0x10     │ Addr │ Qty │ Val │
│  2  │  2  │  2  │  1  │     1      │  2   │  2  │ N*2 │
└─────────────────┴─────────────────┴─────────────────┘

• TID: Transaction ID (incrementa por mensaje)
• PID: Protocol ID (siempre 0x0000 para Modbus)
• LEN: Longitud campos siguientes
• UID: Unit ID (dirección dispositivo esclavo)
• Función 0x10: Write Multiple Registers
```

### ⚙️ Transformación de Datos
```python
# Ejemplo transformación datos PLC
raw_registers = [0x1A40, 0x0000, 0x0001, 0x0064]  # Del PLC

# Conversión a valores de aplicación
temperature = struct.unpack('>f', 
    struct.pack('>HH', raw_registers[0], raw_registers[1]))[0]
quality_status = "OK" if raw_registers[2] == 1 else "NOK"
cycle_time = raw_registers[3] * 10  # ms

# Formato para base de datos
production_data = {
    "timestamp": datetime.utcnow(),
    "temperature": round(temperature, 2),
    "quality_status": quality_status,
    "cycle_time_ms": cycle_time,
    "product_id": extract_product_id(raw_registers)
}
```

### 📊 Estructura Mensaje WebSocket
```json
{
  "type": "production_update",
  "timestamp": "2024-01-15T10:30:45.123Z",
  "data": {
    "production_record": {
      "id": 12345,
      "product_id": 2,
      "quality_status": "OK",
      "production_count": 1547,
      "cycle_time_ms": 2340,
      "temperature": 23.5,
      "batch_id": "BATCH_20240115_001"
    },
    "quality_metrics": {
      "dimension_1": 10.05,
      "dimension_2": 5.12,
      "visual_inspection": true
    },
    "line_status": {
      "status": "RUNNING",
      "speed": 25,
      "efficiency": 94.2
    }
  },
  "metadata": {
    "source": "modbus_server",
    "version": "1.0",
    "sequence": 15472
  }
}
```

## Configuración de Timing

### ⏱️ Intervalos de Comunicación
- **PLC → Servidor**: 2 segundos (configurable)
- **Procesamiento**: <100ms por ciclo
- **DB Insert**: <50ms promedio
- **WebSocket Broadcast**: <10ms
- **Frontend Update**: Inmediato (reactive)

### 🔄 Gestión de Buffer
```
┌──────────────┬──────────────┬──────────────┐
│   Buffer 1   │   Buffer 2   │   Buffer 3   │
│   (Active)   │  (Processing)│   (Backup)   │
├──────────────┼──────────────┼──────────────┤
│ Size: 1000   │ Size: 1000   │ Size: 1000   │
│ Status: Write│ Status: Read │ Status: Idle │
│ Records: 247 │ Records: 1000│ Records: 0   │
└──────────────┴──────────────┴──────────────┘

Rotation: Cada 2 minutos o cuando buffer lleno
Persistence: Automática cada 30 segundos
Recovery: Buffer backup en caso de fallo
```

## Monitoreo y Diagnóstico

### 📈 Métricas del Sistema
```sql
-- Query para métricas en tiempo real
SELECT 
    COUNT(*) as total_records_today,
    AVG(cycle_time_ms) as avg_cycle_time,
    MAX(timestamp) as last_update,
    COUNT(CASE WHEN quality_status = 'OK' THEN 1 END) * 100.0 / COUNT(*) as quality_rate
FROM production_records 
WHERE DATE(timestamp) = CURRENT_DATE;
```

### 🚨 Alertas Automáticas
- **Timeout PLC**: >5 segundos sin datos
- **Quality Drop**: Calidad <90% en última hora
- **DB Lag**: Inserción >1 segundo
- **WebSocket Disconnect**: >10 clientes desconectados
- **Memory Usage**: Buffer >80% capacidad 