"""
Complete System Test
Tests all components
"""

import cv2
import time

def test_complete_system():
    print("="*70)
    print("COMPLETE SYSTEM TEST")
    print("="*70)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Camera
    print("\n[1/8] Testing Camera...")
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if ret:
            print("✅ Camera: PASS")
            tests_passed += 1
        else:
            print("❌ Camera: FAIL")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Camera: FAIL - {e}")
        tests_failed += 1
    
    # Test 2: YOLO Model
    print("\n[2/8] Testing YOLO Model...")
    try:
        from ultralytics import YOLO
        model = YOLO('yolov8n.pt')
        print("✅ YOLO: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ YOLO: FAIL - {e}")
        tests_failed += 1
    
    # Test 3: Object Detector
    print("\n[3/8] Testing Object Detector...")
    try:
        from modules.object_detector import ObjectDetector
        detector = ObjectDetector()
        print("✅ Object Detector: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Object Detector: FAIL - {e}")
        tests_failed += 1
    
    # Test 4: Distance Estimator
    print("\n[4/8] Testing Distance Estimator...")
    try:
        from modules.distance_estimator import DistanceEstimator
        estimator = DistanceEstimator()
        print("✅ Distance Estimator: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Distance Estimator: FAIL - {e}")
        tests_failed += 1
    
    # Test 5: Audio Feedback
    print("\n[5/8] Testing Audio Feedback...")
    try:
        from modules.audio_feedback import AudioFeedback
        audio = AudioFeedback()
        audio.speak("Audio test")
        print("✅ Audio Feedback: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Audio Feedback: FAIL - {e}")
        tests_failed += 1
    
    # Test 6: Face Recognition
    print("\n[6/8] Testing Face Recognition...")
    try:
        from modules.face_recognition import FaceRecognitionModule
        face_rec = FaceRecognitionModule()
        print("✅ Face Recognition: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"⚠️  Face Recognition: OPTIONAL - {e}")
    
    # Test 7: SLAM
    print("\n[7/8] Testing SLAM...")
    try:
        from modules.slam_navigation import SLAMNavigationModule
        slam = SLAMNavigationModule()
        print("✅ SLAM: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"⚠️  SLAM: OPTIONAL - {e}")
    
    # Test 8: Data Logger
    print("\n[8/8] Testing Data Logger...")
    try:
        from modules.data_logger import DataLogger
        logger = DataLogger()
        print("✅ Data Logger: PASS")
        tests_passed += 1
    except Exception as e:
        print(f"⚠️  Data Logger: OPTIONAL - {e}")
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Passed: {tests_passed}")
    print(f"Failed: {tests_failed}")
    
    if tests_failed == 0:
        print("\n🎉 ALL CORE TESTS PASSED! System ready to run!")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
    
    print("="*70)

if __name__ == "__main__":
    test_complete_system()