# 🏭 Production System API Reference

**FastAPI-based Industrial Production Monitoring API**

This document provides comprehensive documentation for all API endpoints following FastAPI best practices for maintainable and readable code.

## 🌐 Base URL & Interactive Documentation

```
http://localhost:8000
```

### Interactive API Documentation

FastAPI automatically generates interactive documentation with live testing capabilities:

- **🔎 Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
  - Interactive endpoint testing
  - Request/response examples
  - Schema validation
  
- **📚 ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
  - Clean, readable documentation
  - Three-panel layout
  - Advanced filtering

- **📄 OpenAPI JSON**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)
  - Raw OpenAPI 3.0 specification
  - For code generation and integration

### Import into Postman

You can import the API directly into Postman using:
```
http://localhost:8000/openapi.json
```

---

## 🔐 Authentication Overview

The API uses **JWT (JSON Web Tokens)** for authentication with role-based access control.

### Authentication Flow

1. **Login** → Get JWT token
2. **Store Token** → Save securely in client
3. **Include Token** → Add to `Authorization` header for protected endpoints
4. **Token Expires** → Re-authenticate after 30 minutes

### User Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| `admin` | System administrator | Full access including user management |
| `supervisor` | Production supervisor | Production oversight and reporting |
| `operator` | Production operator | Production monitoring and control |
| `viewer` | Read-only user | View production data only |

---

## 🔑 Authentication Endpoints

### 🔐 POST `/api/auth/login`

**Authenticate user and receive JWT token**

> 📖 **[Detailed Documentation](../api_endpoints/auth_login.md)**

**Request:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
         "username": "admin",
         "password": "admin123"
     }'
```

**Response (200 OK):**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@company.com",
        "full_name": "Administrator",
        "role": "admin",
        "is_active": true
    }
}
```

**Default Admin Account:**
- Username: `admin`
- Password: `admin123`

---

### 👤 GET `/api/auth/me`

**Get current user profile information**

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Request:**
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
     -H "Authorization: Bearer <your-jwt-token>"
```

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "admin",
    "email": "admin@company.com",
    "full_name": "Administrator",
    "role": "admin",
    "is_active": true,
    "last_login": "2024-01-01T12:00:00Z",
    "created_at": "2024-01-01T10:00:00Z"
}
```

---

## 🏭 Production Data Endpoints

### 📊 GET `/api/production/current`

**Get current real-time production status**

> 📖 **[Detailed Documentation](../api_endpoints/production_current.md)**

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Request:**
```bash
curl -X GET "http://localhost:8000/api/production/current" \
     -H "Authorization: Bearer <your-jwt-token>"
```

**Response (200 OK):**
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

**Quality Status Values:**
- `OK` - Product passed quality checks
- `NOK` - Product failed quality checks  
- `PENDING` - Quality check in progress

**Line Status Values:**
- `RUNNING` - Normal production operation
- `STOPPED` - Production line stopped
- `ERROR` - Error condition detected
- `MAINTENANCE` - Maintenance mode active

---

### 📈 GET `/api/production/history`

**Query historical production data with filtering**

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Query Parameters:**

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `start_date` | string | No | Start date (ISO 8601 format) | `2024-01-01T00:00:00Z` |
| `end_date` | string | No | End date (ISO 8601 format) | `2024-01-01T23:59:59Z` |
| `limit` | integer | No | Max records (1-1000, default: 100) | `50` |

**Request:**
```bash
curl -X GET "http://localhost:8000/api/production/history?start_date=2024-01-01T00:00:00Z&limit=50" \
     -H "Authorization: Bearer <your-jwt-token>"
```

**Response (200 OK):**
```json
{
    "status": "success",
    "data": [
        {
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
    ],
    "count": 1
}
```

---

### 📊 GET `/api/production/stats`

**Get production statistics and quality metrics**

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | No | Statistics start date (ISO 8601) |
| `end_date` | string | No | Statistics end date (ISO 8601) |

**Request:**
```bash
curl -X GET "http://localhost:8000/api/production/stats?start_date=2024-01-01T00:00:00Z" \
     -H "Authorization: Bearer <your-jwt-token>"
```

