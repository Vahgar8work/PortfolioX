@echo off
echo ========================================
echo Starting Redis in Ubuntu-24.04
echo ========================================
echo.
wsl -d Ubuntu-24.04 bash -c "redis-server --daemonize yes && echo 'Redis started' && redis-cli ping"
pause
