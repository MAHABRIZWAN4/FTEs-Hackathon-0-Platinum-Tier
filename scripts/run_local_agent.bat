@echo off
REM Local Agent Runner - Process Approvals
REM Runs the local agent to handle pending approvals

echo.
echo ============================================================
echo   Local Agent - Approval and Execution System
echo ============================================================
echo.

REM Change to project directory
cd /d "%~dp0.."

REM Run local agent
python scripts\local_agent.py

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Local agent completed successfully!
    echo.
) else (
    echo.
    echo [ERROR] Local agent encountered an error. Check logs.
    echo.
)

pause
