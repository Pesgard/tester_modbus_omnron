# POST /api/auth/login

🔐 **User Authentication Endpoint**

Authenticate a user and receive a JWT access token for subsequent API calls.

## Overview

This endpoint validates user credentials and returns a JWT token that must be included in the `Authorization` header for protected endpoints.

## Request

### Method & URL
```http
POST /api/auth/login
Content-Type: application/json
```

### Request Body

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `username` | string | ✅ | Username for authentication (3-50 chars) | `"admin"` |
| `password` | string | ✅ | User password (6-100 chars) | `"admin123"` |

### Example Request

```http
POST /api/auth/login HTTP/1.1
Content-Type: application/json

{
    "username": "admin",
    "password": "admin123"
}
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
         "username": "admin",
         "password": "admin123"
     }'
```

## Response

### Success Response (200 OK)

```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJhZG1pbiIsImV4cCI6MTY0MzQ4MDQwMH0.xyz...",
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

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `access_token` | string | JWT access token for authentication |
| `token_type` | string | Token type (always "bearer") |
| `expires_in` | integer | Token expiration time in seconds (1800 = 30 minutes) |
| `user` | object | Authenticated user information |
| `user.id` | integer | Unique user identifier |
| `user.username` | string | Username |
| `user.email` | string | User email address |
| `user.full_name` | string | Full name of the user |
| `user.role` | string | User role (admin, supervisor, operator, viewer) |
| `user.is_active` | boolean | Whether the user account is active |

## Error Responses

### 401 Unauthorized
```json
{
    "detail": "Incorrect username or password"
}
```

### 422 Validation Error
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

### 500 Internal Server Error
```json
{
    "detail": "Internal server error"
}
```

## Authentication Flow

1. **Submit Credentials**: Send username and password to this endpoint
2. **Receive Token**: Get JWT token and user information in response
3. **Store Token**: Save the token securely in your client
4. **Use Token**: Include token in Authorization header for protected endpoints:
   ```
   Authorization: Bearer <your-token-here>
   ```

## Token Usage

Once you receive the access token, include it in the Authorization header for subsequent API calls:

```http
GET /api/production/current HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Default Accounts

The system comes with a default admin account:

- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `admin`

> ⚠️ **Security Note**: Change the default admin password immediately in production environments.

## Security Features

- **Password Hashing**: Passwords are securely hashed using bcrypt
- **JWT Tokens**: Stateless authentication with configurable expiration
- **Rate Limiting**: 5 login attempts per minute per IP address
- **Audit Logging**: All login attempts are logged for security monitoring

## Token Expiration

- **Default Expiration**: 30 minutes (1800 seconds)
- **Refresh**: No automatic refresh - users must re-authenticate when token expires
- **Security**: Short expiration time reduces security risk if token is compromised

## Error Handling

- **Invalid Credentials**: Returns 401 with generic error message
- **Account Disabled**: Returns 401 (same as invalid credentials for security)
- **Validation Errors**: Returns 422 with detailed field-level errors
- **Server Errors**: Returns 500 with generic error message

## Rate Limiting

- **Limit**: 5 authentication attempts per minute per IP address
- **Purpose**: Prevents brute force attacks
- **Response**: Returns 429 Too Many Requests when exceeded

## JavaScript Example

```javascript
async function login(username, password) {
    try {
        const response = await fetch('http://localhost:8000/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Store token for future requests
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('user_info', JSON.stringify(data.user));
        
        return data;
    } catch (error) {
        console.error('Login failed:', error);
        throw error;
    }
}
```

## Python Example

```python
import requests

def login(username: str, password: str) -> dict:
    """Authenticate user and return token information."""
    url = "http://localhost:8000/api/auth/login"
    
    payload = {
        "username": username,
        "password": password
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# Usage
try:
    auth_data = login("admin", "admin123")
    token = auth_data["access_token"]
    user_info = auth_data["user"]
    print(f"Logged in as {user_info['username']} ({user_info['role']})")
except requests.exceptions.HTTPError as e:
    print(f"Login failed: {e}")
``` 