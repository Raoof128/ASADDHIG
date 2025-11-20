# Architecture Documentation

## Overview

The Sovereign AI Gateway is a hybrid inference gateway designed to enforce Australian data sovereignty by automatically routing sensitive prompts to local LLMs while allowing non-sensitive prompts to use cloud AI services.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Layer                            │
│  ┌──────────────┐              ┌──────────────┐           │
│  │   Web UI     │              │   API Client  │           │
│  │ (Streamlit)  │              │  (REST/HTTP)  │           │
│  └──────┬───────┘              └──────┬───────┘           │
└─────────┼─────────────────────────────┼───────────────────┘
           │                             │
           └─────────────┬───────────────┘
                         │
           ┌─────────────▼───────────────┐
           │    FastAPI Gateway          │
           │  ┌───────────────────────┐   │
           │  │  Request Handler      │   │
           │  │  - Input Validation   │   │
           │  │  - Error Handling     │   │
           │  └───────────┬───────────┘   │
           │              │               │
           │  ┌───────────▼───────────┐   │
           │  │  PII Inspector        │   │
           │  │  - Pattern Matching   │   │
           │  │  - Validation         │   │
           │  │  - Scoring            │   │
           │  └───────────┬───────────┘   │
           │              │               │
           │  ┌───────────▼───────────┐   │
           │  │  Router               │   │
           │  │  - Decision Logic     │   │
           │  │  - LLM Invocation     │   │
           │  └───────────┬───────────┘   │
           │              │               │
           │  ┌───────────▼───────────┐   │
           │  │  Compliance Logger   │   │
           │  │  - Audit Trail        │   │
           │  │  - Structured Logs    │   │
           │  └───────────────────────┘   │
           └─────────────┬─────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                  │
┌───────▼────────┐              ┌─────────▼────────┐
│  Cloud LLM     │              │  Local LLM       │
│  (OpenAI API)  │              │  (Ollama)        │
└────────────────┘              └──────────────────┘
```

## Component Details

### 1. FastAPI Gateway (`gateway/gateway.py`)

**Responsibilities:**
- HTTP request/response handling
- Input validation via Pydantic models
- Error handling and exception management
- CORS middleware configuration
- Health check endpoints

**Key Endpoints:**
- `POST /gateway` - Main inference endpoint
- `GET /health` - Health check
- `GET /audit/recent` - Recent audit logs

**Design Decisions:**
- FastAPI chosen for async support, automatic OpenAPI docs, and type safety
- Pydantic models ensure input validation
- CORS middleware allows dashboard access (should be restricted in production)

### 2. PII Inspector (`gateway/inspector.py`)

**Responsibilities:**
- Pattern-based detection of Australian identifiers
- Checksum validation for Medicare and TFN
- Keyword-based sensitive context detection
- PII scoring algorithm
- Value redaction for logging

**Detection Patterns:**
- Medicare: 10-digit with checksum
- TFN: 8-9 digit with weighted checksum
- Driver's Licence: State-specific formats
- Mobile: 04XX XXX XXX pattern
- Email, Credit Card, BSB, Bank Account

**Scoring Algorithm:**
```
PII Score = min(keyword_score + pattern_score, 1.0)
- keyword_score: min(keyword_matches * 0.15, 0.6)
- pattern_score: min(detections * 0.2, 0.8)
- Boost: +0.1 if multiple PII types detected
```

**Design Decisions:**
- Regex-based for performance and simplicity
- Can be enhanced with Presidio or spaCy NER
- Checksum validation increases confidence
- Redaction preserves privacy in logs

### 3. Router (`gateway/router.py`)

**Responsibilities:**
- Routing decision based on PII score
- Cloud LLM invocation (OpenAI)
- Local LLM invocation (Ollama)
- Error handling and fallback
- Processing time tracking

**Routing Logic:**
```python
if pii_score >= threshold OR len(pii_detections) > 0:
    route = "sovereign"  # Local LLM
else:
    route = "cloud"      # OpenAI
