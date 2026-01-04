@echo off
echo ========================================
echo   Navigation Assistant Server
echo ========================================
echo.
echo Starting server...
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat
python start.py

echo.
echo ========================================
echo   Server stopped
echo ========================================
pause
