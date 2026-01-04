# Navigation Assistant - System Architecture

## Overview

Navigation Assistant is an AI-powered mobility aid for visually impaired users, combining real-time object detection, distance estimation, and multi-modal feedback (audio + haptic).

## System Components

### 1. Backend (Python)

#### Core Modules
- **Object Detector** (`modules/object_detector.py`)
  - YOLOv8n real-time detection
  - 80+ object classes (COCO) + custom navigation classes
  - 30-60 FPS on CPU, 100+ FPS on GPU

- **Distance Estimator** (`modules/distance_estimator.py`)
  - Triangulation method (current)
  - Hybrid depth estimation (monocular + stereo)
  - Category-based alerts (critical/warning/safe)

- **Audio Feedback** (`modules/audio_feedback.py`)
  - Text-to-speech (pyttsx3)
  - Configurable speech rate
  - Alert cooldown system

- **Face Recognition** (`modules/face_recognition.py`)
  - Face encoding database
  - Real-time recognition
  - Confidence scoring

- **SLAM Navigation** (`modules/slam_navigation.py`)
  - Indoor mapping
  - Feature-based tracking
  - 3D map generation

- **Haptic Feedback** (`modules/haptic_feedback.py`)
  - Distance-based vibration patterns
  - Directional feedback
  - Raspberry Pi GPIO support

- **Data Logger** (`modules/data_logger.py`)
  - CSV/JSON logging
  - Performance metrics
  - Visualization generation

- **Data Preprocessing** (`modules/data_preprocessing.py`)
  - Image augmentation pipeline
  - Dataset preparation for training
  - YOLO format conversion

- **Depth Estimator** (`modules/depth_estimator.py`)
  - Monocular depth (MiDaS)
  - Stereo depth (dual cameras)
  - Hybrid estimation

#### API Server (`api/server.py`)
- Flask REST API
- Endpoints:
  - `/detect` - Full object detection
  - `/detect/stream` - Optimized for real-time
  - `/emergency` - Emergency logging
  - `/settings` - Configuration management

### 2. Mobile App (React Native)

#### Three-Mode Interface

**1. Home Screen (Idle/Ready)**
- Full-screen touch target
- Gesture controls:
  - Single tap: Repeat status
  - Double tap: Start navigation
  - Triple tap: Open settings
  - Long press: Emergency mode

**2. Navigation Screen (Active)**
- Real-time detection loop
- Audio announcements
- Haptic feedback
- Gestures:
  - Single tap: Repeat last announcement
  - Double tap: Pause/Resume
  - Swipe up/down: Speech speed
  - Swipe left: Stop navigation
  - Long press: Emergency

**3. Emergency Screen**
- Red background, large call button
- Automatic location tracking
- Alert notification system
- Direct call to emergency contact

#### Services

- **TTSService** - Text-to-speech control
- **HapticService** - Vibration patterns
- **APIService** - Backend communication
- **CameraService** - Frame capture
- **LocationService** - GPS tracking

## Data Flow

```
Camera → Frame Capture → API Request → Object Detection →
Distance Estimation → Priority Filtering → Audio + Haptic Output
```

### Real-time Loop (Mobile)
1. Capture frame (1 Hz)
2. Send to backend API
3. Receive detection results
4. Generate natural language announcement
5. Trigger audio + haptic feedback
6. Repeat

## ML Model Architecture

### Current: YOLOv8n
- **Input**: 640×640 RGB image
- **Backbone**: CSPDarknet with C2f modules
- **Neck**: PAN (Path Aggregation Network)
- **Head**: Anchor-free detection
- **Output**: Class + BBox + Confidence

### Custom Training Pipeline
1. Collect navigation-specific images
2. Annotate in YOLO format
3. Augment dataset
4. Fine-tune YOLOv8n
5. Export to ONNX/TFLite

## Dataset Strategy

### COCO Dataset (Current)
- 80 classes, 330K images
- Pre-trained weights
- General object detection

### Custom Navigation Dataset (Recommended)
- 28 navigation-specific classes:
  - People: person, wheelchair, cane, walker
  - Vertical: stairs, escalator, elevator
  - Hazards: curb, pothole, uneven_surface
  - Traffic: traffic_light, crosswalk
  - Obstacles: pole, pillar, wall, barrier
  - Furniture: bench, table, chair
  - Vehicles: car, bike, bus

### Preprocessing Pipeline
- Random brightness/contrast
- Gaussian blur (simulate low vision)
- Random shadows/fog/rain
- Horizontal flip, rotation
- Perspective transform

## Deployment Architecture

```
┌─────────────────────────────────────────────────┐
│             Mobile App (React Native)           │
│  - Camera capture                               │
│  - TTS output                                   │
│  - Haptic feedback                              │
│  - Gesture controls                             │
└──────────────────┬──────────────────────────────┘
                   │ HTTP/REST API
                   ▼
┌─────────────────────────────────────────────────┐
│         Backend Server (Flask/Python)           │
│  - Object detection (YOLOv8)                    │
│  - Distance estimation                          │
│  - Face recognition (optional)                  │
│  - Data logging                                 │
└─────────────────────────────────────────────────┘
```

## Key Design Principles

### Accessibility-First
- Audio is primary output (not visual)
- Gesture-based controls (not buttons)
- High contrast UI (when needed)
- Screen reader compatible

### Real-Time Performance
- <100ms inference time
- 1 Hz detection loop (mobile)
- Immediate audio feedback
- Low latency haptic

### Reliability
- Offline TTS (critical)
- Cooldown system (prevent spam)
- Graceful degradation
- Error handling

### Privacy
- No cloud processing (optional)
- Local face recognition database
- Emergency data only when triggered

## Future Enhancements

1. **On-device ML** - Run YOLO on mobile (TFLite)
2. **Semantic Segmentation** - Walkable path detection
3. **Depth Camera** - iPhone LiDAR integration
4. **AR Audio** - Spatial audio cues
5. **Cloud Sync** - Face database sync
6. **Multi-language** - I18n support

## Performance Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Detection FPS | >15 | 30-60 |
| Inference Time | <100ms | 45ms |
| API Latency | <200ms | ~150ms |
| Audio Delay | <500ms | ~300ms |
| Battery Life | >6 hours | TBD |
| Accuracy (mAP50) | >70% | 80% (COCO) |

## References

- YOLOv8: [Ultralytics](https://github.com/ultralytics/ultralytics)
- React Native TTS: [react-native-tts](https://github.com/ak1394/react-native-tts)
- COCO Dataset: [cocodataset.org](https://cocodataset.org)
