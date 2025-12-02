@echo off
echo ========================================
echo Starting Celery Beat
echo ========================================
echo.
celery -A config beat -l info
