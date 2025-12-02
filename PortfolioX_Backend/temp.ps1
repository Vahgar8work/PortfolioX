# PortfolioX Diagnostic & Fix Script
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "PORTFOLIOX DIAGNOSTIC TOOL" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

Write-Host "[CHECK 1/10] Checking project structure..." -ForegroundColor Yellow
if (-not (Test-Path "manage.py")) {
    Write-Host "  [ERROR] Not in Django project root!" -ForegroundColor Red
    Write-Host "  Current location: $(Get-Location)" -ForegroundColor Gray
    exit 1
}
Write-Host "  [OK] In project root" -ForegroundColor Green

Write-Host "`n[CHECK 2/10] Checking virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv/Scripts/python.exe")) {
    Write-Host "  [ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "  Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "  [OK] Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "  [OK] Virtual environment exists" -ForegroundColor Green
}

Write-Host "`n[CHECK 3/10] Checking Python packages..." -ForegroundColor Yellow
& "venv/Scripts/python.exe" -c "import django" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERROR] Django not installed!" -ForegroundColor Red
    Write-Host "  Installing dependencies..." -ForegroundColor Yellow
    & "venv/Scripts/pip.exe" install -r requirements.txt
    Write-Host "  [OK] Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  [OK] Django installed" -ForegroundColor Green
}

Write-Host "`n[CHECK 4/10] Checking database configuration..." -ForegroundColor Yellow
& "venv/Scripts/python.exe" manage.py check --database default 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERROR] Database not configured!" -ForegroundColor Red
    Write-Host "  Checking PostgreSQL..." -ForegroundColor Yellow
    
    # Check if PostgreSQL service is running
    $pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
    if (-not $pgService) {
        Write-Host "  [ERROR] PostgreSQL not installed or not running!" -ForegroundColor Red
        Write-Host ""
        Write-Host "  SOLUTION OPTIONS:" -ForegroundColor Cyan
        Write-Host "  Option 1 (Quick): Use SQLite instead" -ForegroundColor White
        Write-Host "  Option 2 (Recommended): Install PostgreSQL" -ForegroundColor White
        
        $choice = Read-Host "`n  Use SQLite for now? (y/n)"
        if ($choice -eq "y") {
            Write-Host "  Switching to SQLite..." -ForegroundColor Yellow
            
            # Backup current settings
            Copy-Item "config/settings.py" "config/settings.py.backup" -Force
            
            # Update settings to use SQLite
            $settingsContent = Get-Content "config/settings.py" -Raw
            $settingsContent = $settingsContent -replace "django\.db\.backends\.postgresql", "django.db.backends.sqlite3"
            $settingsContent = $settingsContent -replace "NAME.*?os\.getenv.*?\n", "NAME': BASE_DIR / 'db.sqlite3',`n"
            Set-Content "config/settings.py" $settingsContent
            
            Write-Host "  [OK] Switched to SQLite" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "  Please install PostgreSQL:" -ForegroundColor Yellow
            Write-Host "  1. Download from: https://www.postgresql.org/download/windows/" -ForegroundColor White
            Write-Host "  2. Install with default settings" -ForegroundColor White
            Write-Host "  3. Remember your postgres password" -ForegroundColor White
            Write-Host "  4. Run this script again" -ForegroundColor White
            exit 1
        }
    }
} else {
    Write-Host "  [OK] Database configured" -ForegroundColor Green
}

Write-Host "`n[CHECK 5/10] Running migrations..." -ForegroundColor Yellow
& "venv/Scripts/python.exe" manage.py migrate 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERROR] Migration failed!" -ForegroundColor Red
    Write-Host "  Running migrations with output..." -ForegroundColor Yellow
    & "venv/Scripts/python.exe" manage.py migrate
} else {
    Write-Host "  [OK] Database migrated" -ForegroundColor Green
}

