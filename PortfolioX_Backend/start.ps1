# PortfolioX - Complete Local Setup & Run Script
# This script sets up and runs the entire project locally

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "PORTFOLIOX LOCAL SETUP" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the project root
if (-not (Test-Path "manage.py")) {
    Write-Host "[ERROR] manage.py not found!" -ForegroundColor Red
    Write-Host "Please run this from your Django project root." -ForegroundColor Yellow
    exit 1
}

Write-Host "[STEP 1/7] Checking Prerequisites..." -ForegroundColor Yellow
Write-Host ""

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found. Install from python.org" -ForegroundColor Red
    exit 1
}

# Check pip
try {
    $pipVersion = pip --version 2>&1
    Write-Host "[OK] pip installed" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] pip not found" -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host ""
    Write-Host "[STEP 2/7] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "[OK] Virtual environment created" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[STEP 2/7] Virtual environment exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "[STEP 3/7] Activating virtual environment..." -ForegroundColor Yellow
& "venv/Scripts/Activate.ps1"
Write-Host "[OK] Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "[STEP 4/7] Installing dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray
pip install -q -r requirements.txt 2>&1 | Out-Null
Write-Host "[OK] Dependencies installed" -ForegroundColor Green

# Setup .env file
Write-Host ""
Write-Host "[STEP 5/7] Setting up environment variables..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    $envContent = @"
# Django Settings
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
DB_NAME=portfoliox_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
"@
    Set-Content -Path ".env" -Value $envContent
    Write-Host "[OK] Created .env file" -ForegroundColor Green
} else {
    Write-Host "[OK] .env file already exists" -ForegroundColor Green
}

# Database migrations
Write-Host ""
Write-Host "[STEP 6/7] Running database migrations..." -ForegroundColor Yellow
python manage.py makemigrations 2>&1 | Out-Null
python manage.py migrate
Write-Host "[OK] Database migrations complete" -ForegroundColor Green

# Create superuser prompt
Write-Host ""
Write-Host "[STEP 7/7] Creating superuser (optional)..." -ForegroundColor Yellow
$createSuperuser = Read-Host "Do you want to create a superuser? (y/n)"
if ($createSuperuser -eq "y") {
    python manage.py createsuperuser
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""

# Create startup scripts
Write-Host "Creating startup scripts..." -ForegroundColor Cyan

# Create start_backend.ps1
$startBackendScript = @'
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
'@

Set-Content -Path "start_backend.ps1" -Value $startBackendScript

# Create start_frontend.ps1
$startFrontendScript = @'
# Start PortfolioX Frontend
Write-Host "Starting PortfolioX Frontend..." -ForegroundColor Cyan
Write-Host ""

if (Test-Path "frontend/index.html") {
    Write-Host "[OK] Opening frontend in browser..." -ForegroundColor Green
    Start-Process "frontend/index.html"
    
    Write-Host ""
    Write-Host "Frontend opened!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Quick Setup:" -ForegroundColor Cyan
    Write-Host "  1. Make sure Django is running (http://localhost:8000)" -ForegroundColor White
    Write-Host "  2. Go to Settings tab in frontend" -ForegroundColor White
    Write-Host "  3. API URL should be: http://localhost:8000" -ForegroundColor White
    Write-Host "  4. Click 'Test Connection'" -ForegroundColor White
} else {
    Write-Host "[ERROR] Frontend not found!" -ForegroundColor Red
    Write-Host "Run: .\create_frontend.ps1" -ForegroundColor Yellow
}
'@

Set-Content -Path "start_frontend.ps1" -Value $startFrontendScript

# Create start_all.ps1
$startAllScript = @'
# Start Everything - PortfolioX Complete
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "STARTING PORTFOLIOX COMPLETE SYSTEM" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

.\start_backend.ps1
'@

Set-Content -Path "start_all.ps1" -Value $startAllScript

# Create stop_all.ps1
$stopAllScript = @'
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
'@

Set-Content -Path "stop_all.ps1" -Value $stopAllScript

Write-Host "[OK] Startup scripts created" -ForegroundColor Green
Write-Host ""

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "HOW TO RUN THE PROJECT" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "OPTION 1: Start Everything (Recommended)" -ForegroundColor Green
Write-Host "  .\start_all.ps1" -ForegroundColor White
Write-Host ""

Write-Host "OPTION 2: Start Services Separately" -ForegroundColor Green
Write-Host "  .\start_backend.ps1    # Django + Celery + Redis" -ForegroundColor White
Write-Host "  .\start_frontend.ps1   # Open frontend only" -ForegroundColor White
Write-Host ""

Write-Host "OPTION 3: Manual Start (Step by Step)" -ForegroundColor Green
Write-Host "  1. Start Redis:" -ForegroundColor Cyan
Write-Host "     docker run --name portfoliox-redis -p 6379:6379 -d redis" -ForegroundColor White
Write-Host ""
Write-Host "  2. Start Celery Worker:" -ForegroundColor Cyan
Write-Host "     celery -A config worker --loglevel=info --pool=solo" -ForegroundColor White
Write-Host ""
Write-Host "  3. Start Celery Beat:" -ForegroundColor Cyan
Write-Host "     celery -A config beat --loglevel=info" -ForegroundColor White
Write-Host ""
Write-Host "  4. Start Django:" -ForegroundColor Cyan
Write-Host "     python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "  5. Open Frontend:" -ForegroundColor Cyan
Write-Host "     Open frontend/index.html in browser" -ForegroundColor White
Write-Host ""

Write-Host "TO STOP EVERYTHING:" -ForegroundColor Red
Write-Host "  .\stop_all.ps1" -ForegroundColor White
Write-Host ""

Write-Host "IMPORTANT URLS:" -ForegroundColor Yellow
Write-Host "  Django:      http://localhost:8000" -ForegroundColor White
Write-Host "  Admin:       http://localhost:8000/admin" -ForegroundColor White
Write-Host "  API Docs:    http://localhost:8000/api/" -ForegroundColor White
Write-Host "  Frontend:    frontend/index.html" -ForegroundColor White
Write-Host ""

$startNow = Read-Host "Do you want to start the project now? (y/n)"
if ($startNow -eq "y") {
    Write-Host ""
    Write-Host "Starting PortfolioX..." -ForegroundColor Cyan
    .\start_all.ps1
}
