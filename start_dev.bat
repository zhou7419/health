@echo off
echo =========================================
echo       Health Metrics Project
echo    Starting Backend and Frontend...
echo =========================================

:: Start Backend
echo [1/2] Starting FastAPI Backend on port 8000...
start "Health Backend (FastAPI)" cmd /c "cd backend && uvicorn app.main:app --reload --port 8000"

:: Start Frontend
echo [2/2] Starting Vue Frontend on port 5173...
start "Health Frontend (Vue)" cmd /c "cd web && npm run dev"

echo.
echo Both services are starting in separate windows.
echo - Backend: http://127.0.0.1:8000/docs
echo - Frontend: http://localhost:5173/
echo.
echo Press any key to exit this script (the services will keep running).
pause
