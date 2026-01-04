"""
TEST SCRIPT - Core functionality only
Tests object detection, distance estimation, and audio feedback
"""

import cv2
import time
from modules.object_detector import ObjectDetector
from modules.distance_estimator import DistanceEstimator
from modules.audio_feedback import AudioFeedback
import config

def test_core_system():
    """Test core navigation features"""
    print("\n" + "="*60)
    print("NAVIGATION ASSISTANT - CORE SYSTEM TEST")
    print("="*60)
    
    # Initialize modules
    print("\n[1/4] Initializing Object Detector...")
    detector = ObjectDetector()
    print("✅ Object Detector ready")
    
    print("\n[2/4] Initializing Distance Estimator...")
    distance_estimator = DistanceEstimator()
    print("✅ Distance Estimator ready")
    
    print("\n[3/4] Initializing Audio Feedback...")
    audio = AudioFeedback()
    print("✅ Audio Feedback ready")
    
    print("\n[4/4] Opening camera...")
    cap = cv2.VideoCapture(config.CAMERA_ID)
    if not cap.isOpened():
        print("❌ ERROR: Cannot open camera")
        return False
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
    print("✅ Camera opened successfully")
    
    print("\n" + "="*60)
    print("STARTING LIVE DETECTION")
    print("="*60)
    print("Instructions:")
    print("  • Point camera at objects (person, chair, laptop, etc.)")
    print("  • Green boxes = detected objects")
    print("  • Audio will announce detections")
    print("  • Press 'q' to quit")
    print("="*60 + "\n")
    
    # Start test
    audio.speak("Navigation assistant started")
    frame_count = 0
    detection_count = 0
    start_time = time.time()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to grab frame")
                break
            
            frame_count += 1
            
            # Detect objects
            detections = detector.detect_objects(frame)
            
            if detections:
                detection_count += len(detections)
                
                for detection in detections:
                    # Get object info
                    obj_class = detection['class']
                    confidence = detection['confidence']
                    bbox = detection['bbox']
                    x1, y1, x2, y2 = bbox
                    
                    # Estimate distance
                    obj_width_pixels = x2 - x1
                    distance = distance_estimator.estimate_distance(
                        obj_class, 
                        obj_width_pixels
                    )
                    
                    # Draw bounding box
                    color = (0, 255, 0)  # Green
                    if distance < config.CRITICAL_DISTANCE:
                        color = (0, 0, 255)  # Red for critical
                    elif distance < config.WARNING_DISTANCE:
                        color = (0, 165, 255)  # Orange for warning
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    
                    # Draw label
                    label = f"{obj_class} {distance:.1f}m ({confidence:.0%})"
                    cv2.putText(frame, label, (x1, y1 - 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    
                    # Audio feedback (throttled)
                    if frame_count % 30 == 0:  # Every 30 frames (~1 second)
                        message = f"{obj_class} ahead, {distance:.1f} meters"
                        audio.speak(message)
                        print(f"🔊 {message}")
            
            # Display FPS
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f"Detections: {detection_count}", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Show frame
            cv2.imshow("Navigation Assistant - TEST", frame)
            
            # Check for quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n✅ User quit - test completed")
                break
                
    except KeyboardInterrupt:
        print("\n✅ Test interrupted by user")
    
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        audio.speak("Navigation assistant stopped")
        
        # Print statistics
        elapsed = time.time() - start_time
        print("\n" + "="*60)
        print("TEST RESULTS")
        print("="*60)
        print(f"Duration:        {elapsed:.1f} seconds")
        print(f"Frames:          {frame_count}")
        print(f"Average FPS:     {frame_count/elapsed:.1f}")
        print(f"Total detections: {detection_count}")
        print(f"Detection rate:  {detection_count/frame_count*100:.1f}% of frames")
        print("="*60)
        
        return True

if __name__ == "__main__":
    success = test_core_system()
    if success:
        print("\n✅ TEST PASSED - Core system working properly!")
    else:
        print("\n❌ TEST FAILED - See errors above")
