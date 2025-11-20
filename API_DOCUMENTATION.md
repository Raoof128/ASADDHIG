# API Documentation

Complete API reference for the Sovereign AI Gateway.

---

## Base URL

```
http://localhost:8000  # Development
https://api.yourdomain.com  # Production
```

---

## Authentication

Currently, the API does not require authentication. **For production deployments, implement authentication.**

Planned authentication methods:
- API Key (Header: `X-API-Key`)
- OAuth2 Bearer Token
- JWT Token

---

## Endpoints

### Health Check

#### `GET /`

Basic health check endpoint.

**Response:**
```json
{
  "service": "Sovereign AI Gateway",
  "status": "operational",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

#### `GET /health`

Detailed health check with component status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1705312800.0,
  "components": {
    "inspector": "operational",
    "router": "operational",
    "audit_logger": "operational"
  },
  "configuration": {
    "pii_threshold": 0.3,
    "openai_configured": true,
    "ollama_url": "http://ollama:11434"
  }
}
```

---

### Gateway Endpoint

#### `POST /gateway`

Main endpoint for AI inference requests.

**Request Body:**
```json
{
  "prompt": "What is the capital of Australia?",
  "user_id": "optional_user_id",
  "session_id": "optional_session_id"
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | User prompt text (max 1MB) |
| `user_id` | string | No | Optional user identifier |
| `session_id` | string | No | Optional session identifier |

**Response:**
```json
{
  "response": "The capital of Australia is Canberra.",
  "route": "cloud",
  "pii_score": 0.0,
  "pii_detected": [],
  "model_used": "gpt-4o",
  "timestamp": "2024-01-15T10:30:00.123456",
  "processing_time_ms": 1250.5
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `response` | string | AI-generated response text |
| `route` | string | Routing decision: "cloud" or "sovereign" |
| `pii_score` | float | PII sensitivity score (0.0-1.0) |
| `pii_detected` | array | List of detected PII objects |
| `model_used` | string | Model that generated the response |
| `timestamp` | string | ISO 8601 timestamp |
| `processing_time_ms` | float | Processing time in milliseconds |

**PII Detection Object:**
```json
{
  "type": "medicare",
  "value": "12****890",
  "confidence": 0.95,
  "position": [20, 33]
}
```

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request (empty prompt) |
| 413 | Request Entity Too Large |
| 422 | Validation Error |
| 500 | Internal Server Error |

**Example Requests:**

```bash
# Clean prompt (routes to cloud)
curl -X POST http://localhost:8000/gateway \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is the capital of Australia?",
    "user_id": "user_123"
  }'

# Sensitive prompt (routes to local)
curl -X POST http://localhost:8000/gateway \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "My Medicare number is 1234 567 890"
  }'
```

---

### Audit Logs

#### `GET /audit/recent`

Retrieve recent audit log entries.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 50 | Number of entries to return (1-1000) |

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2024-01-15T10:30:00.123456",
      "route": "sovereign",
      "pii_score": 0.85,
      "pii_types": ["medicare", "tfn"],
      "model_used": "llama3 (local)",
      "user_id": "user_123",
      "session_id": "session_456",
      "ip_address": "192.168.1.100",
      "prompt_length": 150,
      "response_length": 500,
      "processing_time_ms": 1250.5,
      "sovereignty_enforced": true
    }
  ],
  "count": 1,
  "limit": 50
}
```

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid limit) |
| 500 | Internal Server Error |

**Example:**

```bash
curl http://localhost:8000/audit/recent?limit=10
```

---

## OpenAPI/Swagger Documentation

Interactive API documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

## Error Responses

### Standard Error Format

```json
{
  "error": "Error type",
  "message": "Human-readable error message",
  "details": {}
}
```

### Error Types

1. **Validation Error (422)**
```json
{
  "error": "Validation error",
  "details": [
    {
      "loc": ["body", "prompt"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ],
  "message": "Invalid request format"
}
```

2. **Internal Server Error (500)**
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

---

## Rate Limiting

Currently not implemented. **For production, implement rate limiting.**

Planned limits:
- 60 requests per minute per IP
- 1000 requests per hour per user
- Configurable via environment variables

---

## Best Practices

1. **Request Size**
   - Keep prompts under 1MB
   - Use appropriate timeout values

2. **Error Handling**
   - Implement retry logic with exponential backoff
   - Handle timeout errors gracefully
   - Log errors for debugging

3. **Security**
   - Never send sensitive data in URLs
   - Use HTTPS in production
   - Implement authentication

4. **Performance**
   - Cache responses when appropriate
   - Use connection pooling
   - Monitor response times

---

## SDK Examples

### Python

```python
import requests

def call_gateway(prompt: str, user_id: str = None):
    url = "http://localhost:8000/gateway"
    payload = {
        "prompt": prompt,
        "user_id": user_id
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    return response.json()

# Usage
result = call_gateway("What is the capital of Australia?")
print(f"Response: {result['response']}")
print(f"Route: {result['route']}")
print(f"PII Score: {result['pii_score']}")
```

### JavaScript/TypeScript

```typescript
async function callGateway(prompt: string, userId?: string) {
  const response = await fetch('http://localhost:8000/gateway', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      prompt,
      user_id: userId,
    }),
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
}

// Usage
const result = await callGateway('What is the capital of Australia?');
console.log(`Response: ${result.response}`);
console.log(`Route: ${result.route}`);
console.log(`PII Score: ${result.pii_score}`);
```

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for API version history and breaking changes.

---

**Last Updated**: 2024-01-15

