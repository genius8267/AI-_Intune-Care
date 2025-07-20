.PHONY: help dev build test benchmark clean

# Default target
help:
	@echo "Intune-Care Makefile Commands"
	@echo "============================"
	@echo "make dev        - Start local development environment"
	@echo "make build      - Build all Docker images"
	@echo "make test       - Run all tests"
	@echo "make benchmark  - Run latency benchmarks"
	@echo "make clean      - Clean up containers and volumes"
	@echo "make logs       - Show logs from all services"
	@echo "make shell-api  - Open shell in API gateway container"

# Start development environment
dev:
	@./scripts/local_dev.sh

# Build all Docker images
build:
	docker compose build

# Run all tests
test:
	@echo "Running Go tests..."
	cd services/gateway && go test ./...
	@echo "Running Python tests..."
	cd services/inference && python -m pytest
	@echo "Running Node.js tests..."
	cd services/safety_guard && npm test
	cd apps/web_client && npm test

# Run latency benchmarks
benchmark:
	@echo "Running latency benchmarks..."
	cd tests/benchmarks && python run_latency_test.py

# Clean up
clean:
	docker compose down -v
	docker system prune -f

# Show logs
logs:
	docker compose logs -f

# Shell access
shell-api:
	docker compose exec gateway sh

shell-inference:
	docker compose exec inference bash

shell-safety:
	docker compose exec safety-guard sh

# Quick health check
health:
	@echo "Checking service health..."
	@curl -s http://localhost:8080/health | jq '.' || echo "Gateway not responding"
	@curl -s http://localhost:3000 > /dev/null && echo "Web client: ✅" || echo "Web client: ❌"
	@curl -s http://localhost:9090 > /dev/null && echo "Prometheus: ✅" || echo "Prometheus: ❌"
	@curl -s http://localhost:3001 > /dev/null && echo "Grafana: ✅" || echo "Grafana: ❌"

# Database access
db:
	docker compose exec postgres psql -U intune -d intune_care

# Generate test audio
test-audio:
	@echo "Generating test audio file..."
	@echo "안녕하세요, 오늘 기분이 어떠세요?" | say -v Yuna -o samples/korean_greeting_generated.aiff
	@ffmpeg -i samples/korean_greeting_generated.aiff -ar 16000 -ac 1 samples/korean_greeting.wav
	@rm samples/korean_greeting_generated.aiff

# Quick API test
test-api:
	@echo "Testing API endpoint..."
	curl -X POST http://localhost:8080/api/v1/voice \
		-H "Content-Type: audio/wav" \
		--data-binary @samples/korean_greeting.wav | jq '.'