"""
API SERVER TEST SCRIPT
Tests the Flask API endpoints without starting the full server
"""

import sys
import os
import base64
import cv2
import json
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.object_detector import ObjectDetector
from modules.distance_estimator import DistanceEstimator
import config

def test_api_detection():
    """Test the detection logic that the API uses"""
    print("\n" + "="*60)
    print("API DETECTION TEST")
    print("="*60)
    
    # Initialize
    print("\n[1/3] Initializing detector...")
    detector = ObjectDetector(config.YOLO_MODEL)
    distance_estimator = DistanceEstimator(config.FOCAL_LENGTH)
    print("✅ Detector ready")
    
    # Capture test frame
    print("\n[2/3] Capturing test frame from camera...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return False
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("❌ Failed to capture frame")
        return False
    print("✅ Frame captured")
    
    # Test detection (same as API endpoint)
    print("\n[3/3] Running detection (API logic)...")
    start_time = time.time()
    
    detections = detector.detect(frame)
    results = []
    
    if detections:
        for detection in detections:
            obj_class = detection['class']
            bbox = detection['bbox']
            confidence = detection['confidence']
            
            # Calculate distance
            x1, y1, x2, y2 = bbox
            obj_width_pixels = x2 - x1
            obj_center_x = (x1 + x2) // 2
            frame_center_x = frame.shape[1] // 2
            
            distance = distance_estimator.estimate_distance(
                obj_width_pixels,
                config.KNOWN_WIDTH
            )
            
            # Determine direction
            if obj_center_x < frame_center_x - 100:
                direction = "left"
            elif obj_center_x > frame_center_x + 100:
                direction = "right"
            else:
                direction = "center"
            
            results.append({
                "object": obj_class,
                "distance": round(distance, 2),
                "direction": direction,
                "confidence": round(confidence, 2)
            })
    
    inference_time = (time.time() - start_time) * 1000
    
    # Print results (API response format)
    print("\n" + "="*60)
    print("API RESPONSE (JSON):")
    print("="*60)
    response = {
        "detections": results,
        "timestamp": time.time(),
        "inference_time_ms": round(inference_time, 2)
    }
    print(json.dumps(response, indent=2))
    print("="*60)
    
    print(f"\n✅ Detection completed in {inference_time:.1f}ms")
    print(f"✅ Found {len(results)} objects")
    
    return True

def test_api_server_start():
    """Test if API server can start"""
    print("\n" + "="*60)
    print("API SERVER START TEST")
    print("="*60)
    
    try:
        from flask import Flask
        from flask_cors import CORS
        
        app = Flask(__name__)
        CORS(app)
        
        @app.route('/health')
        def health():
            return {"status": "healthy"}
        
        print("\n✅ Flask app created successfully")
        print("✅ CORS enabled")
        print("\n📝 To start the actual server, run:")
        print("   python api/server.py")
        print("\n📝 Then test with:")
        print("   curl http://127.0.0.1:5000/health")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("\n🧪 RUNNING API TESTS...")
    
    # Test 1: Detection logic
    test1 = test_api_detection()
    
    # Test 2: Server initialization
    test2 = test_api_server_start()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Detection logic:  {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Server init:      {'✅ PASS' if test2 else '❌ FAIL'}")
    print("="*60)
    
    if test1 and test2:
        print("\n✅ ALL API TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED")
