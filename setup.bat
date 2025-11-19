@echo off
echo ============================================
echo LinkedIn Content Studio - Setup
echo Railway Edition
echo ============================================
echo.

echo [1/4] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.9+ from python.org
    pause
    exit /b 1
)

echo.
echo [2/4] Installing backend dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install backend dependencies
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo [3/4] Checking Node.js...
node --version
if errorlevel 1 (
    echo ERROR: Node.js not found! Please install Node.js 16+ from nodejs.org
    pause
    exit /b 1
)

echo.
echo [4/4] Installing frontend dependencies...
cd frontend
call npm install
if errorlevel 1 (
    echo ERROR: Failed to install frontend dependencies
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Copy backend\.env.example to backend\.env
echo 2. Add your API keys to backend\.env
echo 3. Run: run_app.bat
echo.
pause
