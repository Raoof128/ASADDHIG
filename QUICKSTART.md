# 🚀 Quick Start Guide

Get the Sovereign AI Gateway running in 5 minutes.

## Prerequisites

- Docker and Docker Compose installed
- 8GB+ RAM (for local LLM)
- OpenAI API key (optional, for cloud routing)

## Step 1: Clone and Navigate

```bash
cd sovereign_ai_gateway
```

## Step 2: Configure (Optional)

Create a `.env` file:

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY if you want cloud routing
```

## Step 3: Start Services

```bash
docker-compose up -d
```

This will:
- Build the FastAPI gateway
- Build the Streamlit dashboard  
- Start Ollama and pull the model (this may take a few minutes)

## Step 4: Wait for Services

Check service status:

```bash
docker-compose ps
```

Wait until all services show "healthy" status.

## Step 5: Access Dashboard

Open your browser: **http://localhost:8501**

## Step 6: Test the Gateway

### Via Dashboard
1. Enter a prompt in the text area
2. Click "Send to Gateway"
3. View the routing decision and response

### Via API

**Clean prompt (routes to cloud):**
```bash
curl -X POST http://localhost:8000/gateway \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the capital of Australia?"}'
```

**Sensitive prompt (routes to local):**
```bash
curl -X POST http://localhost:8000/gateway \
  -H "Content-Type: application/json" \
  -d '{"prompt": "My Medicare number is 1234 567 890"}'
```

## Troubleshooting

### Ollama model not pulling
```bash
docker exec -it sovereign_ollama ollama pull llama3
```

### Check logs
```bash
docker-compose logs -f
```

### Restart services
```bash
docker-compose restart
```

### Full reset
```bash
docker-compose down -v
docker-compose up -d
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Review [examples/](examples/) for sample requests
- Run tests: `pytest tests/`
- Check audit logs: `tail -f sovereign_audit.log`

## Architecture Overview

```
User → Dashboard (8501) → Gateway API (8000) → Inspector → Router
                                                    ↓
                                    ┌──────────────┴──────────────┐
                                    ↓                            ↓
                              Cloud (OpenAI)              Local (Ollama)
```

---

**🛡️ Your Sovereign AI Gateway is now operational!**

