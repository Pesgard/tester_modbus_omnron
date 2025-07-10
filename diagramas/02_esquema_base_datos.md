# 🗄️ Esquema de Base de Datos PostgreSQL

## Descripción
Diagrama del esquema completo de la base de datos `production_system` con todas las tablas, relaciones y restricciones.

## Base de Datos Principal
- **Nombre**: production_system
- **Motor**: PostgreSQL 15
- **Encoding**: UTF-8
- **Schemas**: public, production, auth, audit, config

## Tablas del Sistema

### 📊 Datos de Producción
- **production_records**: Registro principal de cada pieza
- **quality_records**: Datos detallados de inspección
- **process_records**: Parámetros de proceso operativo

### 👥 Gestión de Usuarios
- **users**: Credenciales y perfiles de usuario
- **permissions**: Permisos granulares del sistema
- **user_permissions**: Relación N:M usuarios-permisos

### 📝 Auditoría y Eventos
- **audit_logs**: Trazabilidad de todas las acciones
- **system_events**: Eventos y alertas del sistema
- **system_config**: Configuración dinámica

```mermaid
erDiagram
    %% Tabla de Usuarios
    users {
        int id PK "Primary Key"
        string username UK "Unique, Required"
        string email UK "Unique, Required"
        string hashed_password "Bcrypt Hash"
        string full_name "Nullable"
        enum role "admin|supervisor|operator|viewer"
        boolean is_active "Default: true"
        boolean is_verified "Default: false"
        datetime last_login "Nullable"
        datetime created_at "Auto timestamp"
        datetime updated_at "Auto update"
    }

    %% Tabla de Permisos
    permissions {
        int id PK
        string name UK "Unique permission name"
        string description "Human readable"
        string resource "e.g., production, system"
        string action "e.g., read, write, delete"
        datetime created_at
    }

    %% Tabla de Relación Usuario-Permisos
    user_permissions {
        int user_id FK
        int permission_id FK
    }

    %% Registro Principal de Producción
    production_records {
        int id PK
        datetime timestamp "Index, Required"
        int product_id "Model ID (1-4)"
        enum quality_status "NOK|OK|PENDING"
        int production_count "Total counter"
        enum line_status "STOPPED|RUNNING|ERROR|MAINTENANCE"
        int error_code "0 = no error"
        int cycle_time_ms "Cycle time milliseconds"
        float temperature "Celsius"
        float pressure "Bar"
        int operator_id FK "Nullable"
        string batch_id "Index, BATCH_YYYYMMDD_XXX"
        string shift_id "Nullable"
        datetime created_at
    }

    %% Registros de Calidad Detallados
    quality_records {
        int id PK
        int production_record_id FK
        float dimension_1 "mm, Nullable"
        float dimension_2 "mm, Nullable"
        float surface_roughness "μm, Nullable"
        float hardness "HRC, Nullable"
        boolean visual_inspection "Nullable"
        datetime created_at
    }

    %% Registros de Parámetros de Proceso
    process_records {
        int id PK
        int production_record_id FK
        float temperature_line1 "°C, Nullable"
        float temperature_line2 "°C, Nullable"
        float hydraulic_pressure "bar, Nullable"
        float air_pressure "bar, Nullable"
        int line_speed "units/min, Nullable"
        float vibration "Hz, Nullable"
        float power_consumption "A, Nullable"
        int lubricant_level "%, Nullable"
        int sensor_status "bitmask, Nullable"
        int active_alarms "bitmask, Nullable"
        datetime created_at
    }

    %% Eventos del Sistema
    system_events {
        int id PK
        datetime timestamp "Index"
        string event_type "error|warning|info|security"
        string severity "low|medium|high|critical"
        text message "Event description"
        string source "modbus|api|system|user"
        int user_id FK "Nullable"
        boolean resolved "Default: false"
        int resolved_by FK "Nullable"
        datetime resolved_at "Nullable"
        text event_metadata "JSON string"
    }

    %% Configuración del Sistema
    system_config {
        int id PK
        string key UK "Config key, Index"
        text value "Config value"
        text description "Nullable"
        string category "Default: general"
        boolean is_sensitive "For passwords, etc."
        int updated_by FK "Nullable"
        datetime updated_at
        datetime created_at
    }

    %% Logs de Auditoría
    audit_logs {
        int id PK
        datetime timestamp "Index"
        int user_id FK "Nullable"
        string action "Action performed"
        string resource "Resource affected"
        string resource_id "Nullable"
        string ip_address "IPv4/IPv6"
        string user_agent "Nullable"
        text details "JSON string"
    }

    %% Relaciones
    users ||--o{ production_records : "operator_id"
    users ||--o{ system_events : "user_id"
    users ||--o{ system_events : "resolved_by"
    users ||--o{ system_config : "updated_by"
    users ||--o{ audit_logs : "user_id"
    users ||--o{ user_permissions : "user_id"
    permissions ||--o{ user_permissions : "permission_id"
    
    production_records ||--o{ quality_records : "production_record_id"
    production_records ||--o{ process_records : "production_record_id"
```

