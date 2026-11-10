@echo off
title SkillPulse - The Stock Market of Skills
cd /d "%~dp0\.."

echo =================================================================
echo                 SKILLPULSE PLATFORM LAUNCHER                     
echo    Job Market Data Analytics: A Spark RDD Approach               
echo =================================================================
echo.
echo [1/2] Verifying Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in your PATH!
    echo Please install Python 3.10+ and add it to your environment variables.
    pause
    exit /b 1
)

echo [2/2] Starting SkillPulse Unified Server on http://localhost:8000...
echo.
echo =================================================================
echo  Web Application: http://localhost:8000
echo  API Documentation: http://localhost:8000/docs
echo =================================================================
echo.
echo Opening browser in 3 seconds... (Press Ctrl+C in this window to stop)
timeout /t 3 /nobreak >nul
start http://localhost:8000

python -m uvicorn backend.app.main:app --host localhost --port 8000 --reload
pause
