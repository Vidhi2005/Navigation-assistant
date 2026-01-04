@echo off
echo ========================================
echo   React Native Mobile App Setup
echo ========================================
echo.

cd mobile_app

echo [1/3] Installing dependencies...
call npm install

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Choose how to run:
echo.
echo For Android:
echo   npm run android
echo.
echo For iOS:
echo   npm run ios
echo.
echo NOTE: You need either:
echo   - Android phone connected via USB
echo   - Android Studio emulator running
echo   - Xcode simulator (macOS only)
echo.
pause
