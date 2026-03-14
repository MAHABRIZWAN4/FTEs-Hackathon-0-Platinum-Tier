@echo off
REM Health Check Runner - Quick System Status
REM Shows current system health and pending tasks

echo.
echo ============================================================
echo   Health Check - System Status
echo ============================================================
echo.

REM Change to project directory
cd /d "%~dp0.."

REM Run health check
python scripts\health_check.py

echo.
pause
