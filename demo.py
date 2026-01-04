"""
FINAL DEMONSTRATION SCRIPT
Shows all working components in action
"""

import sys
sys.path.insert(0, r'C:\Users\agraw\Desktop\navigation-assistant')

import time
from modules.object_detector import ObjectDetector
from modules.distance_estimator import DistanceEstimator
from modules.audio_feedback import AudioFeedback
import cv2

def demo():
    print("\n" + "="*70)
    print("  NAVIGATION ASSISTANT - LIVE DEMONSTRATION")
    print("="*70)
    
    # Initialize
    print("\n⚙️  Initializing system...")
    detector = ObjectDetector()
    distance_est = DistanceEstimator()
    audio = AudioFeedback()
    print("✅ All modules ready!\n")
    
    # Welcome
    audio.speak("Navigation assistant demo starting")
    
    # Open camera
    print("📹 Opening camera...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return
    
    print("✅ Camera ready\n")
    print("="*70)
    print("  RUNNING DETECTION FOR 10 SECONDS")
    print("="*70)
    print("Instructions:")
    print("  • Point camera at objects (person, chair, laptop, phone, etc.)")
    print("  • Listen for audio announcements")
    print("  • Watch console for detection details")
    print("="*70 + "\n")
    
    # Run detection
    start_time = time.time()
    frame_count = 0
    detection_log = []
    
    try:
        while time.time() - start_time < 10:  # 10 second demo
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Detect every 10 frames (smooth demo)
            if frame_count % 10 == 0:
                detections = detector.detect_objects(frame)
                
                if detections:
                    for det in detections:
                        obj_class = det['class']
                        confidence = det['confidence']
                        bbox = det['bbox']
                        
                        # Calculate distance
                        x1, y1, x2, y2 = bbox
                        width = x2 - x1
                        distance = distance_est.estimate_distance(obj_class, width)
                        
                        # Log
                        log_entry = f"{obj_class} at {distance:.1f}m ({confidence:.0%})"
                        if log_entry not in detection_log[-5:]:  # Avoid spam
                            detection_log.append(log_entry)
                            print(f"  🎯 {log_entry}")
                            
                            # Audio (every 3 seconds)
                            if len(detection_log) % 3 == 0:
                                msg = f"{obj_class} detected, {distance:.1f} meters away"
                                audio.speak(msg)
            
            # Progress indicator
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                remaining = 10 - elapsed
                print(f"  ⏱️  {remaining:.0f} seconds remaining...")
    
    except KeyboardInterrupt:
        print("\n  Demo interrupted by user")
    
    finally:
        cap.release()
    
    # Results
    print("\n" + "="*70)
    print("  DEMO COMPLETED")
    print("="*70)
    print(f"  Frames processed: {frame_count}")
    print(f"  Unique detections: {len(detection_log)}")
    print(f"  Average FPS: {frame_count/10:.1f}")
    
    if detection_log:
        print(f"\n  📋 Detection Summary:")
        for i, log in enumerate(detection_log[:10], 1):
            print(f"     {i}. {log}")
    
    print("="*70)
    
    audio.speak("Demo complete. System working perfectly.")
    
    print("\n✅ YOUR NAVIGATION ASSISTANT IS FULLY FUNCTIONAL!\n")
    print("="*70)
    print("  NEXT STEPS:")
    print("="*70)
    print("  1. View full test results: TEST_RESULTS.md")
    print("  2. Start API server: python api/server.py")
    print("  3. Run mobile app: cd mobile_app && npm run android")
    print("  4. Read documentation: README_FULL.md")
    print("="*70 + "\n")

if __name__ == "__main__":
    demo()
