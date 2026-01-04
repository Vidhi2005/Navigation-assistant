# Navigation Assistant - User Guide

## For Visually Impaired Users

### Getting Started

#### Installation
1. Install the Navigation Assistant app from the App Store/Play Store
2. Grant camera and microphone permissions
3. Optional: Grant location permission for emergency features

#### First Time Setup (with caregiver)
1. Open the app
2. Triple-tap anywhere to access settings
3. Configure:
   - Server URL (if using desktop backend)
   - Emergency contact number
   - Speech rate preference
   - Detection sensitivity

### Using the App

#### Home Screen (Ready Mode)

When you open the app, you'll hear:
> "Navigation ready. Double tap to start."

**Controls:**
- **Single tap anywhere** → Hear status again
- **Double tap anywhere** → Start navigation
- **Triple tap** → Open settings (for setup)
- **Long press (2 seconds)** → Emergency mode

#### Navigation Mode (Active)

After double-tapping, navigation starts:
> "Navigation active. Scanning environment."

The app will announce obstacles:
> "Person ahead, 2 meters"
> "Chair on left, 1.5 meters"
> "Vehicle approaching from right, 3 meters"

**During Navigation:**
- **Single tap** → Repeat last announcement
- **Double tap** → Pause/Resume navigation
- **Swipe up** → Speed up speech
- **Swipe down** → Slow down speech
- **Swipe left** → Stop and return home
- **Long press** → Emergency mode

#### Emergency Mode

Activated by long press (2 seconds):
1. Phone vibrates continuously
2. Announcement: "Emergency message sent. Help is on the way."
3. Location is sent to emergency contact
4. **Tap anywhere** → Call emergency contact
5. **Small cancel button at bottom** → Cancel emergency

### Understanding Announcements

#### Distance Categories

- **"Very close"** → Less than 1 meter (immediate danger)
  - Strong continuous vibration
  - Urgent tone
  
- **"X meters"** → 1-5 meters (warning)
  - Medium vibration
  - Normal announcement

- **No announcement** → More than 5 meters (safe)
  - Objects too far to be relevant

#### Direction

- **"Ahead"** → Object directly in front
  - Double vibration in center
  
- **"On left"** → Object to your left
  - Short-long vibration pattern
  
- **"On right"** → Object to your right
  - Long-short vibration pattern

### Haptic Feedback Guide

| Vibration Pattern | Meaning |
|------------------|---------|
| Single light tap | UI feedback (button press) |
| Single medium | Warning - object 1-2m away |
| Single strong | Critical - object <1m away |
| Double tap | Object directly ahead |
| Short-long | Object on left |
| Long-short | Object on right |
| Continuous | Emergency mode active |

### Tips for Best Results

#### Environment
- **Well-lit areas** work best
- **Outdoor** and **indoor** both supported
- Avoid **extreme darkness** or **bright glare**

#### Walking
- Hold phone **at chest level**
- Point camera **forward** in walking direction
- **Steady grip** - avoid shaking
- **Normal walking pace**

#### Battery Life
- Navigation uses camera + detection = high power
- Expect **4-6 hours** of continuous use
- Bring power bank for long trips
- App keeps screen on during navigation

### Common Issues

#### No Announcements
1. Check if navigation is active (you should hear "Scanning")
2. Double-tap to resume if paused
3. Ensure camera is not covered
4. Try stopping and restarting

#### Too Many Announcements
1. Swipe down to slow speech
2. Increase distance threshold in settings
3. Disable less important object types

#### Wrong Distances
1. Backend may need camera calibration
2. Works best for common objects (people, furniture, vehicles)
3. Less accurate for unusual objects

#### App Crashes
1. Ensure you have latest version
2. Restart phone
3. Contact support with details

### Settings (For Caregivers)

Access: Triple-tap on home screen

#### Server Configuration
- **API Server URL**: Address of detection backend
  - Format: `http://192.168.1.100:5000`
  - Use local WiFi for best performance

#### Emergency Contact
- **Phone Number**: Who to call in emergency
  - Format: `+1-555-123-4567` or `911`

#### Audio Feedback
- **Speech Rate**: How fast announcements are spoken
  - Range: 0.0 (very slow) to 1.0 (fast)
  - Adjust with swipe up/down during navigation

#### Object Detection
- **Detect People**: On/Off
- **Detect Vehicles**: On/Off
- **Detect Obstacles**: On/Off

#### Distance Alerts
- **Critical Distance**: Alert threshold for urgent warnings (meters)
  - Default: 1.0m
