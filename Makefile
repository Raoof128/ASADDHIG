.PHONY: help build up down logs test clean

help:
	@echo "Sovereign AI Gateway - Makefile Commands"
	@echo ""
	@echo "  make build    - Build Docker images"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - View logs from all services"
	@echo "  make test     - Run test suite"
	@echo "  make clean    - Remove containers and volumes"
	@echo "  make pull-ollama - Pull Ollama model"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	pytest tests/ -v

clean:
	docker-compose down -v
	rm -f sovereign_audit.log

pull-ollama:
	docker exec sovereign_ollama ollama pull $(OLLAMA_MODEL) || echo "Set OLLAMA_MODEL environment variable"

