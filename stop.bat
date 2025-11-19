@echo off
echo ========================================
echo Stopping LinkedIn Content Automation
echo ========================================
echo.

echo Stopping all Python and Node.js processes...

REM Kill backend (Python/uvicorn)
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM uvicorn.exe /T >nul 2>&1

REM Kill frontend (Node/npm)
taskkill /F /IM node.exe /T >nul 2>&1
taskkill /F /IM npm.cmd /T >nul 2>&1

echo.
echo All servers stopped.
echo.
pause
