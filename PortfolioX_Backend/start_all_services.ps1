# start_all_services.ps1

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Starting All Services" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "1. Starting Redis..." -ForegroundColor Cyan
$redisStarted = wsl -d Ubuntu-24.04 bash -c "redis-server --daemonize yes 2>&1"
Start-Sleep -Seconds 2
$redisPing = wsl -d Ubuntu-24.04 bash -c "redis-cli ping" 2>&1
if ($redisPing -match "PONG") {
    Write-Host "   OK Redis is running`n" -ForegroundColor Green
} else {
    Write-Host "   X Redis failed to start`n" -ForegroundColor Red
}

Write-Host "2. Starting Celery Worker..." -ForegroundColor Cyan
Start-Process cmd -ArgumentList "/c start_celery_worker.bat" -WindowStyle Normal
Start-Sleep -Seconds 3

Write-Host "3. Starting Celery Beat..." -ForegroundColor Cyan
Start-Process cmd -ArgumentList "/c start_celery_beat.bat" -WindowStyle Normal
Start-Sleep -Seconds 2

Write-Host "4. Starting Django..." -ForegroundColor Cyan
Start-Process cmd -ArgumentList "/c start_django.bat" -WindowStyle Normal
Start-Sleep -Seconds 2

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "All services started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nDjango:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Admin:   http://localhost:8000/admin" -ForegroundColor Cyan
Write-Host "`nTo stop: .\stop_all.bat`n" -ForegroundColor Yellow
