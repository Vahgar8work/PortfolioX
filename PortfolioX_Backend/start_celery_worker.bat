@echo off
echo ========================================
echo Starting Celery Worker
echo ========================================
echo.
celery -A config worker -l info --pool=solo
