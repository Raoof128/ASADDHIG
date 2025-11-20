# Deployment Guide

This guide covers production deployment strategies for the Sovereign AI Gateway.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Docker Compose Deployment](#docker-compose-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Production Considerations](#production-considerations)
- [Monitoring & Observability](#monitoring--observability)
- [Scaling](#scaling)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required

- Docker 20.10+ and Docker Compose 2.0+
- 8GB+ RAM (for local LLM)
- 20GB+ disk space
- Network access (for cloud LLM, if used)

### Optional

- Kubernetes 1.24+ (for K8s deployment)
- Helm 3.8+ (for Helm charts)
- Reverse proxy (nginx, traefik)
- Monitoring stack (Prometheus, Grafana)

---

## Docker Compose Deployment

### Quick Start

```bash
# Clone repository
git clone <repository-url>
cd sovereign_ai_gateway

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Production Configuration

Create a `.env` file:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o

# Ollama Configuration
OLLAMA_MODEL=llama3

# Gateway Configuration
PII_THRESHOLD=0.3
GATEWAY_LOG_LEVEL=INFO

# Security
ENABLE_CORS=true
CORS_ORIGINS=https://yourdomain.com,https://dashboard.yourdomain.com
MAX_REQUEST_SIZE=1048576

# Rate Limiting (future)
RATE_LIMIT_ENABLED=false
RATE_LIMIT_PER_MINUTE=60
```

### Health Checks

```bash
# Gateway health
curl http://localhost:8000/health

# Dashboard
curl http://localhost:8501/_stcore/health

# Ollama
curl http://localhost:11434/api/tags
```

---

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Helm 3.8+ (optional)

### Using kubectl

```bash
# Create namespace
kubectl create namespace sovereign-ai

# Create secrets
kubectl create secret generic gateway-secrets \
  --from-literal=openai-api-key=your_key \
  -n sovereign-ai

# Deploy gateway
kubectl apply -f k8s/gateway-deployment.yaml -n sovereign-ai

# Deploy dashboard
kubectl apply -f k8s/dashboard-deployment.yaml -n sovereign-ai

# Deploy Ollama
kubectl apply -f k8s/ollama-deployment.yaml -n sovereign-ai

# Expose services
kubectl apply -f k8s/services.yaml -n sovereign-ai
```

### Using Helm (if charts provided)

```bash
# Install
helm install sovereign-ai ./helm/sovereign-ai \
  --namespace sovereign-ai \
  --create-namespace \
  --set openai.apiKey=your_key

# Upgrade
helm upgrade sovereign-ai ./helm/sovereign-ai \
  --namespace sovereign-ai

# Uninstall
helm uninstall sovereign-ai --namespace sovereign-ai
```

---

## Production Considerations

### Security

1. **Authentication**
   - Implement API key authentication
   - Use OAuth2/JWT for user authentication
   - Enable HTTPS/TLS

2. **Network Security**
   - Use reverse proxy (nginx/traefik)
   - Restrict CORS origins
   - Implement rate limiting
   - Use network policies (Kubernetes)

3. **Secrets Management**
   - Use Kubernetes Secrets
   - Use AWS Secrets Manager / HashiCorp Vault
   - Never commit secrets to repository

4. **Audit Logging**
   - Ship logs to centralized system (ELK, Splunk)
   - Encrypt logs at rest
   - Set retention policies

### Performance

1. **Scaling**
   - Horizontal scaling for gateway API
   - Multiple Ollama instances for local LLM
   - Load balancing

2. **Caching**
   - Redis for session management
   - Response caching for common prompts
   - PII detection result caching

3. **Resource Limits**
   - Set CPU/memory limits
   - Configure timeouts appropriately
   - Monitor resource usage

### High Availability

1. **Redundancy**
   - Multiple gateway instances
   - Multiple Ollama instances
   - Database replication (if using DB)

2. **Health Checks**
   - Liveness probes
   - Readiness probes
   - Startup probes

3. **Disaster Recovery**
   - Regular backups
   - Disaster recovery plan
   - Failover procedures

---

## Monitoring & Observability

### Metrics

Expose Prometheus metrics (future enhancement):

```python
# Example metrics endpoint
@app.get("/metrics")
async def metrics():
    return {
        "requests_total": request_count,
        "requests_by_route": route_counts,
        "pii_detections": pii_count,
        "average_processing_time": avg_time,
    }
```

### Logging

- Structured JSON logging
- Log levels: DEBUG, INFO, WARNING, ERROR
- Centralized log aggregation

### Tracing

- OpenTelemetry integration (future)
- Distributed tracing
- Request flow visualization

### Alerting

Set up alerts for:
- High error rates
- High PII detection rates
- Service downtime
- Resource exhaustion

---

## Scaling

### Horizontal Scaling

```yaml
# Gateway scaling
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gateway-api
spec:
  replicas: 3  # Scale to 3 instances
  ...
```

### Load Balancing

Use Kubernetes Service or external load balancer:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: gateway-service
spec:
  type: LoadBalancer
  selector:
    app: gateway-api
  ports:
    - port: 80
      targetPort: 8000
```

---

## Troubleshooting

### Common Issues

1. **Ollama not responding**
   ```bash
   # Check Ollama logs
   docker logs sovereign_ollama
   
   # Restart Ollama
   docker restart sovereign_ollama
   ```

2. **Gateway API errors**
   ```bash
   # Check gateway logs
   docker logs sovereign_gateway_api
   
   # Verify configuration
   docker exec sovereign_gateway_api env | grep -E "OPENAI|OLLAMA"
   ```

3. **High memory usage**
   - Reduce Ollama model size
   - Scale horizontally
   - Adjust resource limits

### Debug Mode

Enable debug logging:

```bash
export GATEWAY_LOG_LEVEL=DEBUG
docker-compose up -d
```

---

## Backup & Recovery

### Audit Logs

```bash
# Backup audit logs
kubectl exec -it <pod-name> -- tar czf /tmp/audit-logs.tar.gz /app/sovereign_audit.log

# Restore
kubectl cp audit-logs.tar.gz <pod-name>:/tmp/
kubectl exec -it <pod-name> -- tar xzf /tmp/audit-logs.tar.gz -C /app/
```

### Configuration

- Version control all configuration
- Use ConfigMaps (Kubernetes)
- Document all changes

---

## Next Steps

- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure alerting
- [ ] Implement authentication
- [ ] Set up CI/CD pipeline
- [ ] Configure backup procedures
- [ ] Document runbooks

---

**Last Updated**: 2024-01-15