**Response (200 OK):**
```json
{
    "status": "success",
    "data": {
        "total_products": 1000,
        "quality_ok_count": 950,
        "quality_nok_count": 30,
        "quality_pending_count": 20,
        "quality_rate_percentage": 95.0,
        "average_cycle_time_ms": 2450.5,
        "last_update": "2024-01-01T12:00:00Z"
    }
}
```

---

### 🔄 POST `/api/production/batch/new`

**Start a new production batch**

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Required Role:** `operator` or higher

**Request:**
```bash
curl -X POST "http://localhost:8000/api/production/batch/new" \
     -H "Authorization: Bearer <your-jwt-token>"
```

**Response (201 Created):**
```json
{
    "status": "success",
    "message": "New batch started successfully",
    "batch_id": "BATCH_20240101_002",
    "timestamp": "2024-01-01T12:30:00Z"
}
```

---

## ⚙️ System Health & Diagnostics

### 🏥 GET `/api/system/health`

**System health check - No authentication required**

**Request:**
```bash
curl -X GET "http://localhost:8000/api/system/health"
```

**Response (200 OK):**
```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00Z",
    "services": {
        "modbus_server": "running",
        "database": "connected",
        "api": "running",
        "production_line": "healthy"
    },
    "current_batch": "BATCH_20240101_001"
}
```

**Health Status Values:**
- `healthy` - All systems operational
- `degraded` - Some non-critical issues
- `unhealthy` - Critical systems failing

---

### 🔧 GET `/api/system/debug/recent-data`

**Get diagnostic information for troubleshooting**

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Request:**
```bash
curl -X GET "http://localhost:8000/api/system/debug/recent-data" \
     -H "Authorization: Bearer <your-jwt-token>"
```

**Response (200 OK):**
```json
{
    "status": "success",
    "timestamp": "2024-01-01T12:00:00Z",
    "recent_data": [
        {
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
    ],
    "system_info": {
        "timestamp": "2024-01-01T12:00:00Z",
        "active_user": "admin",
        "user_role": "admin",
        "recent_records_count": 10,
        "system_uptime": "Running",
        "memory_usage": "Normal",
        "connection_status": "Connected"
    }
}
```

---

## 👥 Administration Endpoints

**(Admin access required for all endpoints)**

### 👥 GET `/api/admin/users`

**List all system users**

**Headers:**
```
Authorization: Bearer <admin-jwt-token>
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | integer | 0 | Records to skip (pagination) |
| `limit` | integer | 100 | Max records (1-1000) |

**Request:**
```bash
curl -X GET "http://localhost:8000/api/admin/users?skip=0&limit=10" \
     -H "Authorization: Bearer <admin-jwt-token>"
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "username": "admin",
        "email": "admin@company.com",
        "full_name": "Administrator",
        "role": "admin",
        "is_active": true,
        "last_login": "2024-01-01T12:00:00Z",
        "created_at": "2024-01-01T10:00:00Z"
    }
]
```

---

### ➕ POST `/api/admin/users`

**Create a new user account**

**Headers:**
```
Authorization: Bearer <admin-jwt-token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "username": "operator1",
    "email": "operator1@company.com",
    "password": "secure_password123",
    "full_name": "Production Operator",
    "role": "operator"
}
```

**Request:**
```bash
curl -X POST "http://localhost:8000/api/admin/users" \
     -H "Authorization: Bearer <admin-jwt-token>" \
     -H "Content-Type: application/json" \
     -d '{
         "username": "operator1",
         "email": "operator1@company.com",
         "password": "secure_password123",
         "full_name": "Production Operator",
         "role": "operator"
     }'
```

**Response (201 Created):**
```json
{
    "id": 2,
    "username": "operator1",
    "email": "operator1@company.com",
    "full_name": "Production Operator",
    "role": "operator",
    "is_active": true,
    "last_login": null,
    "created_at": "2024-01-01T12:30:00Z"
}
```

---

## 🌐 WebSocket API

### 📡 WebSocket `/ws/production`

**Real-time production data streaming**

**Connection URL:**
```
ws://localhost:8000/ws/production
```

**Message Types Sent:**
- `connection` - Connection confirmation
- `production_data` - Real-time production data
- `pong` - Response to client ping

**Message Types Received:**
- `ping` - Heartbeat from client

**JavaScript Example:**
```javascript
const socket = new WebSocket('ws://localhost:8000/ws/production');

