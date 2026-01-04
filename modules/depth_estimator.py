"""
Advanced Depth Estimation Module
Provides more accurate distance estimation using multiple methods
"""

import cv2
import numpy as np
from typing import Tuple, Optional


class MonocularDepthEstimator:
    """
    Monocular depth estimation using MiDaS model
    More accurate than simple triangulation
    """
    
    def __init__(self, model_type='MiDaS_small'):
        """
        Initialize depth estimator
        
        Args:
            model_type: 'MiDaS_small' (faster) or 'DPT_Large' (more accurate)
        """
        print(f"Initializing {model_type} depth estimator...")
        
        try:
            # Load MiDaS model
            self.model = cv2.dnn.readNet(f'models/{model_type}.onnx')
            self.model_type = model_type
            
            # Input size depends on model
            if model_type == 'MiDaS_small':
                self.input_size = (256, 256)
            else:
                self.input_size = (384, 384)
            
            print(f"✅ {model_type} loaded")
            self.available = True
        
        except Exception as e:
            print(f"⚠️ Could not load MiDaS model: {e}")
            print("   Falling back to triangulation method")
            self.available = False
    
    def estimate_depth(self, frame: np.ndarray) -> np.ndarray:
        """
        Estimate depth map from single image
        
        Args:
            frame: Input image (BGR)
        
        Returns:
            Depth map (normalized 0-1, closer=higher values)
        """
        if not self.available:
            return None
        
        # Preprocess
        blob = cv2.dnn.blobFromImage(
            frame,
            scalefactor=1.0,
            size=self.input_size,
            mean=(123.675, 116.28, 103.53),
            swapRB=True,
            crop=False
        )
        
        # Inference
        self.model.setInput(blob)
        depth = self.model.forward()
        
        # Resize to original size
        depth = cv2.resize(depth[0, 0], (frame.shape[1], frame.shape[0]))
        
        # Normalize
        depth_normalized = cv2.normalize(depth, None, 0, 1, cv2.NORM_MINMAX)
        
        return depth_normalized
    
    def get_object_depth(self, depth_map: np.ndarray, bbox: list) -> float:
        """
        Get depth value for specific object
        
        Args:
            depth_map: Depth map
            bbox: Bounding box [x1, y1, x2, y2]
        
        Returns:
            Average depth in bbox (0-1)
        """
        x1, y1, x2, y2 = bbox
        roi = depth_map[y1:y2, x1:x2]
        
        # Use median for robustness
        return np.median(roi)


