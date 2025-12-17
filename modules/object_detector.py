"""
Object Detection Module using YOLO v8
Detects objects in real-time from camera feed
"""

from ultralytics import YOLO
import cv2
import numpy as np
from config import *
from config import CONFIDENCE_THRESHOLD, CAMERA_INDEX, MODEL_PATH


class ObjectDetector:
    def __init__(self):
        """Initialize YOLO model"""
        print("Loading YOLO model...")
        try:
            self.model = YOLO(YOLO_MODEL)
            print(f"✅ Model loaded: {YOLO_MODEL}")
            print(f"✅ Classes available: {len(self.model.names)}")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
        
        # Class names that YOLO can detect
        self.class_names = self.model.names
        
        # Track detections for filtering
        self.last_detections = []
    
    def detect_objects(self, frame):
        """
        Detect objects in a frame
        
        Args:
            frame: OpenCV image (numpy array)
        
        Returns:
            List of detections: [{
                'class': 'person',
                'confidence': 0.95,
                'bbox': [x1, y1, x2, y2],
                'center': [cx, cy]
            }]
        """
        # Run YOLO detection
        results = self.model(
            frame, 
            conf=CONFIDENCE_THRESHOLD,
            iou=IOU_THRESHOLD,
            verbose=False  # Don't print to console
        )
        
        detections = []
        
        # Process results
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                # Extract box data
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0].cpu().numpy())
                class_id = int(box.cls[0].cpu().numpy())
                class_name = self.class_names[class_id]
                
                # Calculate center point
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                
                # Calculate width and height
                width = x2 - x1
                height = y2 - y1
                
                detection = {
                    'class': class_name,
                    'confidence': confidence,
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'center': [int(center_x), int(center_y)],
                    'width': width,
                    'height': height
                }
                
                detections.append(detection)
        
        self.last_detections = detections
        return detections
    
    def draw_detections(self, frame, detections):
        """
        Draw bounding boxes and labels on frame
        
        Args:
            frame: OpenCV image
            detections: List of detection dictionaries
        
        Returns:
            Annotated frame
        """
        annotated_frame = frame.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            class_name = det['class']
            confidence = det['confidence']
            
            # Choose color based on class
            if class_name == 'person':
                color = (0, 255, 0)  # Green for people
            else:
                color = (255, 0, 0)  # Blue for objects
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{class_name} {confidence:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            
            # Draw label background
            cv2.rectangle(
                annotated_frame,
                (x1, y1 - label_size[1] - 10),
                (x1 + label_size[0], y1),
                color,
                -1
            )
            
            # Draw label text
            cv2.putText(
                annotated_frame,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2
            )
        
        return annotated_frame
    
    def filter_priority_objects(self, detections):
        """
        Filter and prioritize important objects
        Priority: person > chair > door > other furniture > vehicles
        """
        priority_classes = [
            'person', 'chair', 'couch', 'door', 'stairs',
            'car', 'bicycle', 'motorcycle', 'table', 'bed'
        ]
        
        priority_detections = []
        
        for det in detections:
            if det['class'] in priority_classes:
                priority_detections.append(det)
        
        return priority_detections


# Test the module
if __name__ == "__main__":
    print("Testing Object Detector...")
    
    detector = ObjectDetector()
    cap = cv2.VideoCapture(CAMERA_ID)
    
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect objects
        detections = detector.detect_objects(frame)
        
        # Draw detections
        annotated_frame = detector.draw_detections(frame, detections)
        
        # Show results
        cv2.imshow('Object Detection Test', annotated_frame)
        
        # Print detection count
        if detections:
            print(f"Detected {len(detections)} objects")
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("Test complete!")