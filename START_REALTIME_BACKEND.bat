@echo off
title Real-Time Navigation Backend
color 0A
cls

echo.
echo ========================================================================
echo                  REAL-TIME NAVIGATION BACKEND SERVER
echo ========================================================================
echo.
echo Starting WebSocket server for mobile app...
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat

echo.
echo Backend will run on:
echo   WebSocket: ws://0.0.0.0:8765/ws/navigate
echo   Health Check: http://0.0.0.0:8765/health
echo.
echo Make sure your mobile app connects to:
echo   ws://YOUR_IP:8765/ws/navigate
echo.
echo Find your IP: Run 'ipconfig' in another terminal
echo.
echo ========================================================================
echo.

python api/realtime_server.py

pause
