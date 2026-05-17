@echo off
echo ============================================
echo  NexusTrader Core - Stopping...
echo ============================================

docker-compose stop

echo.
echo [INFO] All services stopped. Data is preserved.
echo [INFO] Run start.bat to restart.
echo.
pause
