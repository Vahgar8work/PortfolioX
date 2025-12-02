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
