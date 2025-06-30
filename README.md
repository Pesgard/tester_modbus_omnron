# 🏭 Sistema de Producción Industrial con Modbus

Sistema completo de monitoreo y control de producción industrial que integra comunicación Modbus TCP, API REST, WebSockets en tiempo real y una interfaz web moderna para supervisión de líneas de producción.

## 🌟 Características Principales

### 📡 Comunicación Industrial
- **Servidor Modbus TCP** en puerto 502 para comunicación con PLCs
- Soporte para múltiples direcciones de registro (0-199)
- Procesamiento en tiempo real de datos de producción, calidad y proceso
- Compatible con sistemas de inspección visual y pruebas eléctricas

### 🌐 API REST Completa
- **FastAPI** con documentación automática (Swagger)
- Endpoints para datos de producción, historial y estadísticas
- Sistema de diagnóstico integrado
- CORS habilitado para integración con sistemas externos

### ⚡ Tiempo Real
- **WebSockets** para transmisión instantánea de datos
- Interfaz web moderna con actualizaciones en vivo
- Dashboard interactivo para monitoreo continuo
- Notificaciones de eventos y alertas

### 💾 Gestión de Datos
- Base de datos **SQLite** con esquema optimizado
- Pool de conexiones para alta concurrencia
- Almacenamiento de historial completo de producción
- Indexación automática para consultas rápidas

## 🛠️ Tecnologías Utilizadas

- **Python 3.8+**
- **FastAPI** - Framework web moderno y rápido
- **PyModbus** - Biblioteca Modbus TCP/IP
- **SQLite** - Base de datos embebida
- **WebSockets** - Comunicación bidireccional en tiempo real
- **Uvicorn** - Servidor ASGI de alto rendimiento
- **HTML5 + JavaScript** - Interfaz web responsiva

## 📦 Instalación

### Requisitos Previos
```bash
Python 3.8 o superior
pip (gestor de paquetes de Python)
```

### Instalación de Dependencias
```bash
# Clonar o descargar el proyecto
cd tester_modbus_omnron

# Instalar dependencias
pip install fastapi uvicorn pymodbus
```

### Estructura del Proyecto
```
tester_modbus_omnron/
├── main.py                 # Aplicación principal
├── README.md              # Este archivo
├── production_system.db   # Base de datos (se crea automáticamente)
├── production_system.log  # Archivo de logs
└── plc_simulator.py       # Cliente PLC simulado (tu código)
```

## 🚀 Uso

### 1. Iniciar el Servidor
```bash
python main.py
```

El sistema iniciará:
- **Servidor Modbus TCP**: Puerto 502
- **API REST**: Puerto 8000
- **Interfaz Web**: http://localhost:8000

### 2. Acceder a la Interfaz Web
Abre tu navegador y ve a:
- **Dashboard Principal**: http://localhost:8000
- **Monitor en Tiempo Real**: http://localhost:8000/client
- **API Docs**: http://localhost:8000/docs

### 3. Conectar PLC o Simulador
El servidor acepta conexiones Modbus TCP en las siguientes direcciones:
- **Dirección 1**: Datos principales de producción
- **Dirección 21**: Datos de calidad detallados
- **Dirección 41**: Datos de proceso (temperatura, presión)

## 📊 Mapeo de Registros Modbus

### Registros Principales (Dirección 1)
| Registro | Descripción | Tipo |
|----------|-------------|------|
| 0 | ID del Producto | INT |
| 1 | Estado de Calidad (0=NOK, 1=OK) | INT |
| 2 | Contador de Producción | INT |
| 3 | Piezas OK | INT |
| 4 | Piezas NOK | INT |
| 5 | Estado de Línea (0=Parado, 1=Funcionando, 2=Error, 3=Mantenimiento) | INT |
| 6 | Código de Error | INT |
| 7 | Tiempo de Ciclo (ms) | INT |
| 8 | ID del Operador | INT |
| 9 | ID de Estación | INT |

### Registros de Calidad (Dirección 21)
| Registro | Descripción | Tipo |
|----------|-------------|------|
| 0 | Resultado Cámara 1 (Etiqueta) | INT |
| 1 | Resultado Cámara 2 (Color) | INT |
| 2 | Resultado Cámara 3 (Componentes) | INT |
| 3 | Resultado High Pot | INT |
| 4 | Valor High Pot (*10) | INT |
| 5 | Resultado Continuidad | INT |
| 6 | Valor Continuidad (*100) | INT |
| 8 | Código de Falla | INT |
| 9 | Número de Cámaras Usadas | INT |

### Registros de Proceso (Dirección 41)
| Registro | Descripción | Tipo |
|----------|-------------|------|
| 0 | Temperatura Línea 1 (*10) | INT |
| 1 | Temperatura Línea 2 (*10) | INT |
| 2 | Presión Hidráulica (*10) | INT |
| 3 | Presión Neumática (*10) | INT |
| 4 | Velocidad de Línea | INT |
| 5 | Vibración Motor (*100) | INT |
| 6 | Consumo Energético | INT |
| 7 | Nivel Lubricante | INT |
| 8 | Estado Sensores | INT |
| 9 | Alarmas Activas | INT |

## 🔌 API Endpoints

### Producción
- `GET /api/production/current` - Datos actuales de producción
- `GET /api/production/history` - Historial de producción con filtros
- `GET /api/production/stats` - Estadísticas de producción