class StereoDepthEstimator:
    """
    Stereo depth estimation using two cameras
    Requires stereo camera setup
    """
    
    def __init__(self, baseline: float = 0.06, focal_length: float = 700):
        """
        Initialize stereo depth estimator
        
        Args:
            baseline: Distance between cameras in meters (default: 6cm)
            focal_length: Camera focal length in pixels
        """
        self.baseline = baseline
        self.focal_length = focal_length
        
        # Create stereo matcher
        self.stereo = cv2.StereoBM_create(numDisparities=96, blockSize=15)
        
        # Improve parameters
        self.stereo.setPreFilterType(cv2.STEREO_BM_PREFILTER_NORMALIZED_RESPONSE)
        self.stereo.setPreFilterSize(5)
        self.stereo.setPreFilterCap(31)
        self.stereo.setMinDisparity(0)
        self.stereo.setTextureThreshold(10)
        self.stereo.setUniquenessRatio(15)
        self.stereo.setSpeckleWindowSize(100)
        self.stereo.setSpeckleRange(32)
        self.stereo.setDisp12MaxDiff(1)
        
        print("✅ Stereo depth estimator initialized")
    
    def compute_disparity(self, left_frame: np.ndarray, right_frame: np.ndarray) -> np.ndarray:
        """
        Compute disparity map from stereo pair
        
        Args:
            left_frame: Left camera image
            right_frame: Right camera image
        
        Returns:
            Disparity map
        """
        # Convert to grayscale
        left_gray = cv2.cvtColor(left_frame, cv2.COLOR_BGR2GRAY)
        right_gray = cv2.cvtColor(right_frame, cv2.COLOR_BGR2GRAY)
        
        # Compute disparity
        disparity = self.stereo.compute(left_gray, right_gray)
        
        # Normalize
        disparity = cv2.normalize(disparity, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        
        return disparity
    
    def disparity_to_depth(self, disparity: np.ndarray) -> np.ndarray:
        """
        Convert disparity to depth
        
        Formula: depth = (baseline × focal_length) / disparity
        
        Args:
            disparity: Disparity map
        
        Returns:
            Depth map in meters
        """
        # Avoid division by zero
        disparity = np.maximum(disparity, 1)
        
        # Calculate depth
        depth = (self.baseline * self.focal_length) / disparity
        
        return depth
    
    def get_object_depth_stereo(self, disparity: np.ndarray, bbox: list) -> float:
        """
        Get depth for object from disparity map
        
        Args:
            disparity: Disparity map
            bbox: Bounding box [x1, y1, x2, y2]
        
        Returns:
            Depth in meters
        """
        x1, y1, x2, y2 = bbox
        roi = disparity[y1:y2, x1:x2]
        
        # Use median disparity
        median_disparity = np.median(roi[roi > 0])
        
        if median_disparity > 0:
            depth = (self.baseline * self.focal_length) / median_disparity
            return depth
        
        return float('inf')


class HybridDepthEstimator:
    """
    Hybrid depth estimator combining multiple methods
    Provides best accuracy
    """
    
    def __init__(self, use_monocular=True, use_stereo=False, use_triangulation=True):
        """
        Initialize hybrid depth estimator
        
        Args:
            use_monocular: Use MiDaS monocular depth
            use_stereo: Use stereo cameras
            use_triangulation: Use simple triangulation as fallback
        """
        self.use_monocular = use_monocular
        self.use_stereo = use_stereo
        self.use_triangulation = use_triangulation
        
        # Initialize available methods
        self.monocular = None
        self.stereo = None
        
        if use_monocular:
            try:
                self.monocular = MonocularDepthEstimator()
            except:
                print("⚠️ Monocular depth not available")
        
        if use_stereo:
            try:
                self.stereo = StereoDepthEstimator()
            except:
                print("⚠️ Stereo depth not available")
        
        # Triangulation parameters
        from config import FOCAL_LENGTH, KNOWN_WIDTH
        self.focal_length = FOCAL_LENGTH
        self.known_width = KNOWN_WIDTH
        
        self.object_widths = {
            'person': 0.5,
            'chair': 0.5,
            'couch': 1.8,
            'dining table': 1.5,
            'car': 1.8,
            'bicycle': 0.6,
            'door': 0.9,
            'stairs': 1.2,
            'curb': 0.15,
        }
    
    def estimate_distance_triangulation(self, object_class: str, bbox_width: int) -> float:
        """
        Simple triangulation method (fallback)
        
        Args:
            object_class: Object class name
            bbox_width: Bounding box width in pixels
        
        Returns:
            Distance in meters
        """
        if bbox_width == 0:
            return float('inf')
        
        known_width = self.object_widths.get(object_class, self.known_width)
        distance = (known_width * self.focal_length) / bbox_width
        
        return distance
    
    def estimate_distance(self, 
                         frame: np.ndarray,
                         object_class: str,
                         bbox: list,
                         left_frame: Optional[np.ndarray] = None,
                         right_frame: Optional[np.ndarray] = None) -> Tuple[float, str]:
        """
        Estimate distance using best available method
        
        Args:
            frame: Main camera frame
            object_class: Object class name
            bbox: Bounding box [x1, y1, x2, y2]
            left_frame: Left stereo frame (if available)
            right_frame: Right stereo frame (if available)
        
        Returns:
            (distance_in_meters, method_used)
        """
        x1, y1, x2, y2 = bbox
        bbox_width = x2 - x1
        
        # Method 1: Stereo (most accurate)
        if self.use_stereo and left_frame is not None and right_frame is not None:
            try:
                disparity = self.stereo.compute_disparity(left_frame, right_frame)
                distance = self.stereo.get_object_depth_stereo(disparity, bbox)
                
                if distance < 50:  # Sanity check
                    return distance, 'stereo'
            except:
                pass
        
        # Method 2: Monocular depth (good accuracy)
        if self.use_monocular and self.monocular and self.monocular.available:
            try:
                depth_map = self.monocular.estimate_depth(frame)
                depth_value = self.monocular.get_object_depth(depth_map, bbox)
                
                # Convert normalized depth to meters (calibration needed)
                # This is an approximation - needs calibration
                distance = 10.0 * (1.0 - depth_value)  # Closer objects = higher depth value
                
                if 0.1 < distance < 50:  # Sanity check
                    return distance, 'monocular'
            except:
                pass
        
        # Method 3: Triangulation (fallback)
        if self.use_triangulation:
            distance = self.estimate_distance_triangulation(object_class, bbox_width)
            return distance, 'triangulation'
        
        return float('inf'), 'none'
    
    def calibrate_monocular(self, frames_with_known_distances: list):
        """
        Calibrate monocular depth to real-world distances
        
        Args:
            frames_with_known_distances: List of (frame, bbox, true_distance)
        """
        # Collect depth values vs true distances
        depth_values = []
        true_distances = []
        
        for frame, bbox, true_dist in frames_with_known_distances:
            if self.monocular and self.monocular.available:
                depth_map = self.monocular.estimate_depth(frame)
                depth_val = self.monocular.get_object_depth(depth_map, bbox)
                
                depth_values.append(depth_val)
                true_distances.append(true_dist)
        
        # Fit linear model: distance = a * depth + b
        if len(depth_values) > 5:
            depth_values = np.array(depth_values)
            true_distances = np.array(true_distances)
            
            # Simple linear regression
            A = np.vstack([depth_values, np.ones(len(depth_values))]).T
            self.monocular_scale, self.monocular_offset = np.linalg.lstsq(A, true_distances, rcond=None)[0]
            
            print(f"✅ Monocular calibration: distance = {self.monocular_scale:.2f} * depth + {self.monocular_offset:.2f}")


# Test module
if __name__ == "__main__":
    print("Testing Depth Estimation...")
    
    # Test hybrid estimator
    estimator = HybridDepthEstimator(
        use_monocular=False,  # Set True if you have MiDaS model
        use_stereo=False,     # Set True if you have stereo cameras
        use_triangulation=True
    )
    
    # Test with webcam
    cap = cv2.VideoCapture(0)
    
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Simulate detection
        h, w = frame.shape[:2]
        bbox = [w//3, h//3, 2*w//3, 2*h//3]  # Center region
        
        # Estimate distance
        distance, method = estimator.estimate_distance(
            frame, 'person', bbox
        )
        
        # Draw bbox and distance
        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
        cv2.putText(
            frame,
            f"Distance: {distance:.2f}m ({method})",
            (bbox[0], bbox[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )
        
        cv2.imshow('Depth Estimation Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("Test complete!")