## Índices Principales

### 🔍 Índices de Performance
```sql
-- Índices para consultas frecuentes
CREATE INDEX idx_production_timestamp ON production_records(timestamp);
CREATE INDEX idx_production_batch ON production_records(batch_id);
CREATE INDEX idx_production_status ON production_records(line_status);
CREATE INDEX idx_quality_status ON production_records(quality_status);

-- Índices para auditoría
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_events_timestamp ON system_events(timestamp);
CREATE INDEX idx_events_severity ON system_events(severity);

-- Índices únicos
CREATE UNIQUE INDEX idx_users_username ON users(username);
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE UNIQUE INDEX idx_config_key ON system_config(key);
```

## Vistas Principales

### 📊 Vista Resumen Producción
```sql
CREATE VIEW production_summary AS
SELECT 
    DATE(timestamp) as production_date,
    COUNT(*) as total_records,
    SUM(production_count) as total_production,
    AVG(cycle_time_ms) as avg_cycle_time,
    COUNT(CASE WHEN quality_status = 'OK' THEN 1 END) as good_quality_count,
    COUNT(CASE WHEN quality_status = 'NOK' THEN 1 END) as bad_quality_count,
    ROUND(100.0 * COUNT(CASE WHEN quality_status = 'OK' THEN 1 END) / COUNT(*), 2) as quality_rate
FROM production_records 
GROUP BY DATE(timestamp)
ORDER BY production_date DESC;
```

### 👥 Vista Actividad Usuarios
```sql
CREATE VIEW user_activity AS
SELECT 
    u.username,
    u.role,
    u.last_login,
    COUNT(al.id) as total_actions,
    MAX(al.timestamp) as last_action
FROM users u
LEFT JOIN audit_logs al ON u.id = al.user_id
GROUP BY u.id, u.username, u.role, u.last_login
ORDER BY last_action DESC NULLS LAST;
```

## Configuración de Backup

### 🔄 Backup Automático
```bash
#!/bin/bash
# Script de backup automático
BACKUP_DIR="/var/backups/production_system"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup completo
pg_dump production_system > "$BACKUP_DIR/full_backup_$DATE.sql"

# Backup solo datos
pg_dump --data-only production_system > "$BACKUP_DIR/data_only_$DATE.sql"

# Comprimir y limpiar backups antiguos
gzip "$BACKUP_DIR/full_backup_$DATE.sql"
find "$BACKUP_DIR" -name "*.gz" -mtime +30 -delete
```

## Mantenimiento

### 🧹 Limpieza de Datos Antiguos
```sql
-- Eliminar audit_logs mayores a 1 año
DELETE FROM audit_logs 
WHERE timestamp < NOW() - INTERVAL '365 days';

-- Eliminar system_events resueltos mayores a 6 meses
DELETE FROM system_events 
WHERE resolved = true 
AND resolved_at < NOW() - INTERVAL '180 days';

-- Actualizar estadísticas
ANALYZE production_records;
ANALYZE quality_records;
ANALYZE process_records;
```

### 📈 Monitoreo de Performance
```sql
-- Consultas más lentas
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;

-- Tamaño de tablas
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
``` 