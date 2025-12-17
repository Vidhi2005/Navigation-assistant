"""
Configuration settings for Navigation Assistant
"""

# Camera Settings
CAMERA_ID = 0  # 0 = default webcam, change to 1 if not working
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 30

# YOLO Model Settings
YOLO_MODEL = "yolov8n.pt"  # nano = fastest, 's'=small, 'm'=medium
CONFIDENCE_THRESHOLD = 0.5  # 0.0 to 1.0 (higher = more confident detections)
IOU_THRESHOLD = 0.45  # For non-max suppression

# Distance Estimation Settings
# IMPORTANT: Calibrate these for your camera!
FOCAL_LENGTH = 700  # pixels (adjust after calibration)
KNOWN_WIDTH = 0.5   # meters (average object width)
AVERAGE_PERSON_WIDTH = 0.5  # meters

# Distance Thresholds
CRITICAL_DISTANCE = 1.0  # meters - immediate danger
WARNING_DISTANCE = 2.5   # meters - warning zone
SAFE_DISTANCE = 5.0      # meters - safe zone

# Audio Settings
TTS_RATE = 150  # Words per minute (100-200 is good)
TTS_VOLUME = 1.0  # 0.0 to 1.0
ALERT_COOLDOWN = 2.0  # seconds between same alert

# Face Recognition Settings
FACE_RECOGNITION_TOLERANCE = 0.6  # Lower = stricter matching
FACE_CHECK_INTERVAL = 30  # Check faces every N frames

# GPS Settings (get from Google Cloud Console)
GOOGLE_MAPS_API_KEY = "YOUR_API_KEY_HERE"  # Replace this!

# File Paths
FACE_DATABASE_PATH = "data/face_encodings.pkl"
FACE_IMAGES_PATH = "data/faces/"
MODEL_PATH = "models/"

# App Settings
DEBUG_MODE = True  # Show visual output
SHOW_FPS = True   # Display FPS counter
LOG_DETECTIONS = True  # Print detection info

CONFIDENCE_THRESHOLD = 0.5
CAMERA_INDEX = 0
MODEL_PATH = "yolov8n.pt"

# In config.py:
YOLO_MODEL = "yolov8n.pt"  # Use nano (fastest)
CONFIDENCE_THRESHOLD = 0.6  # Higher = fewer detections
ENABLE_GPS = True