```

**Design Decisions:**
- Configurable threshold via environment variable
- Fallback to local if cloud unavailable
- Timeout handling for both APIs
- Error messages returned in response (consider logging separately)

### 4. Compliance Logger (`gateway/logging_utils.py`)

**Responsibilities:**
- Structured JSON logging
- Human-readable summaries
- Log file management
- Log retrieval for dashboard

**Log Format:**
```json
{
  "timestamp": "ISO8601",
  "route": "cloud|sovereign",
  "pii_score": 0.0-1.0,
  "pii_types": ["medicare", "tfn"],
  "model_used": "gpt-4o",
  "user_id": "optional",
  "session_id": "optional",
  "ip_address": "optional",
  "prompt_length": 150,
  "response_length": 500,
  "processing_time_ms": 1250.5,
  "sovereignty_enforced": true
}
```

**Design Decisions:**
- JSON format for structured querying
- No prompt content stored (privacy-preserving)
- Dual format: JSON + human-readable
- File-based (can be enhanced with database)

### 5. Streamlit Dashboard (`dashboard/app.py`)

**Responsibilities:**
- User interface for prompt submission
- Real-time visualization of routing decisions
- Audit log viewer
- Statistics and metrics

**Design Decisions:**
- Streamlit for rapid UI development
- Real-time updates via API polling
- Visual indicators for route decisions
- Responsive layout with columns

## Data Flow

### Request Flow

1. **Client** sends POST request to `/gateway` with prompt
2. **Gateway** validates request using Pydantic model
3. **Inspector** analyzes prompt for PII:
   - Pattern matching
   - Validation (checksums)
   - Scoring
4. **Router** makes routing decision:
   - If sensitive → Call Ollama API
   - If clean → Call OpenAI API
5. **Logger** records audit entry
6. **Gateway** returns response with metadata

### Response Format

```json
{
  "response": "AI generated text",
  "route": "cloud|sovereign",
  "pii_score": 0.75,
  "pii_detected": [
    {
      "type": "medicare",
      "value": "12****890",
      "confidence": 0.95,
      "position": [20, 33]
    }
  ],
  "model_used": "llama3 (local)",
  "timestamp": "2024-01-15T10:30:00",
  "processing_time_ms": 1250.5
}
```

## Deployment Architecture

### Docker Compose Setup

```
┌─────────────────────────────────────────┐
│         Docker Network                  │
│  ┌──────────────┐                      │
│  │ Gateway API  │ :8000                │
│  │ (FastAPI)    │                      │
│  └──────┬───────┘                      │
│         │                               │
│  ┌──────▼───────┐                      │
│  │  Dashboard   │ :8501                │
│  │ (Streamlit)  │                      │
│  └──────┬───────┘                      │
│         │                               │
│  ┌──────▼───────┐                      │
│  │   Ollama     │ :11434               │
│  │ (Local LLM)  │                      │
│  └──────────────┘                      │
│                                         │
│  ┌──────────────┐                      │
│  │ Audit Log     │ (Volume)            │
│  │ sovereign_    │                      │
│  │ audit.log     │                      │
│  └──────────────┘                      │
└─────────────────────────────────────────┘
         │
         ▼
    External APIs
    (OpenAI Cloud)
```

### Service Dependencies

- **Gateway API** depends on Ollama (for local routing)
- **Dashboard** depends on Gateway API
- **Ollama** is standalone but must have model pulled

## Security Architecture

### Current Security Posture

- **Input Validation**: ✅ Pydantic models
- **Output Sanitization**: ✅ PII redaction
- **Audit Logging**: ✅ Comprehensive
- **Authentication**: ❌ Not implemented
- **Authorization**: ❌ Not implemented
- **Rate Limiting**: ❌ Not implemented
- **Encryption**: ⚠️ Depends on deployment (HTTPS)

### Security Boundaries

```
┌─────────────────────────────────────┐
│   Untrusted Network                 │
│   (Internet)                         │
└──────────────┬──────────────────────┘
               │ HTTPS (Production)
┌──────────────▼──────────────────────┐
│   Reverse Proxy                     │
│   (nginx/traefik)                   │
│   - TLS Termination                 │
│   - Rate Limiting                   │
│   - Authentication                  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Gateway API                       │
│   - Input Validation                │
│   - PII Detection                   │
│   - Routing Decision                │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────┐          ┌────▼────┐
│ Cloud  │          │  Local   │
│ (API)  │          │  (Ollama)│
└────────┘          └──────────┘
```

## Scalability Considerations

### Current Limitations

- Single instance deployment
- File-based logging (not scalable)
- No caching layer
- Synchronous processing

### Scaling Strategies

1. **Horizontal Scaling**
   - Multiple gateway instances behind load balancer
   - Stateless design supports this
   - Shared audit log storage (database)

2. **Caching**
   - Redis for session management
   - Response caching for common prompts
   - PII detection result caching

3. **Async Processing**
   - FastAPI supports async (partially implemented)
   - Queue system for long-running requests
   - WebSocket for streaming responses

4. **Database**
   - Replace file logging with database
   - PostgreSQL for audit logs
   - TimescaleDB for time-series metrics

## Monitoring & Observability

### Current State

- Basic health checks
- Audit logging
- Processing time tracking

### Recommended Enhancements

1. **Metrics**
   - Prometheus metrics endpoint
   - Request rate, latency, error rate
   - PII detection statistics
   - Routing decision distribution

2. **Tracing**
   - OpenTelemetry integration
   - Distributed tracing
   - Request flow visualization

3. **Alerting**
   - High PII score alerts
   - Error rate thresholds
   - Service health alerts

## Performance Characteristics

### Expected Latency

- **PII Detection**: < 10ms (regex-based)
- **Cloud API Call**: 500-2000ms (network dependent)
- **Local LLM Call**: 1000-5000ms (model dependent)
- **Total Gateway Overhead**: ~20ms

### Throughput

- **Current**: ~100 req/s (single instance, no optimization)
- **Potential**: 1000+ req/s (with async, caching, scaling)

## Future Enhancements

### Planned Improvements

1. **Enhanced PII Detection**
   - Presidio integration
   - Machine learning models
   - Custom entity recognition

2. **Advanced Routing**
   - Multi-model routing
   - Cost optimization
   - Quality-based routing

3. **Enterprise Features**
   - Multi-tenancy
   - Role-based access control
   - Policy engine
   - Compliance reporting

4. **Operational Excellence**
   - Kubernetes manifests
   - Helm charts
   - CI/CD pipelines
   - Automated testing

---

**Architecture Version**: 1.0  
**Last Updated**: 2024-01-15  
**Maintainer**: Sovereign AI Gateway Team

