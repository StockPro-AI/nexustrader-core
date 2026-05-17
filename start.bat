@echo off
echo ============================================
echo  NexusTrader Core - Starting...
echo ============================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running! Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo [WARNING] .env not found - copying from .env.example...
    copy .env.example .env
    echo [ACTION REQUIRED] Please edit .env with your API keys before trading!
    notepad .env
    pause
)

echo [INFO] Building and starting services...
docker-compose up -d --build

if errorlevel 1 (
    echo [ERROR] Failed to start services!
    pause
    exit /b 1
)

echo.
echo ============================================
echo  NexusTrader Core is running!
echo ============================================
echo  Dashboard:     http://localhost:8501
echo  Orchestrator:  http://localhost:8000
echo  API Docs:      http://localhost:8000/docs
echo ============================================
echo.
pause
