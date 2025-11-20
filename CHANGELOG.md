# Changelog

All notable changes to the Sovereign AI Gateway project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-15

### Added

#### Core Features
- **FastAPI Gateway** - Main API server with REST endpoints
- **PII Inspector** - Australian identifier detection (Medicare, TFN, driver's licence, mobile, etc.)
- **Intelligent Router** - Automatic cloud vs. sovereign routing based on PII sensitivity
- **Compliance Logger** - Structured audit logging for ISO 27001 / ASD Essential 8
- **Streamlit Dashboard** - Real-time visualization and monitoring

#### Documentation
- Comprehensive README.md with architecture diagrams
- ARCHITECTURE.md with detailed design documentation
- CONTRIBUTING.md with contribution guidelines
- CODE_OF_CONDUCT.md for community standards
- SECURITY.md with security policy and best practices
- QUICKSTART.md for rapid setup
- API documentation via FastAPI OpenAPI/Swagger

#### Configuration
- Centralized configuration management (`gateway/config.py`)
- Environment variable support
- Configurable PII threshold
- Configurable timeouts and limits

#### Testing
- Unit tests for PII inspector
- Unit tests for routing logic
- Test fixtures and examples

#### Deployment
- Docker Compose configuration
- Dockerfiles for gateway and dashboard
- Health checks for all services
- Volume persistence for logs

### Security

- Input validation via Pydantic models
- Request size limits (configurable)
- CORS configuration (configurable)
- PII redaction in logs
- Privacy-preserving audit logs (no prompt content)

### Performance

- Async FastAPI endpoints
- Efficient regex-based PII detection
- Configurable timeouts
- Processing time tracking

### Known Limitations

- No authentication/authorization (planned for v1.1.0)
- No rate limiting (planned for v1.1.0)
- File-based logging (database planned for v1.2.0)
- Single instance deployment (scaling planned for v1.2.0)

## [Unreleased]

### Planned for v1.1.0

- [ ] Authentication (API keys, OAuth2, JWT)
- [ ] Rate limiting middleware
- [ ] Enhanced security headers
- [ ] Request signing/verification
- [ ] IP whitelisting

### Planned for v1.2.0

- [ ] Database-backed audit logging
- [ ] Horizontal scaling support
- [ ] Redis caching layer
- [ ] Prometheus metrics
- [ ] Kubernetes manifests

### Planned for v1.3.0

- [ ] Enhanced PII detection (Presidio integration)
- [ ] Multi-model routing
- [ ] Cost optimization
- [ ] Quality-based routing

---

## Version History

- **1.0.0** - Initial release with core functionality

---

For detailed commit history, see [GitHub commits](https://github.com/your-org/sovereign_ai_gateway/commits/main).

