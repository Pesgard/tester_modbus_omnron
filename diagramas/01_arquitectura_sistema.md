# 🏗️ Arquitectura del Sistema - Servidor Único

## Descripción
Diagrama de la arquitectura completa del sistema de producción industrial con servidor único, PLC externo conectado vía Modbus TCP.

## Componentes Principales

### 🏭 PLC Externo
- **Ubicación**: Red industrial separada
- **IP**: 192.168.1.100 (configurable)
- **Protocolo**: Modbus TCP puerto 502
- **Integra**: Cámaras, sensores, controladores

### 🖥️ Servidor Principal  
- **IP**: 192.168.1.200
- **OS**: Linux Ubuntu 20.04+
- **Backend**: FastAPI + Python 3.11
- **Frontend**: SvelteKit + Node.js 18
- **DB**: PostgreSQL local

### 🌐 Acceso Usuarios
- **Puerto Frontend**: 3000
- **Puerto API**: 8000
- **WebSocket**: ws://server:8000/ws
- **Múltiples clientes simultáneos**

```mermaid
graph TB
    %% Definición de estilos
    classDef plc fill:#FFF9C4,stroke:#E65100,stroke-width:3px,color:#000
    classDef server fill:#E8F5E8,stroke:#2E7D32,stroke-width:3px,color:#000
    classDef backend fill:#E3F2FD,stroke:#1565C0,stroke-width:2px,color:#000
    classDef frontend fill:#F3E5F5,stroke:#7B1FA2,stroke-width:2px,color:#000
    classDef database fill:#FFEBEE,stroke:#C62828,stroke-width:2px,color:#000
    classDef client fill:#FFF3E0,stroke:#F57C00,stroke-width:2px,color:#000

    %% PLC Externo
    subgraph "🏭 PLC Externo (Red Industrial)"
        PLCExterno["`🔧 **PLC/Equipos Externos**<br/>- Sensores de Calidad<br/>- Sistemas de Visión<br/>- Controladores Proceso<br/>- Dirección IP: 192.168.1.100`"]
        CamerasExternas["`📷 **Cámaras Inspección**<br/>- Verificación Etiqueta<br/>- Control Color<br/>- Validación Componentes<br/>- Conectadas al PLC`"]
        SensoresExternos["`🌡️ **Sensores Proceso**<br/>- Temperatura Línea<br/>- Presión Hidráulica<br/>- Vibración Motores<br/>- Datos vía PLC`"]
    end

    %% Servidor Principal
    subgraph "🖥️ Servidor Principal (192.168.1.200)"
        
        %% Backend en el Servidor
        subgraph "🚀 Backend Application"
            ModbusServer["`📡 **Servidor Modbus TCP**<br/>- Puerto: 502<br/>- IP: 0.0.0.0<br/>- Escucha conexiones PLC<br/>- Procesamiento datos`"]
            
            DataProcessor["`⚙️ **Procesador Datos**<br/>- Buffer 1000 registros<br/>- Validación tiempo real<br/>- Thread asíncrono<br/>- Gestión errores`"]
            
            APIService["`🌐 **API REST Service**<br/>- FastAPI Framework<br/>- Puerto: 8000<br/>- Endpoints JSON<br/>- Autenticación JWT`"]
            
            WebSocketService["`📡 **WebSocket Service**<br/>- Tiempo real<br/>- Broadcasting datos<br/>- Heartbeat activo<br/>- Multi-cliente`"]
            
            BusinessLogic["`🏭 **Lógica Negocio**<br/>- Procesamiento producción<br/>- Cálculo estadísticas<br/>- Gestión lotes<br/>- Control calidad`"]
        end
        
        %% Base de Datos en el Servidor
        subgraph "🗄️ Base de Datos"
            PostgreSQL["`🐘 **PostgreSQL**<br/>- Puerto: 5432<br/>- DB: production_system<br/>- Almacenamiento local<br/>- Backup automático`"]
            
            DataTables["`📊 **Tablas Principales**<br/>- production_records<br/>- quality_records<br/>- process_records<br/>- users & audit_logs`"]
        end
        
        %% Frontend en el Servidor
        subgraph "💻 Frontend Web Application"
            SvelteApp["`🎨 **SvelteKit App**<br/>- Puerto: 3000<br/>- UI Tiempo Real<br/>- Dashboard Interactivo<br/>- Responsive Design`"]
            
            StaticFiles["`📦 **Assets Estáticos**<br/>- CSS compilado<br/>- JavaScript bundles<br/>- Imágenes y fonts<br/>- PWA manifest`"]
        end
        
        %% Sistema Operativo
        ServerOS["`💻 **Sistema Operativo**<br/>- Linux Ubuntu 20.04+<br/>- Python 3.11 Runtime<br/>- Node.js 18+ Runtime<br/>- Nginx (opcional)`"]
    end

    %% Clientes Web
    subgraph "👥 Usuarios Finales"
        WebClients["`🌐 **Navegadores Web**<br/>- Chrome, Firefox, Safari<br/>- Dispositivos móviles<br/>- Tablets industriales<br/>- Estaciones trabajo`"]
        
        UserRoles["`👤 **Roles Usuario**<br/>- Admin: Gestión total<br/>- Supervisor: Reportes<br/>- Operador: Monitoreo<br/>- Viewer: Solo lectura`"]
    end

    %% Red Industrial
    subgraph "🌐 Red Ethernet Industrial"
        NetworkSwitch["`🔗 **Switch Industrial**<br/>- Gigabit Ethernet<br/>- VLAN Configurada<br/>- QoS para Modbus<br/>- Redundancia activa`"]
    end

    %% Herramientas Diagnóstico
    subgraph "🔧 Herramientas Diagnóstico"
        PLCSimulator["`🎮 **Simulador PLC**<br/>- ModbusPoll / Qmodbus<br/>- Testing conexiones<br/>- Simulación datos<br/>- Validación protocolo`"]
        
        NetworkTools["`📡 **Herramientas Red**<br/>- Wireshark análisis<br/>- ModbusScan diagnóstico<br/>- Ping/Telnet testing<br/>- Port monitoring`"]
    end

    %% Conexiones principales
    PLCExterno -.->|"Modbus TCP<br/>Puerto 502<br/>IP: 192.168.1.200"| NetworkSwitch
    CamerasExternas --> PLCExterno
    SensoresExternos --> PLCExterno
    
    NetworkSwitch -.->|"Ethernet"| ModbusServer
    
    %% Flujo interno del servidor
    ModbusServer --> DataProcessor
    DataProcessor --> BusinessLogic
    DataProcessor --> PostgreSQL
    DataProcessor --> WebSocketService
    
    BusinessLogic --> PostgreSQL
    BusinessLogic --> APIService
    
    PostgreSQL --> DataTables
    APIService --> SvelteApp
    WebSocketService -.->|"ws://server:8000/ws"| SvelteApp
    
    %% Conexión con clientes
    SvelteApp -.->|"HTTP/HTTPS<br/>Puerto 3000"| NetworkSwitch
    NetworkSwitch -.->|"LAN/WiFi"| WebClients
    WebClients --> UserRoles
    
    %% Herramientas de diagnóstico
    PLCSimulator -.->|"Modbus TCP Test"| NetworkSwitch
    NetworkTools -.->|"Network Analysis"| NetworkSwitch
    
    %% Sistema base
    ServerOS --> PostgreSQL
    ServerOS --> APIService
    ServerOS --> SvelteApp
    StaticFiles --> SvelteApp

    %% Aplicar estilos
    class PLCExterno,CamerasExternas,SensoresExternos plc
    class ServerOS server
    class ModbusServer,DataProcessor,APIService,WebSocketService,BusinessLogic backend
    class SvelteApp,StaticFiles frontend
    class PostgreSQL,DataTables database
    class WebClients,UserRoles,PLCSimulator,NetworkTools,NetworkSwitch client
```

