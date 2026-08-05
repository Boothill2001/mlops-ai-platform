@echo off
title CICAAD MLOps AI Platform — Port 8493
echo ============================================
echo   CICAAD MLOps AI Platform
echo   Backend: http://localhost:8493
echo   Frontend: http://localhost:8494
echo ============================================
echo.

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install Python 3.11+
    pause
    exit /b 1
)

:: Check Node
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Install Node 18+
    pause
    exit /b 1
)

:: Setup backend venv if needed
if not exist "backend\.venv" (
    echo [SETUP] Creating Python venv...
    python -m venv backend\.venv
)

:: Install backend deps
echo [BACKEND] Installing dependencies...
call backend\.venv\Scripts\activate.bat
pip install -r backend\requirements.txt -q

:: Install frontend deps if needed
if not exist "frontend\node_modules" (
    echo [FRONTEND] Installing dependencies...
    cd frontend
    call npm ci
    cd ..
)

:: Start backend on port 8493
echo.
echo [BACKEND] Starting FastAPI on port 8493...
set LLM_PROVIDER=mock
set EMBEDDING_PROVIDER=mock
start "CICAAD-Backend" cmd /k "cd /d %~dp0 && call backend\.venv\Scripts\activate.bat && cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8493 --reload"

:: Wait for backend to be ready
echo [WAIT] Waiting for backend...
timeout /t 5 /nobreak >nul

:: Start frontend on port 8494 (proxying to backend 8493)
echo [FRONTEND] Starting Vite dev server on port 8494...
start "CICAAD-Frontend" cmd /k "cd /d %~dp0\frontend && set VITE_BACKEND_PORT=8493 && npx vite --port 8494"

echo.
echo ============================================
echo   Backend:  http://localhost:8493/health
echo   Frontend: http://localhost:8494
echo   API docs: http://localhost:8493/docs
echo ============================================
echo.
echo Press any key to stop all services...
pause >nul

:: Cleanup
taskkill /FI "WINDOWTITLE eq CICAAD-Backend" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq CICAAD-Frontend" /F >nul 2>&1
echo [DONE] All services stopped.
