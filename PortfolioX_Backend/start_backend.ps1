# Start PortfolioX Backend Services
Write-Host "Starting PortfolioX Backend..." -ForegroundColor Cyan

# Activate virtual environment
& "venv/Scripts/Activate.ps1"

# Start Redis in Docker (or use local Redis)
Write-Host "`n[1/4] Starting Redis..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "docker run --name portfoliox-redis -p 6379:6379 -d redis:latest; Write-Host 'Redis running on port 6379' -ForegroundColor Green"

Start-Sleep -Seconds 3

# Start Celery Worker
Write-Host "`n[2/4] Starting Celery Worker..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& venv/Scripts/Activate.ps1; celery -A config worker --loglevel=info --pool=solo"

Start-Sleep -Seconds 2

# Start Celery Beat
Write-Host "`n[3/4] Starting Celery Beat..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& venv/Scripts/Activate.ps1; celery -A config beat --loglevel=info"

Start-Sleep -Seconds 2

# Start Django Server
Write-Host "`n[4/4] Starting Django Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& venv/Scripts/Activate.ps1; python manage.py runserver"

Start-Sleep -Seconds 3

Write-Host "`n======================================" -ForegroundColor Green
Write-Host "ALL SERVICES STARTED!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "Services running:" -ForegroundColor Cyan
Write-Host "  Django:       http://localhost:8000" -ForegroundColor White
Write-Host "  Admin:        http://localhost:8000/admin" -ForegroundColor White
Write-Host "  Redis:        localhost:6379" -ForegroundColor White
Write-Host "  Celery:       Running in background" -ForegroundColor White
Write-Host ""
Write-Host "Opening frontend in 3 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
Start-Process "frontend/index.html"

Write-Host "`nPress any key to stop all services..." -ForegroundColor Red
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host "`nStopping services..." -ForegroundColor Yellow
docker stop portfoliox-redis 2>$null
docker rm portfoliox-redis 2>$null
Stop-Process -Name "celery" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
Write-Host "Services stopped." -ForegroundColor Green
