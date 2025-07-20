#!/bin/bash
set -e

echo "🚀 Starting Intune-Care Local Development Environment"
echo "=================================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env with your API keys before continuing"
    echo "   Required keys: OPENAI_API_KEY, DEEPGRAM_API_KEY, ELEVENLABS_API_KEY"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker Desktop."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose."
    exit 1
fi

# Function to wait for service
wait_for_service() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $service to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200"; then
            echo "✅ $service is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service failed to start"
    return 1
}

# Clean up function
cleanup() {
    echo -e "\n🧹 Cleaning up..."
    docker compose down
    exit 0
}

# Set up trap for cleanup
trap cleanup INT TERM

# Build images
echo "🔨 Building Docker images..."
docker compose build

# Start services
echo "🚀 Starting services..."
docker compose up -d

# Wait for services to be ready
wait_for_service "Gateway" "http://localhost:8080/health"
wait_for_service "Web Client" "http://localhost:3000"
wait_for_service "Prometheus" "http://localhost:9090"
wait_for_service "Grafana" "http://localhost:3001"

# Seed demo data
echo "🌱 Seeding demo data..."
docker compose run --rm demo-seeder || echo "Demo seeding skipped"

# Display status
echo -e "\n✨ Intune-Care is ready!"
echo "=================================="
echo "🌐 Web Client: http://localhost:3000"
echo "🔌 API Gateway: http://localhost:8080"
echo "📊 Grafana Dashboard: http://localhost:3001 (admin/admin)"
echo "📈 Prometheus: http://localhost:9090"
echo "=================================="
echo ""
echo "📝 Quick Test Commands:"
echo "  curl http://localhost:8080/health"
echo "  docker compose logs -f gateway"
echo "  docker compose exec postgres psql -U intune"
echo ""
echo "Press Ctrl+C to stop all services"

# Keep script running
docker compose logs -f