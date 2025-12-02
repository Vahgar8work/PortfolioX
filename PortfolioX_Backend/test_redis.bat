@echo off
echo Testing Redis...
wsl -d Ubuntu-24.04 bash -c "redis-cli ping"
pause
