@echo off
echo.
echo ===================================================================
echo   INSTALLING JAVA 17 FOR ANDROID BUILD
echo ===================================================================
echo.
echo This will download and install Java 17 (required for React Native)
echo.
pause

echo.
echo Downloading Java 17...
echo.

:: Download Java 17 using PowerShell
powershell -Command "& {Invoke-WebRequest -Uri 'https://download.oracle.com/java/17/latest/jdk-17_windows-x64_bin.exe' -OutFile '%TEMP%\jdk17-installer.exe'}"

if not exist "%TEMP%\jdk17-installer.exe" (
    echo.
    echo ERROR: Download failed!
    echo.
    echo Please manually download from:
    echo https://www.oracle.com/java/technologies/downloads/#java17
    echo.
    pause
    exit /b 1
)

echo.
echo Starting Java 17 installer...
echo Please follow the installation wizard
echo.

start /wait "%TEMP%\jdk17-installer.exe"

echo.
echo ===================================================================
echo   INSTALLATION COMPLETE!
echo ===================================================================
echo.
echo Next steps:
echo 1. Restart your terminal/VS Code
echo 2. Run: java -version
echo 3. Should show: java version "17.0.x"
echo 4. Then run: npx react-native run-android
echo.
echo ===================================================================
echo.
pause
