# Stop All PortfolioX Services
Write-Host "Stopping all PortfolioX services..." -ForegroundColor Yellow

# Stop Docker Redis
docker stop portfoliox-redis 2>$null
docker rm portfoliox-redis 2>$null

# Stop Celery processes
Stop-Process -Name "celery" -Force -ErrorAction SilentlyContinue

# Stop Python/Django
Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue

Write-Host "All services stopped." -ForegroundColor Green