Write-Host "`n[CHECK 6/10] Checking Docker..." -ForegroundColor Yellow
docker --version 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERROR] Docker not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "  SOLUTION OPTIONS:" -ForegroundColor Cyan
    Write-Host "  Option 1: Install Docker Desktop" -ForegroundColor White
    Write-Host "  Option 2: Use Redis Cloud (free)" -ForegroundColor White
    Write-Host "  Option 3: Skip Celery (analytics won't work)" -ForegroundColor White
    
    $choice = Read-Host "`n  Skip Celery for now? (y/n)"
    if ($choice -ne "y") {
        Write-Host ""
        Write-Host "  Install Docker Desktop:" -ForegroundColor Yellow
        Write-Host "  https://www.docker.com/products/docker-desktop/" -ForegroundColor White
        exit 1
    }
    $skipCelery = $true
} else {
    Write-Host "  [OK] Docker installed" -ForegroundColor Green
    $skipCelery = $false
}

Write-Host "`n[CHECK 7/10] Checking Redis..." -ForegroundColor Yellow
if (-not $skipCelery) {
    # Check if Redis container exists
    $redisContainer = docker ps -a --filter "name=portfoliox-redis" --format "{{.Names}}" 2>$null
    if ($redisContainer -eq "portfoliox-redis") {
        # Container exists, check if running
        $redisStatus = docker ps --filter "name=portfoliox-redis" --format "{{.Status}}" 2>$null
        if ($redisStatus) {
            Write-Host "  [OK] Redis already running" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] Redis container exists but stopped, starting..." -ForegroundColor Yellow
            docker start portfoliox-redis 2>$null
            Start-Sleep -Seconds 2
            Write-Host "  [OK] Redis started" -ForegroundColor Green
        }
    } else {
        Write-Host "  [WARN] Redis not running, starting..." -ForegroundColor Yellow
        docker run --name portfoliox-redis -p 6379:6379 -d redis:latest 2>$null
        Start-Sleep -Seconds 3
        
        # Verify Redis is running
        $redisCheck = docker ps --filter "name=portfoliox-redis" --format "{{.Names}}" 2>$null
        if ($redisCheck -eq "portfoliox-redis") {
            Write-Host "  [OK] Redis started successfully" -ForegroundColor Green
        } else {
            Write-Host "  [ERROR] Failed to start Redis!" -ForegroundColor Red
            $skipCelery = $true
        }
    }
} else {
    Write-Host "  [SKIP] Redis check skipped" -ForegroundColor Gray
}

Write-Host "`n[CHECK 8/10] Checking CORS settings..." -ForegroundColor Yellow
$settingsContent = Get-Content "config/settings.py" -Raw
if ($settingsContent -notmatch "CORS_ALLOW_ALL_ORIGINS") {
    Write-Host "  [WARN] CORS not configured properly!" -ForegroundColor Yellow
    Write-Host "  Fixing CORS settings..." -ForegroundColor Yellow
    
    if ($settingsContent -notmatch "corsheaders") {
        $settingsContent = $settingsContent -replace "INSTALLED_APPS = \[", "INSTALLED_APPS = [`n    'corsheaders',"
    }
    
    if ($settingsContent -notmatch "CorsMiddleware") {
        $settingsContent = $settingsContent -replace "MIDDLEWARE = \[", "MIDDLEWARE = [`n    'corsheaders.middleware.CorsMiddleware',"
    }
    
    if ($settingsContent -notmatch "CORS_ALLOW_ALL_ORIGINS") {
        $settingsContent += "`n`n# CORS Settings`nCORS_ALLOW_ALL_ORIGINS = True`n"
    }
    
    Set-Content "config/settings.py" $settingsContent
    Write-Host "  [OK] CORS configured" -ForegroundColor Green
} else {
    Write-Host "  [OK] CORS configured" -ForegroundColor Green
}

Write-Host "`n[CHECK 9/10] Testing Django server..." -ForegroundColor Yellow
Write-Host "  Starting Django in test mode..." -ForegroundColor Gray

# Start Django in background
$djangoJob = Start-Job -ScriptBlock {
    param($projectPath)
    Set-Location $projectPath
    & "venv/Scripts/python.exe" manage.py runserver 2>&1
} -ArgumentList (Get-Location).Path

# Wait for Django to start
Start-Sleep -Seconds 5

# Test if Django is responding
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    Write-Host "  [OK] Django server working!" -ForegroundColor Green
    $djangoWorking = $true
} catch {
    Write-Host "  [ERROR] Django server not responding!" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Gray
    
    # Show Django output
    Write-Host "`n  Django output:" -ForegroundColor Yellow
    Receive-Job $djangoJob | Select-Object -Last 20
    
    $djangoWorking = $false
}

