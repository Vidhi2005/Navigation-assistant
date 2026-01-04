@echo off
title Navigation Assistant - Phone Preview Server
color 0A
cls

echo.
echo ============================================================
echo        NAVIGATION ASSISTANT - PHONE PREVIEW
echo ============================================================
echo.
echo Starting web server for phone access...
echo.

cd /d "%~dp0"

REM Start Python web server
echo Your phone can access the app at:
echo.
echo   http://%COMPUTERNAME%:8000/MOBILE_PREVIEW.html
echo.
echo OR find your IP address and use:
echo   http://YOUR_IP:8000/MOBILE_PREVIEW.html
echo.
echo.
echo Open this URL in your phone's browser!
echo.
echo ============================================================
echo.

python -m http.server 8000

pause
