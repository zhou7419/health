@echo off
setlocal enabledelayedexpansion

echo =========================================
echo       Health Metrics Project
echo    Starting Backend and Frontend...
echo =========================================
echo.

set "PORT_OCCUPIED="

:: ---------- 检查端口 8000（后端） ----------
set "PID8000="
for /f "tokens=5" %%i in ('netstat -ano ^| findstr ":8000 "') do set "PID8000=%%i"
if defined PID8000 (
    set "PROC8000="
    for /f "skip=3 tokens=1" %%n in ('tasklist /fi "pid eq !PID8000!"') do if not defined PROC8000 set "PROC8000=%%n"
    if /i "!PROC8000!"=="python.exe" (
        echo [Backend] Port 8000 被本项目占用，正在重启...
        taskkill /f /pid !PID8000! >nul 2>&1
    ) else if /i "!PROC8000!"=="uvicorn.exe" (
        echo [Backend] Port 8000 被本项目占用，正在重启...
        taskkill /f /pid !PID8000! >nul 2>&1
    ) else if defined PROC8000 (
        echo [WARN] 端口 8000 已被其他程序占用: !PROC8000! (PID=!PID8000!)
        echo        请手动关闭后重试。
        set "PORT_OCCUPIED=1"
    )
)

:: ---------- 检查端口 5173（前端） ----------
set "PID5173="
for /f "tokens=5" %%i in ('netstat -ano ^| findstr ":5173 "') do set "PID5173=%%i"
if defined PID5173 (
    set "PROC5173="
    for /f "skip=3 tokens=1" %%n in ('tasklist /fi "pid eq !PID5173!"') do if not defined PROC5173 set "PROC5173=%%n"
    if /i "!PROC5173!"=="node.exe" (
        echo [Frontend] Port 5173 被本项目占用，正在重启...
        taskkill /f /pid !PID5173! >nul 2>&1
    ) else if defined PROC5173 (
        echo [WARN] 端口 5173 已被其他程序占用: !PROC5173! (PID=!PID5173!)
        echo        请手动关闭后重试。
        set "PORT_OCCUPIED=1"
    )
)

echo.
if defined PORT_OCCUPIED (
    echo 存在端口冲突，请解决后重新运行。
    pause
    exit /b 1
)

:: 启动后端
echo [1/2] Starting FastAPI Backend on port 8000...
start "Health Backend (FastAPI)" cmd /c "cd /d %~dp0backend && ..\.venv\Scripts\uvicorn app.main:app --reload --port 8000"

:: 启动前端
echo [2/2] Starting Vue Frontend on port 5173...
start "Health Frontend (Vue)" cmd /c "cd /d %~dp0web && npm run dev"

echo.
echo Both services are starting in separate windows.
echo - Backend: http://127.0.0.1:8000/docs
echo - Frontend: http://localhost:5173/
echo.
pause
