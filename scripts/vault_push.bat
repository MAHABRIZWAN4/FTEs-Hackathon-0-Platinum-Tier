@echo off
REM Vault Push - One-Click Sync for Windows
REM Synchronizes AI_Employee_Vault with GitHub

echo.
echo ============================================================
echo   Vault Sync - Pushing Local Changes to Cloud
echo ============================================================
echo.

REM Change to project directory
cd /d "%~dp0.."

REM Run Python sync script
python scripts\vault_sync.py

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Vault synced successfully!
    echo.
    timeout /t 3 >nul
    exit /b 0
) else (
    echo.
    echo [ERROR] Vault sync failed! Check logs\sync.log for details.
    echo.
    pause
    exit /b 1
)