# Stop test Django server
Stop-Job $djangoJob -ErrorAction SilentlyContinue
Remove-Job $djangoJob -ErrorAction SilentlyContinue

Write-Host "`n[CHECK 10/10] Checking frontend..." -ForegroundColor Yellow
if (Test-Path "frontend/index.html") {
    Write-Host "  [OK] Frontend exists" -ForegroundColor Green
} else {
    Write-Host "  [WARN] Frontend not found!" -ForegroundColor Yellow
    Write-Host "  Run: .\create_frontend.ps1" -ForegroundColor Gray
}

Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "DIAGNOSTIC SUMMARY" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

if ($djangoWorking) {
    Write-Host "[SUCCESS] All critical checks passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now start the project with:" -ForegroundColor Cyan
    Write-Host "  .\start_project_fixed.ps1" -ForegroundColor White
    Write-Host ""
    
    # Create fixed startup script
    $fixedStartScript = @'
# Start PortfolioX - Fixed Version
Write-Host "Starting PortfolioX..." -ForegroundColor Cyan
Write-Host ""

# Activate venv
& "venv/Scripts/Activate.ps1"

# Start Redis if not running
$redisCheck = docker ps --filter "name=portfoliox-redis" --format "{{.Names}}" 2>$null
if ($redisCheck -ne "portfoliox-redis") {
    Write-Host "[1/4] Starting Redis..." -ForegroundColor Yellow
    docker start portfoliox-redis 2>$null
    if ($LASTEXITCODE -ne 0) {
        docker run --name portfoliox-redis -p 6379:6379 -d redis:latest
    }
    Start-Sleep -Seconds 2
    Write-Host "  [OK] Redis running" -ForegroundColor Green
} else {
    Write-Host "[1/4] Redis already running" -ForegroundColor Green
}

# Start Celery Worker in new window
Write-Host "[2/4] Starting Celery Worker..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PWD'; & venv/Scripts/Activate.ps1; Write-Host 'Starting Celery Worker...' -ForegroundColor Cyan; celery -A config worker --loglevel=info --pool=solo"
Start-Sleep -Seconds 3
Write-Host "  [OK] Celery Worker started" -ForegroundColor Green

# Start Celery Beat in new window
Write-Host "[3/4] Starting Celery Beat..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PWD'; & venv/Scripts/Activate.ps1; Write-Host 'Starting Celery Beat...' -ForegroundColor Cyan; celery -A config beat --loglevel=info"
Start-Sleep -Seconds 2
Write-Host "  [OK] Celery Beat started" -ForegroundColor Green

# Start Django in new window
Write-Host "[4/4] Starting Django Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PWD'; & venv/Scripts/Activate.ps1; Write-Host 'Starting Django Server...' -ForegroundColor Cyan; python manage.py runserver"
Start-Sleep -Seconds 5
Write-Host "  [OK] Django started" -ForegroundColor Green

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "PORTFOLIOX IS RUNNING!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access Points:" -ForegroundColor Cyan
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "  Admin:    http://localhost:8000/admin" -ForegroundColor White
Write-Host "  API:      http://localhost:8000/portfolios/" -ForegroundColor White
Write-Host ""

# Test connection
Write-Host "Testing connection..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
try {
    $test = Invoke-WebRequest -Uri "http://localhost:8000" -UseBasicParsing -TimeoutSec 5
    Write-Host "[OK] Backend responding!" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Backend not responding yet, may need more time" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Opening frontend in 3 seconds..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

if (Test-Path "frontend/index.html") {
    Start-Process "frontend/index.html"
    Write-Host "[OK] Frontend opened!" -ForegroundColor Green
} else {
    Write-Host "[WARN] Frontend not found. Run: .\create_frontend.ps1" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "To stop all services, run: .\stop_all.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Enter to continue..." -ForegroundColor Gray
$null = Read-Host
'@
    
    Set-Content -Path "start_project_fixed.ps1" -Value $fixedStartScript
    Write-Host "Created: start_project_fixed.ps1" -ForegroundColor Gray
    
} else {
    Write-Host "[ERROR] Critical issues found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please fix the issues above and run this script again." -ForegroundColor Yellow
}

Write-Host ""
