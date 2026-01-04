@echo off
echo ========================================
echo   Converting to Expo for Easy Preview
echo ========================================
echo.
echo This will let you see the mobile app on your phone
echo WITHOUT installing Android Studio!
echo.
echo Steps:
echo 1. Install Expo CLI globally
echo 2. Download "Expo Go" app on your phone from:
echo    - Google Play Store (Android)
echo    - App Store (iOS)
echo.
echo 3. Run: npx expo start
echo 4. Scan QR code with your phone
echo 5. See the app running!
echo.
echo ========================================
pause
echo.
echo Installing Expo...
cd mobile_app
call npm install -g expo-cli
call npx expo install expo
echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Now run:
echo   cd mobile_app
echo   npx expo start
echo.
echo Then scan the QR code with Expo Go app!
pause
