@echo off
title Navigation Assistant Server
color 0A
cls

echo.
echo ============================================================
echo           NAVIGATION ASSISTANT API SERVER
echo ============================================================
echo.
echo Starting server...
echo.

cd /d "%~dp0"
call venv\Scripts\activate.bat

python start.py

echo.
echo.
echo ============================================================
echo   Server stopped. Close this window or press any key...
echo ============================================================
pause >nul
