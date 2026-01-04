# Testing Guide - Navigation Assistant

## Quick Testing Options

### Option 1: Backend Only (Python Desktop App)
**Fastest way to test object detection**
```powershell
# Test the desktop app with webcam
python main.py
```

### Option 2: Backend API + Mobile App
**Full system test with audio/haptic feedback**

---

## 🔧 Setup & Testing Steps

### Step 1: Test Backend First

#### Install Python Dependencies
```powershell
pip install -r requirements.txt
```

#### Test Desktop App (simplest test)
```powershell
python main.py
```

**Expected behavior:**
- Webcam window opens
- Green bounding boxes around detected objects
- Console shows: "person detected at 2.5m"
- Audio announces objects

**Troubleshooting:**
- No audio? Check `pyttsx3` installation: `pip install pyttsx3`
- No camera? Check `cv2` installation: `pip install opencv-python`
- Model download? First run auto-downloads `yolov8n.pt`

---

#### Test API Server

**Terminal 1 - Start Backend:**
```powershell
cd C:\Users\agraw\Desktop\navigation-assistant
python api/server.py
```

**Expected output:**
```
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
```

**Terminal 2 - Test API:**
```powershell
# Health check
curl http://127.0.0.1:5000/health

# Test detection with webcam image (requires curl with file upload)
# Or use Postman/Insomnia to POST image to http://127.0.0.1:5000/detect
```

**Expected response:**
```json
{
  "detections": [
    {"object": "person", "distance": 2.5, "direction": "center"}
  ]
}
```

---

### Step 2: Test Mobile App

#### Install Node.js Dependencies
```powershell
cd mobile_app
npm install
```

#### Configure API Endpoint

Edit `mobile_app/src/services/APIService.js`:
```javascript
// Find your computer's IP address first
// Run in PowerShell: ipconfig
// Look for "IPv4 Address" (e.g., 192.168.1.100)

const API_BASE_URL = 'http://YOUR_IP_HERE:5000';  // Replace with your IP
```

#### Run on Android

**Prerequisites:**
- Android Studio installed
- USB debugging enabled on phone OR Android emulator running

**Commands:**
```powershell
cd mobile_app

# Start Metro bundler
npm start

# In another terminal, run on device/emulator
npm run android
```

**Expected behavior:**
1. App installs on phone/emulator
2. You see "Navigation Assistant" title
3. Permissions requested (Camera, Location, Audio)
4. Gestures work:
   - Single tap → Announces "Ready to navigate"
   - Double tap → Starts navigation mode
   - Long press → Emergency mode

#### Run on iOS (Mac only)

```bash
cd mobile_app
pod install --project-directory=ios
npm run ios
```

---

### Step 3: Test Full Integration

**Setup:**
1. ✅ Backend API running (`python api/server.py`)
2. ✅ Mobile app running on device
3. ✅ Same WiFi network (phone and computer)

**Test Navigation Mode:**

1. **Open app** → You see Home Screen
2. **Double tap** → Enters Navigation mode
3. **Point camera at objects**
4. **Listen** → Should hear: "Person ahead, 2 meters, center"
5. **Feel** → Phone vibrates (distance pattern)
6. **Swipe left** → Stops navigation

**Test Emergency Mode:**

1. **Long press anywhere** → Red screen
2. **Hear** → "Emergency mode activated"
3. **Location** → GPS coordinates logged
4. **Tap** → Returns to home

---

## 🐛 Common Issues & Fixes

### Backend Issues

**Issue: `ModuleNotFoundError: No module named 'ultralytics'`**
```powershell
pip install ultralytics
```

**Issue: Camera not opening**
```python
# Edit config.py, change camera index:
CAMERA_INDEX = 1  # Try 0, 1, 2
```

**Issue: YOLO model not found**
```powershell
# Download manually
curl -L https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt -o yolov8n.pt
```

### Mobile App Issues

**Issue: Metro bundler error**
```powershell
# Clear cache
cd mobile_app
npm start -- --reset-cache
```

**Issue: "Network request failed" in app**
- ✅ Check API server is running
- ✅ Check IP address in APIService.js
- ✅ Phone and PC on same WiFi
- ✅ Windows Firewall: Allow port 5000

**Windows Firewall Fix:**
```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "Flask API" -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow
```

