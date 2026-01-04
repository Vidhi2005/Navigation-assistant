"""Simple test runner"""
import sys
sys.path.insert(0, r'C:\Users\agraw\Desktop\navigation-assistant')

from modules.object_detector import ObjectDetector
from modules.distance_estimator import DistanceEstimator
from modules.audio_feedback import AudioFeedback
import cv2
import time

print("="*60)
print("QUICK SYSTEM TEST")
print("="*60)

# Test 1: Detector
print("\n[1/5] Testing Object Detector...")
try:
    detector = ObjectDetector()
    print("  OK - Detector initialized")
except Exception as e:
    print(f"  FAIL - {e}")
    sys.exit(1)

# Test 2: Distance Estimator
print("\n[2/5] Testing Distance Estimator...")
try:
    distance_est = DistanceEstimator()
    test_dist = distance_est.estimate_distance('person', 100)
    print(f"  OK - Distance estimated: {test_dist:.2f}m")
except Exception as e:
    print(f"  FAIL - {e}")
    sys.exit(1)

# Test 3: Audio
print("\n[3/5] Testing Audio Feedback...")
try:
    audio = AudioFeedback()
    print("  OK - Audio initialized")
    audio.speak("Test complete")
except Exception as e:
    print(f"  FAIL - {e}")
    sys.exit(1)

# Test 4: Camera
print("\n[4/5] Testing Camera Access...")
try:
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if ret:
        print(f"  OK - Camera working ({frame.shape[1]}x{frame.shape[0]})")
    else:
        print("  FAIL - Cannot read frame")
        sys.exit(1)
except Exception as e:
    print(f"  FAIL - {e}")
    sys.exit(1)

# Test 5: Detection
print("\n[5/5] Testing Live Detection...")
try:
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        detections = detector.detect_objects(frame)
        print(f"  OK - Detection ran ({len(detections)} objects found)")
        for d in detections[:3]:
            print(f"      - {d['class']} ({d['confidence']:.0%})")
    cap.release()
except Exception as e:
    print(f"  FAIL - {e}")
    sys.exit(1)

print("\n" + "="*60)
print(" ALL TESTS PASSED!")
print("="*60)
print("\nSystem is working! To see it in action:")
print("  python test_core_system.py")
print("\n")