### Sistema
- `GET /api/system/health` - Estado de salud del sistema
- `GET /api/debug/recent-data` - Diagnóstico y datos recientes

### WebSocket
- `WS /ws/production` - Stream de datos en tiempo real

### Ejemplos de Uso API

```bash
# Obtener datos actuales
curl http://localhost:8000/api/production/current

# Obtener historial del último día
curl "http://localhost:8000/api/production/history?start_date=2024-01-01T00:00:00&limit=100"

# Verificar estado del sistema
curl http://localhost:8000/api/system/health

# Diagnóstico completo
curl http://localhost:8000/api/debug/recent-data
```

## 🖥️ Interfaz de Usuario

### Dashboard Principal
- **Página de inicio**: Vista general del sistema
- **Enlaces rápidos**: Acceso directo a todas las funciones
- **Estado del sistema**: Indicadores de salud en tiempo real

### Monitor en Tiempo Real
- **Datos de Producción**: Visualización en vivo de todos los parámetros
- **Estadísticas de Sesión**: Contadores y métricas de la sesión actual
- **Log de Eventos**: Historial detallado de actividad
- **Controles**: Conexión/desconexión, ping, diagnóstico

### Características de la UI
- ✅ **Responsive Design**: Se adapta a diferentes tamaños de pantalla
- 🎨 **Interfaz Moderna**: Diseño profesional con gradientes y sombras
- 🔄 **Actualizaciones en Tiempo Real**: Sin necesidad de recargar la página
- 📊 **Visualización Intuitiva**: Códigos de color para estados y calidad
- 🔧 **Herramientas de Diagnóstico**: Botones para verificación rápida

## 🧪 Simulador de PLC

El proyecto incluye un simulador avanzado de PLC que genera datos realistas:

### Características del Simulador
- **4 Modelos de Productos**: Diferentes configuraciones de cámaras y pruebas
- **Sistema de Inspección Visual**: Simulación de cámaras para etiqueta, color y componentes
- **Pruebas Eléctricas**: High Pot y continuidad con valores realistas
- **Fallas Simuladas**: 15% de probabilidad de fallas con códigos específicos
- **Datos Ambientales**: Temperatura, presión y vibración variables

### Ejecutar el Simulador
```bash
python plc_simulator.py
```

## 📝 Logs y Diagnóstico

### Archivos de Log
- **production_system.log**: Log completo del sistema
- **Consola**: Mensajes informativos en tiempo real

### Niveles de Log
- 📡 **INFO**: Datos recibidos del PLC
- 🌡️ **PROCESS**: Datos de temperatura y presión
- 📊 **QUALITY**: Información de calidad
- ❌ **ERROR**: Errores del sistema
- ⚠️ **WARNING**: Advertencias

### Herramientas de Diagnóstico
1. **Botón Diagnóstico en UI**: Verificación rápida desde el navegador
2. **Endpoint de Debug**: `/api/debug/recent-data`
3. **Health Check**: `/api/system/health`
4. **Logs Detallados**: Seguimiento completo de actividad

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Puerto del servidor web (por defecto: 8000)
export WEB_PORT=8000

# Puerto Modbus (por defecto: 502)
export MODBUS_PORT=502

# Nivel de log (por defecto: INFO)
export LOG_LEVEL=INFO
```

### Personalización de Base de Datos
- **Ubicación**: `production_system.db`
- **Esquema**: Se crea automáticamente al iniciar
- **Migración**: Automática en nuevas versiones

## 🚨 Solución de Problemas

### Problemas Comunes

**1. Error "Puerto 502 en uso"**
```bash
# En Windows (ejecutar como administrador)
netstat -ano | findstr :502
# Terminar proceso que use el puerto

# En Linux
sudo netstat -tulpn | grep :502
sudo kill <PID>
```

**2. No se reciben datos del PLC**
- Verificar que el PLC esté enviando a las direcciones correctas (1, 21, 41)
- Usar el botón "🔍 Diagnóstico" en la interfaz web
- Revisar logs en `production_system.log`

**3. WebSocket no conecta**
- Verificar firewall/antivirus
- Comprobar que el puerto 8000 esté disponible
- Revisar logs del navegador (F12)

### Comandos de Diagnóstico
```bash
# Verificar puertos
netstat -an | grep -E "502|8000"

# Ver logs en tiempo real
tail -f production_system.log

# Probar conectividad Modbus
telnet localhost 502
```

## 🤝 Contribución

### Estructura del Código
- **Modular**: Clases separadas para cada funcionalidad
- **Documentado**: Docstrings en todas las funciones importantes
- **Type Hints**: Tipado estático para mejor mantenibilidad
- **Logging**: Sistema de logs comprehensivo

### Para Desarrolladores
```python
# Agregar nuevos endpoints
@app.get("/api/nueva-funcionalidad")
async def nueva_funcionalidad():
    return {"mensaje": "Nueva funcionalidad"}

# Procesar nuevos tipos de datos
def procesar_nuevos_datos(self, address: int, values: List[int]):
    # Tu lógica aquí
    pass
```

## 📄 Licencia

Este proyecto es de código abierto y puede ser usado libremente para propósitos educativos e industriales.

## 📞 Soporte

Para reportar bugs o solicitar nuevas características:
1. Revisar los logs del sistema
2. Usar las herramientas de diagnóstico integradas
3. Documentar el problema con ejemplos específicos

---

**¡Sistema listo para producción industrial! 🏭**

> Desarrollado para integración robusta con PLCs industriales y sistemas de inspección visual. 