## Ventajas de esta Arquitectura

### ✅ Simplicidad
- Un solo servidor para gestionar
- Instalación directa sin contenedores
- Configuración centralizada

### ✅ Performance
- Comunicación directa entre componentes
- Sin overhead de Docker
- Acceso directo a recursos sistema

### ✅ Mantenimiento
- Logs centralizados en servidor
- Backup simplificado
- Updates coordinados

### ✅ Escalabilidad
- Preparado para múltiples PLCs
- Soporte múltiples usuarios
- Base para futura expansión

## Requisitos de Red

### IP Addresses
- **Servidor**: 192.168.1.200
- **PLC**: 192.168.1.100
- **Subnet**: 192.168.1.0/24

### Puertos Utilizados
- **502**: Modbus TCP (PLC → Servidor)
- **3000**: Frontend Web
- **8000**: API REST + WebSocket
- **5432**: PostgreSQL (local)

### Firewall Rules
```bash
# Permitir Modbus TCP desde PLC
iptables -A INPUT -s 192.168.1.100 -p tcp --dport 502 -j ACCEPT

# Permitir acceso web desde LAN
iptables -A INPUT -s 192.168.1.0/24 -p tcp --dport 3000 -j ACCEPT
iptables -A INPUT -s 192.168.1.0/24 -p tcp --dport 8000 -j ACCEPT
``` 