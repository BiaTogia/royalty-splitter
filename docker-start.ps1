# Docker Compose startup script for Windows
# Run: .\docker-start.ps1

Write-Host "🚀 Starting Royalty Splitter with Docker Compose..." -ForegroundColor Green
Write-Host "📦 Building images and starting services..." -ForegroundColor Cyan

# Remove old containers if they exist
Write-Host "Cleaning up old containers..." -ForegroundColor Yellow
docker compose down --remove-orphans 2>$null

# Build and start
Write-Host "Building and starting services..." -ForegroundColor Cyan
docker compose up --build

Write-Host "`n✅ Services started!" -ForegroundColor Green
Write-Host "🌐 Backend API: http://localhost:8000" -ForegroundColor Blue
Write-Host "🎵 Frontend: http://localhost:3000 (run 'npm run dev' in Harmoniq/ folder)" -ForegroundColor Blue
Write-Host "`nTo stop services, press Ctrl+C or run: docker compose down" -ForegroundColor Yellow
