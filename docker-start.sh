#!/bin/bash
# Docker Compose startup script for Royalty Splitter

set -e

echo "🚀 Starting Royalty Splitter with Docker Compose..."
echo "📦 Building images and starting services..."

# Remove old containers if they exist
docker compose down --remove-orphans 2>/dev/null || true

# Build and start
docker compose up --build

echo "✅ Services started!"
echo "🌐 Backend API: http://localhost:8000"
echo "🎵 Frontend: http://localhost:3000 (run 'npm run dev' in Harmoniq/ folder)"
echo ""
echo "To stop services, press Ctrl+C or run: docker compose down"
