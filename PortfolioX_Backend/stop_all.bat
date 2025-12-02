@echo off
echo Stopping all services...
echo.
echo Stopping Python processes...
taskkill /F /IM python.exe 2>nul
echo.
echo Stopping Redis...
wsl -d Ubuntu-24.04 bash -c "redis-cli shutdown" 2>nul
echo.
echo Done!
pause
