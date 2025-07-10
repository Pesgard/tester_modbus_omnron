# GET /api/production/current

📊 **Current Production Status Endpoint**

Get the most recent production data from the manufacturing line in real-time.

## Overview

This endpoint provides real-time visibility into the current manufacturing process, including product information, quality metrics, production rates, system status, and process parameters.

## Request

### Method & URL
```http
GET /api/production/current
Authorization: Bearer <your-token-here>
```

### Authentication Required

This endpoint requires a valid JWT token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Example Request

```http
GET /api/production/current HTTP/1.1
Host: localhost:8000
Authorization: Bearer <your-jwt-token>
```

### cURL Example

```bash
curl -X GET "http://localhost:8000/api/production/current" \
     -H "Authorization: Bearer <your-jwt-token>"
```

## Response

### Success Response (200 OK)

```json
{
    "status": "success",
    "data": {
        "timestamp": "2024-01-01T12:00:00Z",
        "product_id": 12345,
        "quality_status": "OK",
        "production_count": 100,
        "line_status": "RUNNING",
        "error_code": 0,
        "cycle_time_ms": 2500,
        "temperature": 25.5,
        "pressure": 4.2,
        "operator_id": 1,
        "batch_id": "BATCH_20240101_001"
    }
}
```

### No Data Response (200 OK)

When no production data is available:

```json
{
    "status": "success",
    "data": null
}
```

### Response Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `status` | string | Response status | `"success"` |
| `data` | object\|null | Production data or null if no data available | - |

### Production Data Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `timestamp` | string (ISO 8601) | When the data was recorded | `"2024-01-01T12:00:00Z"` |
| `product_id` | integer | Unique identifier for manufactured product | `12345` |
| `quality_status` | string | Quality assessment result | `"OK"`, `"NOK"`, `"PENDING"` |
| `production_count` | integer | Total products produced in session | `100` |
| `line_status` | string | Current production line status | `"RUNNING"`, `"STOPPED"`, `"ERROR"`, `"MAINTENANCE"` |
| `error_code` | integer | Error code (0 = no error) | `0` |
| `cycle_time_ms` | integer | Production cycle time in milliseconds | `2500` |
| `temperature` | float | Operating temperature in Celsius | `25.5` |
| `pressure` | float | Operating pressure in bar | `4.2` |
| `operator_id` | integer | ID of operator managing production | `1` |
| `batch_id` | string | Unique identifier for production batch | `"BATCH_20240101_001"` |

## Error Responses

### 401 Unauthorized
```json
{
    "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
    "detail": "Insufficient permissions"
}
```

### 500 Internal Server Error
```json
{
    "detail": "Error retrieving production data"
}
```

## Quality Status Values

| Status | Description | Color Code |
|--------|-------------|------------|
| `OK` | Product passed quality checks | 🟢 Green |
| `NOK` | Product failed quality checks | 🔴 Red |
| `PENDING` | Quality check in progress | 🟡 Yellow |

## Line Status Values

| Status | Description | Typical Actions |
|--------|-------------|-----------------|
| `RUNNING` | Normal production operation | Monitor metrics |
| `STOPPED` | Production line stopped | Check for planned downtime |
| `ERROR` | Error condition detected | Investigate error_code |
| `MAINTENANCE` | Maintenance mode active | Scheduled maintenance |

## Data Update Frequency

- **PLC Communication**: Data updated every 2-3 seconds
- **WebSocket Alternative**: Use `/ws/production` for real-time streaming
- **Polling Recommendation**: Poll this endpoint every 5-10 seconds maximum

## Real-time Alternative

For continuous real-time data, consider using the WebSocket endpoint instead:

```javascript
const socket = new WebSocket('ws://localhost:8000/ws/production');
socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'production_data') {
        updateProductionDisplay(data.data);
    }
};
```

## Use Cases

