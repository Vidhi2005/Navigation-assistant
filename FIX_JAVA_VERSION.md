# 🔧 Fix Java Version Issue

## ❌ Current Problem:

- You have Java 8 installed
- Gradle 9.0 requires Java 17 or higher
- App won't build until this is fixed

## ✅ Solution Options:

### Option 1: Install Java 17 (RECOMMENDED - 5 minutes)

**Download & Install:**

1. Visit: https://adoptium.net/temurin/releases/
2. Select:
   - **Version:** 17 (LTS)
   - **Operating System:** Windows
   - **Architecture:** x64
   - **Package Type:** JDK
3. Download the `.msi` installer
4. Run installer → Install to default location (`C:\Program Files\Eclipse Adoptium\jdk-17...`)
5. Restart VS Code terminal

**After installing, run:**

```powershell
# Set JAVA_HOME for this session
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.13.11-hotspot"  # Adjust path
$env:PATH = "$env:JAVA_HOME\bin;$env:PATH"

# Verify
java -version
# Should show: openjdk version "17.0.x"

# Build app
cd c:\Users\agraw\Desktop\navigation-assistant
npx react-native run-android
```

---

### Option 2: Use Existing Gradle 8.x (TEMPORARY - 2 minutes)

Downgrade Gradle to version 8 which supports Java 8:

```powershell
cd c:\Users\agraw\Desktop\navigation-assistant\android

# Edit gradle/wrapper/gradle-wrapper.properties
# Change: distributionUrl=https\://services.gradle.org/distributions/gradle-9.0-all.zip
# To:     distributionUrl=https\://services.gradle.org/distributions/gradle-8.5-all.zip

# Then build
cd ..
npx react-native run-android
```

---

### Option 3: Use Expo (FASTEST - already installed)

Since you have Expo set up, use it instead:

```powershell
cd c:\Users\agraw\Desktop\navigation-assistant\mobile_app
npx expo run:android
```

**This will:**

- Use Expo's build system
- Work with your current Java 8
- Install directly to your connected phone
- Takes 3-5 minutes

---

## 🚀 RECOMMENDED: Use Expo Right Now

Since your phone is already connected and Expo is installed, run this:

```powershell
cd c:\Users\agraw\Desktop\navigation-assistant\mobile_app
npx expo run:android
```

**After app installs:**

1. Open "Navigation Assistant" on phone
2. Grant camera permission
3. Double-tap to start navigation
4. Point camera at person/object
5. Listen for spoken instructions

---

## ⚡ Quick Command (Copy & Paste):

```powershell
cd c:\Users\agraw\Desktop\navigation-assistant\mobile_app
Write-Host "`n🚀 USING EXPO TO BUILD APP`n" -ForegroundColor Green
Write-Host "✅ Works with Java 8" -ForegroundColor Cyan
Write-Host "✅ Phone: RZCX525KD4M connected`n" -ForegroundColor Cyan
npx expo run:android
```

---

## 📝 Why Expo?

- ✅ Works with your current Java 8
- ✅ Faster build times
- ✅ Auto-handles Android configuration
- ✅ Includes all required permissions
- ✅ Direct install to phone

**Choose:**

- **Now:** Expo (fastest, works immediately)
- **Later:** Install Java 17 for pure React Native builds
