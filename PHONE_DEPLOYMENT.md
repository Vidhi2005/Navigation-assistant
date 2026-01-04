# 📱 Deploy Navigation Assistant to Your Phone

## ✅ Prerequisites Completed

- [x] Backend running at `ws://172.24.192.1:8765/ws/navigate`
- [x] Camera package installing (`react-native-vision-camera`)
- [x] Android permissions configured
- [x] Mobile app IP configured

---

## 🚀 Quick Start (3 Steps)

### Step 1: Enable USB Debugging on Your Phone

**On your Android phone:**

1. Open **Settings** → **About Phone**
2. Tap **Build Number** 7 times (Developer mode enabled!)
3. Go back to **Settings** → **System** → **Developer Options**
4. Enable **USB Debugging**
5. Connect phone to PC via USB cable
6. When popup appears on phone: **Allow USB Debugging** → Tap **OK**

---

### Step 2: Build & Install the App

**In your terminal:**

```bash
cd c:\Users\agraw\Desktop\navigation-assistant
npx react-native run-android
```

**OR build APK manually:**

```bash
cd android
./gradlew assembleDebug
# APK location: android/app/build/outputs/apk/debug/app-debug.apk
# Install: adb install app/build/outputs/apk/debug/app-debug.apk
```

---

### Step 3: Test the App

**On your phone:**

1. Open **Navigation Assistant** app
2. Grant **Camera** permission when prompted
3. Grant **Location** permission when prompted
4. **Double-tap** screen to start navigation
5. Point camera at a person or object
6. **Listen**: "Person ahead, 2 meters"
7. **Feel**: Vibration (strong for close objects)
8. **Long-press** for emergency mode

---

## 🔧 Troubleshooting

### "No connected devices found"

```bash
# Check if phone is detected
adb devices

# Should show:
# List of devices attached
# ABC123DEF456    device
```

If nothing appears:

- Reconnect USB cable
- Try different USB port
- Check USB debugging is enabled
- Install ADB drivers for your phone

---

### "Camera permission denied"

- Uninstall app
- Reinstall
- Grant all permissions when asked

---

### "Cannot connect to backend"

1. **Check PC and phone on same WiFi**
2. **Verify backend is running:**
   ```bash
   # On PC browser: http://172.24.192.1:8765/health
   # Should show: {"status": "healthy"}
   ```
3. **If IP changed, update in code:**
   - Get new IP: `ipconfig` (look for IPv4 Address)
   - Edit: `mobile_app/src/screens/NavigationScreen_PRODUCTION.js`
   - Change: `const BACKEND_URL = 'ws://YOUR_NEW_IP:8765/ws/navigate'`
   - Rebuild app

---

### "App crashes on startup"

```bash
# View logs
adb logcat | Select-String "ReactNative"

# Clear cache and reinstall
cd android
./gradlew clean
cd ..
npx react-native run-android
```

---

## ✨ Expected Behavior

### When Working Correctly:

1. **Camera turns on** automatically when navigation starts
2. **Speaks instructions** every 2 seconds:
   - "Person ahead, 2 meters, right"
   - "Car ahead, 5 meters, center"
3. **Vibrates based on danger:**
   - **Strong vibration** = Object very close (< 1m)
   - **Medium vibration** = Object nearby (< 2m)
   - **Light vibration** = Object far (> 2m)
4. **Gestures work:**
   - **Single tap** = Repeat last instruction
   - **Double tap** = Pause/Resume navigation
   - **Long press (2s)** = Emergency mode (sends SMS)

---

## 📊 Performance Checklist

Test these scenarios:

- [ ] App opens without crashing
- [ ] Camera permission granted
- [ ] Camera feed starts
- [ ] Backend connection established (check logs)
- [ ] First detection spoken within 5 seconds
- [ ] Haptic feedback works
- [ ] Emergency mode triggers
- [ ] Works with screen off (audio only)
- [ ] Battery usage acceptable (< 20%/hour)

---

## 🎯 Next Steps After Installation

1. **Walk around** with the app running
2. **Test different objects** (person, chair, door)
3. **Test distances** (close vs far objects)
4. **Test emergency** (long press → SMS sent)
5. **Check battery** after 10 minutes of use

---

## 📱 Alternative: Install APK Directly

If USB debugging doesn't work, install APK via file transfer:

1. Build APK:

   ```bash
   cd android
   ./gradlew assembleDebug
   ```

2. Find APK at:

   ```
   android/app/build/outputs/apk/debug/app-debug.apk
   ```

3. Transfer to phone:

   - Email to yourself
   - Google Drive
   - Bluetooth
   - USB file transfer

4. On phone:
   - Settings → Security → **Allow Unknown Sources**
   - Open APK file → **Install**

---

## 🚨 Critical Requirements

**Must be true for app to work:**

- ✅ Backend running on PC
- ✅ Phone and PC on same WiFi
- ✅ Camera permission granted
- ✅ react-native-vision-camera installed
- ✅ Correct IP address in code

**If ANY of these is false, app won't work!**
