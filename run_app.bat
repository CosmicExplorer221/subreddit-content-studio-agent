@echo off
echo ============================================
echo LinkedIn Content Studio - Railway Edition
echo ============================================
echo.
echo Starting both backend and frontend servers...
echo.
echo Backend will start at: http://localhost:8000
echo Frontend will start at: http://localhost:5173
echo.
echo Press Ctrl+C in each window to stop
echo.

REM Start backend in new window
start "LinkedIn Studio - Backend" cmd /k "cd backend && python main.py"

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
start "LinkedIn Studio - Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers started!
echo.
echo Backend: http://localhost:8000/api/docs
echo Frontend: http://localhost:5173
echo.
echo Close this window when done.
pause
