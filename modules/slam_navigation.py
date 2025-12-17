"""
SLAM (Simultaneous Localization and Mapping) Module
For indoor navigation without GPS
Uses visual odometry and feature tracking
"""

import cv2
import numpy as np
from collections import deque
import time
import pickle
import os

from config import *


class SLAMNavigationModule:
    """
    Simplified SLAM implementation for indoor navigation
    Uses ORB features for mapping and localization
    """
    
    def __init__(self):
        """Initialize SLAM system"""
        print("Initializing SLAM navigation...")
        
        # Feature detector (ORB - fast and free)
        self.orb = cv2.ORB_create(
            nfeatures=2000,
            scaleFactor=1.2,
            nlevels=8,
            edgeThreshold=31,
            firstLevel=0,
            WTA_K=2,
            scoreType=cv2.ORB_HARRIS_SCORE,
            patchSize=31
        )
        
        # Feature matcher
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
        
        # Camera intrinsics (calibrate for your camera)
        self.camera_matrix = np.array([
            [700, 0, 320],  # fx, 0, cx
            [0, 700, 240],  # 0, fy, cy
            [0, 0, 1]
        ], dtype=np.float32)
        
        self.dist_coeffs = np.zeros(5)  # Assuming no distortion
        
        # Map storage
        self.map_points_3d = []  # 3D points in world coordinates
        self.map_descriptors = []  # Descriptors for each point
        self.keyframes = []  # Reference frames
        
        # Current state
        self.current_pose = np.eye(4)  # 4x4 transformation matrix
        self.trajectory = []  # List of poses
        
        # Previous frame data
        self.prev_frame = None
        self.prev_keypoints = None
        self.prev_descriptors = None
        
        # Settings
        self.min_matches = 15
        self.max_trajectory_length = 1000
        
        print("✅ SLAM system ready")
    
    def process_frame(self, frame):
        """
        Process new frame and update map
        
        Args:
            frame: Input image (BGR)
        
        Returns:
            Dictionary with processing results
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect features
        keypoints, descriptors = self.orb.detectAndCompute(gray, None)
        
        result = {
            'num_features': len(keypoints),
            'num_map_points': len(self.map_points_3d),
            'pose': self.current_pose.copy(),
            'trajectory_length': len(self.trajectory)
        }
        
        if self.prev_descriptors is not None:
            # Match features with previous frame
            matches = self.match_features(self.prev_descriptors, descriptors)
            
            if len(matches) >= self.min_matches:
                # Estimate camera motion
                R, t, points_3d = self.estimate_motion(
                    self.prev_keypoints, keypoints, matches
                )
                
                if R is not None:
                    # Update pose
                    self.update_pose(R, t)
                    
                    # Add points to map
                    if points_3d is not None and len(points_3d) > 0:
                        self.add_to_map(points_3d, keypoints, descriptors, matches)
                    
                    result['motion_estimated'] = True
                else:
                    result['motion_estimated'] = False
            else:
                result['motion_estimated'] = False
                result['insufficient_matches'] = True
        
        # Update previous frame data
        self.prev_frame = gray
        self.prev_keypoints = keypoints
        self.prev_descriptors = descriptors
        
        return result
    
    def match_features(self, desc1, desc2):
        """
        Match features between two frames
        
        Returns:
            List of good matches
        """
        if desc1 is None or desc2 is None:
            return []
        
        # Match descriptors
        matches = self.matcher.knnMatch(desc1, desc2, k=2)
        
        # Apply Lowe's ratio test
        good_matches = []
        for match_pair in matches:
            if len(match_pair) == 2:
                m, n = match_pair
                if m.distance < 0.75 * n.distance:
                    good_matches.append(m)
        
        return good_matches
    
    def estimate_motion(self, kp1, kp2, matches):
        """
        Estimate camera motion between frames
        
        Returns:
            (R, t, points_3d) - Rotation, translation, and 3D points
        """
        if len(matches) < self.min_matches:
            return None, None, None
        
        # Extract matched point coordinates
        pts1 = np.float32([kp1[m.queryIdx].pt for m in matches])
        pts2 = np.float32([kp2[m.trainIdx].pt for m in matches])
        
        # Find essential matrix
        E, mask = cv2.findEssentialMat(
            pts1, pts2,
            self.camera_matrix,
            method=cv2.RANSAC,
            prob=0.999,
            threshold=1.0
        )
        
        if E is None:
            return None, None, None
        
        # Recover pose
        _, R, t, mask = cv2.recoverPose(
            E, pts1, pts2,
            self.camera_matrix,
            mask=mask
        )
        
        # Triangulate points
        points_3d = self.triangulate_points(pts1, pts2, R, t, mask)
        
        return R, t, points_3d
    
    def triangulate_points(self, pts1, pts2, R, t, mask):
        """
        Triangulate 3D points from 2D correspondences
        """
        # Projection matrices
        P1 = self.camera_matrix @ np.hstack([np.eye(3), np.zeros((3, 1))])
        P2 = self.camera_matrix @ np.hstack([R, t])
        
        # Triangulate
        points_4d = cv2.triangulatePoints(P1, P2, pts1.T, pts2.T)
        
        # Convert to 3D
        points_3d = points_4d[:3] / points_4d[3]
        points_3d = points_3d.T
        
        # Filter points behind camera or too far
        valid_points = []
        for point in points_3d:
            if point[2] > 0 and point[2] < 50:  # Between 0 and 50 meters
                valid_points.append(point)
        
        return np.array(valid_points) if valid_points else None
    
    def update_pose(self, R, t):
        """
        Update current camera pose
        """
        # Create transformation matrix
        T = np.eye(4)
        T[:3, :3] = R
        T[:3, 3] = t.reshape(3)
        
        # Update global pose
        self.current_pose = self.current_pose @ T
        
        # Add to trajectory
        self.trajectory.append(self.current_pose.copy())
        
        # Limit trajectory length
        if len(self.trajectory) > self.max_trajectory_length:
            self.trajectory.pop(0)
    
    def add_to_map(self, points_3d, keypoints, descriptors, matches):
        """
        Add new 3D points to map
        """
        if points_3d is None or len(points_3d) == 0:
            return
        
        # Transform points to world coordinates
        R = self.current_pose[:3, :3]
        t = self.current_pose[:3, 3]
        
        world_points = (R @ points_3d.T).T + t
        
        # Add to map
        for i, point in enumerate(world_points):
            if i < len(matches):
                match = matches[i]
                desc = descriptors[match.trainIdx]
                
                self.map_points_3d.append(point)
                self.map_descriptors.append(desc)
    
    def get_current_position(self):
        """
        Get current camera position
        
        Returns:
            (x, y, z) position in meters
        """
        position = self.current_pose[:3, 3]
        return tuple(position)
    
    def get_current_orientation(self):
        """
        Get current camera orientation
        
        Returns:
            (roll, pitch, yaw) in degrees
        """
        R = self.current_pose[:3, :3]
        
        # Extract Euler angles
        sy = np.sqrt(R[0, 0]**2 + R[1, 0]**2)
        
        if sy > 1e-6:
            roll = np.arctan2(R[2, 1], R[2, 2])
            pitch = np.arctan2(-R[2, 0], sy)
            yaw = np.arctan2(R[1, 0], R[0, 0])
        else:
            roll = np.arctan2(-R[1, 2], R[1, 1])
            pitch = np.arctan2(-R[2, 0], sy)
            yaw = 0
        
        # Convert to degrees
        return (
            np.degrees(roll),
            np.degrees(pitch),
            np.degrees(yaw)
        )
    
    def visualize_map(self, size=(800, 800), scale=50):
        """
        Create top-down view of mapped environment
        
        Args:
            size: Image size (width, height)
            scale: Pixels per meter
        
        Returns:
            Visualization image
        """
        if len(self.map_points_3d) < 10:
            # Not enough points
            img = np.zeros((size[1], size[0], 3), dtype=np.uint8)
            cv2.putText(
                img, "Insufficient map data",
                (size[0]//2 - 100, size[1]//2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (255, 255, 255), 2
            )
            return img
        
        points = np.array(self.map_points_3d)
        
        # Create image
        img = np.zeros((size[1], size[0], 3), dtype=np.uint8)
        
        # Project 3D points to 2D (top-down view)
        x = points[:, 0]
        z = points[:, 2]
        
        # Center and scale
        center_x = size[0] // 2
        center_y = size[1] // 2
        
        # Draw points
        for xi, zi in zip(x, z):
            px = int(center_x + xi * scale)
            py = int(center_y + zi * scale)
            
            if 0 <= px < size[0] and 0 <= py < size[1]:
                cv2.circle(img, (px, py), 2, (0, 255, 0), -1)
        
        # Draw trajectory
        if len(self.trajectory) > 1:
            trajectory_points = []
            for pose in self.trajectory:
                pos = pose[:3, 3]
                px = int(center_x + pos[0] * scale)
                py = int(center_y + pos[2] * scale)
                
                if 0 <= px < size[0] and 0 <= py < size[1]:
                    trajectory_points.append((px, py))
            
            # Draw path
            for i in range(len(trajectory_points) - 1):
                cv2.line(
                    img,
                    trajectory_points[i],
                    trajectory_points[i + 1],
                    (255, 0, 0), 2
                )
        
        # Draw current position
        current_pos = self.current_pose[:3, 3]
        curr_px = int(center_x + current_pos[0] * scale)
        curr_py = int(center_y + current_pos[2] * scale)
        
        if 0 <= curr_px < size[0] and 0 <= curr_py < size[1]:
            cv2.circle(img, (curr_px, curr_py), 8, (0, 0, 255), -1)
            
            # Draw orientation arrow
            roll, pitch, yaw = self.get_current_orientation()
            arrow_length = 30
            end_x = int(curr_px + arrow_length * np.cos(np.radians(yaw)))
            end_y = int(curr_py + arrow_length * np.sin(np.radians(yaw)))
            
            cv2.arrowedLine(
                img,
                (curr_px, curr_py),
                (end_x, end_y),
                (0, 255, 255), 3, tipLength=0.3
            )
        
        # Draw grid
        grid_spacing = scale  # 1 meter
        for i in range(0, size[0], grid_spacing):
            cv2.line(img, (i, 0), (i, size[1]), (50, 50, 50), 1)
        for i in range(0, size[1], grid_spacing):
            cv2.line(img, (0, i), (size[0], i), (50, 50, 50), 1)
        
        # Draw center cross
        cv2.line(img, (center_x - 10, center_y), (center_x + 10, center_y), (100, 100, 100), 1)
        cv2.line(img, (center_x, center_y - 10), (center_x, center_y + 10), (100, 100, 100), 1)
        
        # Add text info
        position = self.get_current_position()
        orientation = self.get_current_orientation()
        
        info_text = [
            f"Map Points: {len(self.map_points_3d)}",
            f"Position: ({position[0]:.2f}, {position[1]:.2f}, {position[2]:.2f})m",
            f"Yaw: {orientation[2]:.1f} deg"
        ]
        
        y_offset = 30
        for text in info_text:
            cv2.putText(
                img, text, (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (255, 255, 255), 1
            )
            y_offset += 25
        
        return img
    
    def save_map(self, filename="data/slam_map.pkl"):
        """
        Save map to file
        """
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        map_data = {
            'points_3d': self.map_points_3d,
            'descriptors': self.map_descriptors,
            'trajectory': self.trajectory,
            'camera_matrix': self.camera_matrix
        }
        
        with open(filename, 'wb') as f:
            pickle.dump(map_data, f)
        
        print(f"✅ Map saved: {filename}")
    
    def load_map(self, filename="data/slam_map.pkl"):
        """
        Load map from file
        """
        if not os.path.exists(filename):
            print(f"⚠️ Map file not found: {filename}")
            return False
        
        try:
            with open(filename, 'rb') as f:
                map_data = pickle.load(f)
            
            self.map_points_3d = map_data['points_3d']
            self.map_descriptors = map_data['descriptors']
            self.trajectory = map_data['trajectory']
            self.camera_matrix = map_data['camera_matrix']
            
            print(f"✅ Map loaded: {len(self.map_points_3d)} points")
            return True
        
        except Exception as e:
            print(f"❌ Error loading map: {e}")
            return False
    
    def reset(self):
        """Reset SLAM system"""
        self.map_points_3d = []
        self.map_descriptors = []
        self.keyframes = []
        self.current_pose = np.eye(4)
        self.trajectory = []
        self.prev_frame = None
        self.prev_keypoints = None
        self.prev_descriptors = None
        
        print("✅ SLAM system reset")


# Test the module
if __name__ == "__main__":
    print("="*60)
    print("SLAM NAVIGATION TEST")
    print("="*60)
    print()
    
    slam = SLAMNavigationModule()
    
    # Open camera
    cap = cv2.VideoCapture(0)
    
    print("SLAM system active")
    print("Controls:")
    print("  Q - Quit")
    print("  S - Save map")
    print("  L - Load map")
    print("  R - Reset")
    print("  M - Show map")
    print()
    
    show_map = False
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Process frame
        result = slam.process_frame(frame)
        
        # Draw features on frame
        if slam.prev_keypoints:
            for kp in slam.prev_keypoints:
                x, y = kp.pt
                cv2.circle(frame, (int(x), int(y)), 3, (0, 255, 0), -1)
        
        # Display info
        info_text = [
            f"Features: {result['num_features']}",
            f"Map Points: {result['num_map_points']}",
            f"Frames: {frame_count}"
        ]
        
        y_offset = 30
        for text in info_text:
            cv2.putText(
                frame, text, (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (0, 255, 0), 2
            )
            y_offset += 30
        
        # Show current position
        position = slam.get_current_position()
        cv2.putText(
            frame,
            f"Pos: ({position[0]:.2f}, {position[1]:.2f}, {position[2]:.2f})",
            (10, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5, (255, 255, 0), 1
        )
        
        cv2.imshow('SLAM - Camera View', frame)
        
        # Show map view
        if show_map:
            map_view = slam.visualize_map()
            cv2.imshow('SLAM - Map View', map_view)

        # Handle keys
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('s'):
            slam.save_map()
        elif key == ord('l'):
            slam.load_map()
        elif key == ord('r'):
            slam.reset()
        elif key == ord('m'):
            show_map = not show_map
            if not show_map:
                cv2.destroyWindow('SLAM - Map View')

    cap.release()
    cv2.destroyAllWindows()

    print("\n✅ SLAM test complete")