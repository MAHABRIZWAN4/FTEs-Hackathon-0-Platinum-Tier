@echo off
REM Watchdog Runner - Start System Health Monitor
REM Monitors all agents and auto-restarts if needed

echo.
echo ============================================================
echo   Watchdog - System Health Monitor
echo ============================================================
echo.

REM Change to project directory
cd /d "%~dp0.."

echo Starting watchdog in background...
echo.
echo Watchdog will:
echo - Monitor all agents and watchers
echo - Auto-restart stopped processes
echo - Check system health every 5 minutes
echo - Write reports to AI_Employee_Vault/Logs/system_health.md
echo.
echo Press Ctrl+C to stop watchdog
echo.

REM Run watchdog
python scripts\watchdog.py

pause
