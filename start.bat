@echo off
echo ========================================
echo LinkedIn Content Automation Tool
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ and try again
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ and try again
    pause
    exit /b 1
)

echo [1/4] Checking backend dependencies...
cd backend
if not exist "venv\" (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo [2/4] Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1

echo [3/4] Checking frontend dependencies...
cd ..\frontend
if not exist "node_modules\" (
    echo Installing npm packages...
    call npm install
)

echo [4/4] Starting application...
echo.
echo Backend will start at: http://localhost:8000
echo Frontend will start at: http://localhost:3000
echo.
echo Press Ctrl+C in each window to stop the servers
echo.
pause

REM Start backend in new window
start "LinkedIn Automation - Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && python -m app.main"

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
start "LinkedIn Automation - Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo Application started successfully!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/api/docs
echo.
echo Close this window or press any key to exit launcher
pause >nul