### Production Monitoring Dashboard
```javascript
async function getCurrentProduction() {
    try {
        const response = await fetch('/api/production/current', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        
        const result = await response.json();
        
        if (result.data) {
            updateProductionDisplay(result.data);
        } else {
            showNoDataMessage();
        }
    } catch (error) {
        console.error('Failed to fetch production data:', error);
    }
}

// Poll every 5 seconds
setInterval(getCurrentProduction, 5000);
```

### Quality Monitoring
```javascript
function checkQualityStatus(data) {
    switch (data.quality_status) {
        case 'OK':
            updateQualityIndicator('green', 'Quality: PASS');
            break;
        case 'NOK':
            updateQualityIndicator('red', 'Quality: FAIL');
            triggerQualityAlert(data);
            break;
        case 'PENDING':
            updateQualityIndicator('yellow', 'Quality: TESTING');
            break;
    }
}
```

### Error Detection
```javascript
function checkForErrors(data) {
    if (data.error_code !== 0) {
        showErrorAlert({
            code: data.error_code,
            status: data.line_status,
            timestamp: data.timestamp
        });
    }
    
    if (data.line_status === 'ERROR') {
        triggerProductionAlert(data);
    }
}
```

## Python Example

```python
import requests
from datetime import datetime

class ProductionMonitor:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {'Authorization': f'Bearer {token}'}
    
    def get_current_production(self) -> dict:
        """Get current production data."""
        response = requests.get(
            f"{self.base_url}/api/production/current",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def monitor_production(self):
        """Monitor production with basic alerts."""
        try:
            result = self.get_current_production()
            
            if not result['data']:
                print("No production data available")
                return
            
            data = result['data']
            
            # Quality check
            if data['quality_status'] == 'NOK':
                print(f"⚠️ Quality failure detected: Product {data['product_id']}")
            
            # Error check
            if data['error_code'] != 0:
                print(f"🚨 Error detected: Code {data['error_code']}")
            
            # Status check
            if data['line_status'] != 'RUNNING':
                print(f"ℹ️ Line status: {data['line_status']}")
            
            # Performance metrics
            print(f"📊 Production: {data['production_count']} units, "
                  f"Cycle: {data['cycle_time_ms']}ms, "
                  f"Quality: {data['quality_status']}")
                  
        except requests.exceptions.RequestException as e:
            print(f"Error fetching production data: {e}")

# Usage
monitor = ProductionMonitor("http://localhost:8000", "your-jwt-token")
monitor.monitor_production()
```

## Integration with Monitoring Systems

### Prometheus Metrics
```python
from prometheus_client import Gauge, Counter

# Define metrics
production_count = Gauge('production_total', 'Total production count')
cycle_time = Gauge('cycle_time_seconds', 'Production cycle time')
quality_rate = Gauge('quality_rate', 'Quality pass rate')
temperature = Gauge('temperature_celsius', 'Operating temperature')

def update_metrics(data):
    """Update Prometheus metrics with production data."""
    production_count.set(data['production_count'])
    cycle_time.set(data['cycle_time_ms'] / 1000)  # Convert to seconds
    temperature.set(data['temperature'])
    
    if data['quality_status'] == 'OK':
        quality_rate.set(1)
    elif data['quality_status'] == 'NOK':
        quality_rate.set(0)
```

### Alerting Rules
```yaml
# Example Prometheus alerting rules
groups:
  - name: production.rules
    rules:
      - alert: ProductionLineStopped
        expr: line_status != "RUNNING"
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Production line stopped"
          
      - alert: QualityFailure
        expr: quality_rate < 0.95
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Quality rate below 95%"
```

## Performance Considerations

- **Caching**: Data is cached for 2-3 seconds to avoid overwhelming the database
- **Lightweight**: Returns only essential current data
- **Fast Response**: Typical response time < 100ms
- **Concurrent Access**: Supports multiple simultaneous requests

## Security Notes

- **Authentication Required**: Valid JWT token must be provided
- **Role-based Access**: All authenticated users can access this endpoint
- **Rate Limiting**: Standard API rate limits apply
- **No Sensitive Data**: Response contains only production metrics 