socket.onopen = function(event) {
    console.log('Connected to production WebSocket');
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'connection':
            console.log('Connection confirmed:', data);
            break;
        case 'production_data':
            updateProductionDisplay(data.data);
            break;
        case 'pong':
            console.log('Server pong received');
            break;
    }
};

socket.onerror = function(error) {
    console.error('WebSocket error:', error);
};

socket.onclose = function(event) {
    console.log('WebSocket connection closed');
};

// Send heartbeat
function sendHeartbeat() {
    if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({type: 'ping'}));
    }
}

setInterval(sendHeartbeat, 30000); // Every 30 seconds
```

---

## 🚨 Error Handling

### Standard Error Response Format

```json
{
    "detail": "Error description"
}
```

### HTTP Status Codes

| Code | Description | When Used |
|------|-------------|-----------|
| `200` | OK | Successful request |
| `201` | Created | Resource created successfully |
| `400` | Bad Request | Invalid request data |
| `401` | Unauthorized | Authentication required/failed |
| `403` | Forbidden | Insufficient permissions |
| `404` | Not Found | Resource not found |
| `422` | Validation Error | Request validation failed |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Server error |
| `503` | Service Unavailable | System unavailable |

### Validation Errors (422)

```json
{
    "detail": [
        {
            "loc": ["body", "username"],
            "msg": "ensure this value has at least 3 characters",
            "type": "value_error.any_str.min_length"
        }
    ]
}
```

---

## 🔒 Security

### Authentication Security
- **JWT Tokens**: Stateless authentication
- **Token Expiration**: 30 minutes for security
- **Password Hashing**: bcrypt with salt
- **Rate Limiting**: Prevents brute force attacks

### API Security
- **CORS Configuration**: Controlled origin access
- **Input Validation**: Pydantic model validation
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: JSON response sanitization

### Best Practices
- Use HTTPS in production
- Store tokens securely (not in localStorage for sensitive apps)
- Implement proper error handling
- Log security events
- Regular security audits

---

## 📊 Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|---------|
| `/api/auth/login` | 5 requests | 1 minute |
| All other endpoints | 100 requests | 1 minute |

---

## 🛠️ SDKs and Examples

### Python SDK Example

```python
import requests
from typing import Optional

class ProductionAPI:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {'Authorization': f'Bearer {token}'}
    
    def get_current_production(self) -> dict:
        response = requests.get(f"{self.base_url}/api/production/current", headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_production_history(self, start_date: str = None, end_date: str = None, limit: int = 100) -> dict:
        params = {'limit': limit}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
            
        response = requests.get(f"{self.base_url}/api/production/history", headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

# Usage
api = ProductionAPI("http://localhost:8000", "your-jwt-token")
current = api.get_current_production()
print(f"Current production: {current}")
```

### JavaScript SDK Example

```javascript
class ProductionAPI {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl;
        this.token = token;
    }
    
    async getCurrentProduction() {
        const response = await fetch(`${this.baseUrl}/api/production/current`, {
            headers: {
                'Authorization': `Bearer ${this.token}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    async getProductionHistory(startDate = null, endDate = null, limit = 100) {
        const params = new URLSearchParams({limit: limit.toString()});
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        const response = await fetch(`${this.baseUrl}/api/production/history?${params}`, {
            headers: {
                'Authorization': `Bearer ${this.token}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
}

// Usage
const api = new ProductionAPI('http://localhost:8000', 'your-jwt-token');
api.getCurrentProduction()
    .then(data => console.log('Current production:', data))
    .catch(error => console.error('Error:', error));
```

---

## 📚 Additional Resources

- **[System Architecture](architecture.md)** - System design and components
- **[Deployment Guide](deployment.md)** - Production deployment
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions
- **[WebSocket Guide](../api_endpoints/websocket_production.md)** - Real-time data integration

---

**🔗 Quick Links:**
- [Interactive API Docs (Swagger)](http://localhost:8000/docs)
- [Alternative Docs (ReDoc)](http://localhost:8000/redoc)
- [Health Check](http://localhost:8000/api/system/health)
- [System Dashboard](http://localhost:8000/)
- [Real-time Monitor](http://localhost:8000/client) 