**Issue: Camera permissions denied**
- Settings → Apps → Navigation Assistant → Permissions → Allow Camera

**Issue: App crashes on launch**
```powershell
# Rebuild
cd mobile_app/android
./gradlew clean
cd ..
npm run android
```

### iOS Issues

**Issue: Pods not installing**
```bash
cd mobile_app/ios
pod deintegrate
pod install
```

**Issue: Build fails**
- Open `NavigationAssistant.xcworkspace` in Xcode
- Product → Clean Build Folder
- Product → Build

---

## 🧪 Test Checklist

### Backend Tests ✅

- [ ] `python main.py` runs without errors
- [ ] Webcam opens and shows video
- [ ] Objects are detected (green boxes)
- [ ] Console prints detection messages
- [ ] Audio feedback plays
- [ ] `python api/server.py` starts on port 5000
- [ ] `/health` endpoint returns 200

### Mobile App Tests ✅

- [ ] App installs successfully
- [ ] No crash on launch
- [ ] Home screen loads
- [ ] Single tap announces status
- [ ] Double tap enters Navigation mode
- [ ] Long press enters Emergency mode
- [ ] Settings screen accessible (triple tap)

### Integration Tests ✅

- [ ] Backend API receives requests
- [ ] Mobile camera captures frames
- [ ] Objects detected and returned
- [ ] Audio announces detections
- [ ] Haptic feedback triggers
- [ ] Emergency logs location
- [ ] Gestures work smoothly

---

## 📊 Expected Performance

| Component | Expected | Acceptable |
|-----------|----------|------------|
| Backend FPS | 30-60 | >15 |
| API latency | <200ms | <500ms |
| Mobile FPS | 10-15 | >5 |
| Audio delay | <1s | <2s |
| Detection accuracy | >80% | >70% |

---

## 🎬 Demo Scenarios

### Scenario 1: Indoor Navigation
1. Start navigation mode
2. Walk toward furniture (chair, table)
3. Listen for: "Chair ahead, 1.5 meters, left"
4. Feel distance vibration (medium intensity)

### Scenario 2: Person Detection
1. Point camera at person
2. Listen for: "Person ahead, 3 meters, center"
3. Move closer → vibration gets stronger

### Scenario 3: Emergency
1. Long press screen
2. Emergency mode activates (red screen)
3. Location logged to `data/logs/`
4. Can tap to return

---

## 📱 Alternative Testing (No Physical Phone)

### Use Android Emulator

1. Open Android Studio
2. AVD Manager → Create Virtual Device
3. Choose: Pixel 5 with API 33
4. Start emulator
5. Run: `npm run android`

### Use iOS Simulator (Mac)

1. Xcode → Open Developer Tool → Simulator
2. Choose: iPhone 14
3. Run: `npm run ios`

**Note:** Emulators have limited camera (fake images only)

---

## 🔍 Debugging Tools

### View Backend Logs
```powershell
# API server shows all requests
python api/server.py
# Look for: POST /detect/stream - 200
```

### View Mobile Logs

**Android:**
```powershell
npm run android
# In another terminal:
npx react-native log-android
```

**iOS:**
```bash
npx react-native log-ios
```

### Check Data Logs
```powershell
# View detection logs
cat data/logs/detections_*.csv

# View performance
cat data/logs/performance_*.csv
```

---

## ✅ Success Criteria

**You know it's working when:**

1. ✅ Backend detects objects in real-time (15+ FPS)
2. ✅ Mobile app doesn't crash
3. ✅ Audio announces objects clearly
4. ✅ Haptic vibration is noticeable
5. ✅ Gestures respond immediately (<500ms)
6. ✅ Emergency mode logs location
7. ✅ No "Network error" messages

---

## 🚀 Next Steps After Testing

1. **Test with visually impaired user** (actual user feedback)
2. **Measure battery life** (6+ hours target)
3. **Test outdoors** (stairs, curbs, crosswalks)
4. **Fine-tune audio** (speed, volume, clarity)
5. **Add custom dataset** (improve accuracy)

---

**Quick Start Command:**
```powershell
# Terminal 1: Backend
python api/server.py

# Terminal 2: Mobile app
cd mobile_app && npm run android
```

Good luck! 🎯
