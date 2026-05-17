@echo off
echo ============================================
echo  NexusTrader Core - RESET
echo  WARNING: This will delete all containers!
echo  Your .env and data folder are preserved.
echo ============================================
echo.
set /p CONFIRM=Type YES to confirm reset: 
if /i not "%CONFIRM%"=="YES" (
    echo [CANCELLED] Reset aborted.
    pause
    exit /b 0
)

echo [INFO] Stopping and removing containers...
docker-compose down

echo [INFO] Removing Docker images for clean rebuild...
docker-compose down --rmi local

echo.
echo [INFO] Reset complete. Run start.bat to rebuild and restart.
echo.
pause