- **Warning Distance**: Alert threshold for cautions (meters)
  - Default: 2.5m

### Privacy & Data

#### What's Collected
- **Images**: Only processed in real-time, not stored
- **Location**: Only collected during emergency
- **Face Data**: Stored locally on device (optional feature)

#### What's NOT Collected
- No video recording
- No audio recording
- No usage analytics (unless opted in)
- No cloud uploads (all processing local/WiFi)

### Safety Guidelines

⚠️ **IMPORTANT**: This app is an assistive tool, NOT a replacement for traditional mobility aids (cane, guide dog, etc.)

#### Use Together With
- White cane
- Guide dog
- Human guide
- Your existing mobility techniques

#### Limitations
- **Cannot detect**:
  - Holes in ground
  - Low-hanging obstacles above waist
  - Transparent glass doors/walls
  - Water/ice on ground
  
- **May miss**:
  - Fast-moving objects
  - Objects in poor lighting
  - Very small objects
  
- **Not suitable for**:
  - Driving/cycling
  - Running
  - Crowded areas with rapid movement

## For Caregivers/Family

### Setting Up for Someone Else

1. **Initial Configuration**
   - Install app on user's phone
   - Triple-tap to open settings
   - Enter emergency contact (your number)
   - Test emergency feature
   
2. **Training Session**
   - Start in familiar, safe area
   - Practice gestures: tap, double-tap, swipe, long-press
   - Walk together and verify announcements
   - Adjust speech rate to user preference
   
3. **Backend Setup (Optional)**
   - Install Python backend on computer/Raspberry Pi
   - Connect to same WiFi as phone
   - Enter server IP in app settings
   - Test connection
   
### Emergency Response

When you receive an emergency alert:
1. You'll get location coordinates
2. Call back immediately
3. If no answer, proceed to last known location
4. User can also dial you by tapping screen in emergency mode

### Monitoring Usage

- Check Data Logger in backend for usage statistics
- Review detection logs to understand common routes
- Adjust sensitivity based on feedback

## Troubleshooting Guide

### Desktop/Backend Issues

#### Backend Won't Start
```bash
# Check Python version
python --version  # Should be 3.8+

# Install dependencies
pip install -r requirements.txt

# Run server
python api/server.py
```

#### Camera Not Working
```bash
# Test camera
python test_camera.py

# Check camera ID in config.py
CAMERA_ID = 0  # Try 1, 2 if 0 doesn't work
```

#### Slow Detection
- Use GPU if available
- Reduce image resolution in config
- Use yolov8n (nano) not larger models
- Close other applications

### Mobile App Issues

#### Can't Connect to Server
1. Both devices on same WiFi network
2. Check server IP address (use `ipconfig` on Windows, `ifconfig` on Mac/Linux)
3. Firewall may be blocking port 5000
4. Try accessing `http://SERVER_IP:5000/health` in browser

#### No Audio
1. Check phone volume
2. Ensure TTS is initialized (close and reopen app)
3. Check Do Not Disturb mode
4. Try different voice in phone settings

#### No Haptic Feedback
1. Check phone vibration settings
2. Some phones disable vibration in power-saving mode
3. Haptic may not work in phone silent mode

## Advanced Features

### Custom Object Detection

Train model for specific objects:
1. Collect images using `scripts/collect_dataset.py`
2. Annotate with labels
3. Train custom model: `scripts/train_model.py`
4. Replace yolov8n.pt with your custom model

### Face Recognition

Add known faces:
1. Create folder: `modules/data/faces/PersonName/`
2. Add 3-5 photos of person
3. Restart backend
4. System will announce "PersonName" when detected

### SLAM Indoor Navigation

For complex indoor environments:
1. Enable SLAM in main.py: `enable_slam=True`
2. Walk through area to build map
3. Map will show your position and obstacles
4. Save map for future use

## Contact & Support

- **Issues**: Open issue on GitHub
- **Email**: support@navigationassistant.com
- **Community**: Join our Discord server
- **Documentation**: https://navigationassistant.com/docs

## Changelog

### Version 2.0 (Current)
- ✅ Complete mobile app with gesture controls
- ✅ Audio-first interface
- ✅ Emergency mode
- ✅ Real-time API integration
- ✅ Haptic feedback patterns
- ✅ Face recognition module
- ✅ Custom dataset tools

### Version 1.0 (Previous)
- Basic desktop application
- YOLO detection
- Audio feedback
- SLAM navigation

## License

MIT License - Free for personal and commercial use
