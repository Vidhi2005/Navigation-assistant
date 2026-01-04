"""
Dataset Collection Tool for Navigation Assistant
Helps collect and annotate navigation-specific images
"""

import cv2
import os
import json
from datetime import datetime
from pathlib import Path
import numpy as np


class DatasetCollector:
    """
    Interactive tool for collecting navigation dataset
    """
    
    def __init__(self, output_dir='datasets/navigation_custom'):
        self.output_dir = Path(output_dir)
        self.setup_directories()
        
        # Navigation-specific classes
        self.classes = [
            'person', 'wheelchair', 'cane', 'walker',
            'stairs_up', 'stairs_down', 'escalator', 'elevator',
            'curb', 'pothole', 'uneven_surface',
            'traffic_light', 'crosswalk', 'zebra_crossing',
            'door_open', 'door_closed', 'automatic_door',
            'pole', 'pillar', 'wall', 'barrier',
            'bench', 'table', 'chair',
            'vehicle_car', 'vehicle_bike', 'vehicle_bus'
        ]
        
        self.current_class = 0
        self.image_count = 0
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        print("=" * 70)
        print("NAVIGATION DATASET COLLECTOR")
        print("=" * 70)
        print(f"\nCollecting images for: {len(self.classes)} classes")
        print(f"Output directory: {self.output_dir}")
        print("\nControls:")
        print("  SPACE  - Capture image")
        print("  LEFT   - Previous class")
        print("  RIGHT  - Next class")
        print("  S      - Save session")
        print("  Q      - Quit")
        print("=" * 70)
    
    def setup_directories(self):
        """Create directory structure"""
        dirs = [
            'raw_images',
            'annotations',
            'metadata'
        ]
        
        for dir_name in dirs:
            (self.output_dir / dir_name).mkdir(parents=True, exist_ok=True)
    
    def run(self, camera_id=0):
        """Start collection session"""
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            print(f"❌ Cannot open camera {camera_id}")
            return
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Draw UI
            display = self.draw_ui(frame.copy())
            
            # Show
            cv2.imshow('Dataset Collector', display)
            
            # Handle keys
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord(' '):
                self.capture_image(frame)
            elif key == 83:  # Right arrow
                self.next_class()
            elif key == 81:  # Left arrow
                self.previous_class()
            elif key == ord('s'):
                self.save_session()
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"\n✅ Collection complete: {self.image_count} images")
    
    def draw_ui(self, frame):
        """Draw collection UI"""
        h, w = frame.shape[:2]
        
        # Semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 150), (0, 0, 0), -1)
        cv2.rectangle(overlay, (0, h - 100), (w, h), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
        
        # Current class
        class_name = self.classes[self.current_class]
        cv2.putText(
            frame, f"Class: {class_name}",
            (20, 50), cv2.FONT_HERSHEY_SIMPLEX,
            1.5, (0, 255, 0), 3
        )
        
        # Progress
        cv2.putText(
            frame, f"Class {self.current_class + 1}/{len(self.classes)}",
            (20, 100), cv2.FONT_HERSHEY_SIMPLEX,
            0.8, (255, 255, 255), 2
        )
        
        # Image count
        cv2.putText(
            frame, f"Images: {self.image_count}",
            (20, h - 60), cv2.FONT_HERSHEY_SIMPLEX,
            0.8, (255, 255, 255), 2
        )
        
        # Instructions
        cv2.putText(
            frame, "SPACE: Capture | ARROWS: Change Class | Q: Quit",
            (20, h - 20), cv2.FONT_HERSHEY_SIMPLEX,
            0.6, (200, 200, 200), 2
        )
        
        # Center crosshair
        cv2.line(frame, (w//2 - 30, h//2), (w//2 + 30, h//2), (0, 255, 0), 2)
        cv2.line(frame, (w//2, h//2 - 30), (w//2, h//2 + 30), (0, 255, 0), 2)
        
        return frame
    
    def capture_image(self, frame):
        """Capture and save image"""
        class_name = self.classes[self.current_class]
        
        # Generate filename
        filename = f"{self.session_id}_{class_name}_{self.image_count:04d}.jpg"
        
        # Save image
        img_path = self.output_dir / 'raw_images' / filename
        cv2.imwrite(str(img_path), frame)
        
        # Save metadata
        metadata = {
            'filename': filename,
            'class': class_name,
            'class_id': self.current_class,
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'resolution': frame.shape[:2][::-1]
        }
        
        meta_path = self.output_dir / 'metadata' / f"{filename}.json"
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.image_count += 1
        
        print(f"✅ Captured: {class_name} ({self.image_count})")
    
    def next_class(self):
        """Move to next class"""
        self.current_class = (self.current_class + 1) % len(self.classes)
        class_name = self.classes[self.current_class]
        print(f"→ Class: {class_name}")
    
    def previous_class(self):
        """Move to previous class"""
        self.current_class = (self.current_class - 1) % len(self.classes)
        class_name = self.classes[self.current_class]
        print(f"← Class: {class_name}")
    
    def save_session(self):
        """Save collection session summary"""
        session_file = self.output_dir / 'metadata' / f"session_{self.session_id}.json"
        
        session_data = {
            'session_id': self.session_id,
            'total_images': self.image_count,
            'classes': self.classes,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        print(f"💾 Session saved: {session_file}")


def collect_video_dataset(video_path, output_dir='datasets/navigation_video', fps=1):
    """
    Extract frames from video for dataset
    
    Args:
        video_path: Path to video file
        output_dir: Output directory
        fps: Frames per second to extract
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"❌ Cannot open video: {video_path}")
        return
    
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(video_fps / fps)
    
    frame_count = 0
    saved_count = 0
    
    print(f"Extracting frames from: {video_path}")
    print(f"Video FPS: {video_fps}, Extracting every {frame_interval} frames")
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        if frame_count % frame_interval == 0:
            filename = f"frame_{saved_count:06d}.jpg"
            cv2.imwrite(str(output_path / filename), frame)
            saved_count += 1
            
            if saved_count % 100 == 0:
                print(f"  Saved {saved_count} frames...")
        
        frame_count += 1
    
    cap.release()
    
    print(f"✅ Extracted {saved_count} frames to {output_dir}")


# Run collector
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Dataset Collection Tool')
    parser.add_argument('--output', default='datasets/navigation_custom',
                       help='Output directory')
    parser.add_argument('--camera', type=int, default=0,
                       help='Camera ID')
    parser.add_argument('--video', type=str,
                       help='Extract from video file instead')
    parser.add_argument('--fps', type=int, default=1,
                       help='Frames per second (for video extraction)')
    
    args = parser.parse_args()
    
    if args.video:
        # Extract from video
        collect_video_dataset(args.video, args.output, args.fps)
    else:
        # Interactive collection
        collector = DatasetCollector(args.output)
        collector.run(args.camera)
