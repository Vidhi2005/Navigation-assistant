"""
Distance Estimation Module
Calculates approximate distance to detected objects
"""

import numpy as np
from config import *
from config import CAMERA_INDEX, CONFIDENCE_THRESHOLD, MODEL_PATH


class DistanceEstimator:
    def __init__(self):
        """Initialize distance estimator"""
        self.focal_length = FOCAL_LENGTH
        self.known_width = KNOWN_WIDTH
        
        # Known widths for common objects (in meters)
        self.object_widths = {
            'person': 0.5,      # Average shoulder width
            'chair': 0.5,
            'couch': 1.8,
            'dining table': 1.5,
            'car': 1.8,
            'bicycle': 0.6,
            'door': 0.9,
            'laptop': 0.35,
            'tv': 1.0,
            'cell phone': 0.08,
            'bottle': 0.08,
            'cup': 0.09,
            'book': 0.15
        }
    
    def estimate_distance(self, object_class, bbox_width):
        """
        Estimate distance using similar triangles
        
        Formula: Distance = (Real_Width × Focal_Length) / Pixel_Width
        
        Args:
            object_class: Name of detected object
            bbox_width: Width of bounding box in pixels
        
        Returns:
            Distance in meters (float)
        """
        if bbox_width == 0:
            return float('inf')
        
        # Get known width for this object class
        real_width = self.object_widths.get(object_class, self.known_width)
        
        # Calculate distance
        distance = (real_width * self.focal_length) / bbox_width
        
        return distance
    
    def calibrate_focal_length(self, real_width, measured_distance, bbox_width):
        """
        Calibrate focal length using a known object
        
        Place object at known distance and measure its bbox width
        
        Args:
            real_width: Actual width of object in meters
            measured_distance: Measured distance to object in meters
            bbox_width: Width of bounding box in pixels
        
        Returns:
            Calculated focal length
        """
        focal_length = (bbox_width * measured_distance) / real_width
        self.focal_length = focal_length
        
        print(f"✅ Focal length calibrated: {focal_length:.2f} pixels")
        print(f"Update FOCAL_LENGTH in config.py to: {focal_length:.2f}")
        
        return focal_length
    
    def get_distance_category(self, distance):
        """
        Categorize distance as critical/warning/safe
        
        Returns:
            ('critical'|'warning'|'safe', urgency_level)
        """
        if distance < CRITICAL_DISTANCE:
            return ('critical', 3)
        elif distance < WARNING_DISTANCE:
            return ('warning', 2)
        elif distance < SAFE_DISTANCE:
            return ('safe', 1)
        else:
            return ('far', 0)
    
    def get_position_in_frame(self, bbox_center_x, frame_width):
        """
        Determine if object is left, center, or right
        
        Args:
            bbox_center_x: X coordinate of bbox center
            frame_width: Width of frame
        
        Returns:
            'left' | 'center' | 'right'
        """
        third = frame_width / 3
        
        if bbox_center_x < third:
            return 'left'
        elif bbox_center_x > 2 * third:
            return 'right'
        else:
            return 'center'
    
    def process_detections(self, detections, frame_width):
        """
        Add distance and position info to all detections
        
        Args:
            detections: List of detection dicts
            frame_width: Width of video frame
        
        Returns:
            Enhanced detections with distance and position
        """
        enhanced_detections = []
        
        for det in detections:
            # Calculate distance
            distance = self.estimate_distance(
                det['class'],
                det['width']
            )
            
            # Get position
            position = self.get_position_in_frame(
                det['center'][0],
                frame_width
            )
            
            # Get category
            category, urgency = self.get_distance_category(distance)
            
            # Add to detection
            det['distance'] = distance
            det['position'] = position
            det['category'] = category
            det['urgency'] = urgency
            
            enhanced_detections.append(det)
        
        # Sort by urgency (most urgent first)
        enhanced_detections.sort(key=lambda x: x['urgency'], reverse=True)
        
        return enhanced_detections


# Calibration tool
if __name__ == "__main__":
    print("="*50)
    print("DISTANCE ESTIMATOR CALIBRATION TOOL")
    print("="*50)
    print()
    print("Instructions:")
    print("1. Place a known object (e.g., a book) at a measured distance")
    print("2. Measure the actual distance in meters")
    print("3. Run object detection and note the bbox width in pixels")
    print("4. Enter the values below")
    print()
    
    estimator = DistanceEstimator()
    
    try:
        real_width = float(input("Enter real width of object (meters): "))
        measured_distance = float(input("Enter measured distance (meters): "))
        bbox_width = float(input("Enter bbox width from detection (pixels): "))
        
        focal_length = estimator.calibrate_focal_length(
            real_width,
            measured_distance,
            bbox_width
        )
        
        print()
        print("="*50)
        print(f"✅ CALIBRATION COMPLETE!")
        print(f"Focal Length: {focal_length:.2f} pixels")
        print()
        print("Copy this to config.py:")
        print(f"FOCAL_LENGTH = {focal_length:.2f}")
        print("="*50)
        
    except ValueError:
        print("❌ Invalid input! Please enter numbers only.")
    except Exception as e:
        print(f"❌ Error: {e}")