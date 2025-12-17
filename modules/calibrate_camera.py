"""
Camera Calibration Tool
Calculates focal length for accurate distance estimation
"""

import cv2
import numpy as np

def calibrate_distance():
    print("="*70)
    print("CAMERA CALIBRATION FOR DISTANCE ESTIMATION")
    print("="*70)
    print()
    print("Steps:")
    print("1. Place an object (book, chair, person) at a known distance")
    print("2. Measure the ACTUAL distance with a tape measure")
    print("3. Measure the ACTUAL width of the object")
    print("4. Run detection and note the pixel width")
    print()
    
    try:
        # Get measurements
        real_width = float(input("Enter actual width of object (in meters, e.g., 0.15 for book): "))
        actual_distance = float(input("Enter actual distance to object (in meters, e.g., 2.0): "))
        
        # Open camera
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Cannot open camera")
            return
        
        print("\nPosition your camera to see the object")
        print("Press SPACE when ready to capture")
        print("Press Q to quit")
        
        from ultralytics import YOLO
        model = YOLO('yolov8n.pt')
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect objects
            results = model(frame, verbose=False)
            
            # Draw detections
            annotated = results[0].plot()
            
            cv2.imshow('Camera Calibration - Press SPACE to capture', annotated)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord(' '):
                # Capture and measure
                if len(results[0].boxes) > 0:
                    # Get first detection
                    box = results[0].boxes[0]
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    pixel_width = x2 - x1
                    
                    print(f"\n✅ Detection captured!")
                    print(f"Pixel width: {pixel_width:.2f}")
                    
                    # Calculate focal length
                    focal_length = (pixel_width * actual_distance) / real_width
                    
                    print(f"\n{'='*70}")
                    print("CALIBRATION RESULT")
                    print(f"{'='*70}")
                    print(f"Focal Length: {focal_length:.2f} pixels")
                    print(f"\n✅ Update config.py with:")
                    print(f"FOCAL_LENGTH = {focal_length:.2f}")
                    print(f"{'='*70}")
                    
                    break
                else:
                    print("No object detected! Try again...")
            
            elif key == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    calibrate_distance()