"""
COMPLETE NAVIGATION ASSISTANT SYSTEM
Integrated with all features: Detection, Distance, Audio, Face Recognition, SLAM, Haptic, Data Logging

Author: Navigation Assistant Team
Version: 2.0 - Full Integration
"""

import cv2
import time
import numpy as np
from datetime import datetime
import os
import sys
import argparse

# Import all modules
from modules.object_detector import ObjectDetector
from modules.distance_estimator import DistanceEstimator
from modules.audio_feedback import AudioFeedback

# Optional modules with fallback
try:
    from modules.face_recognition import FaceRecognitionModule
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("⚠️ Face recognition not available (optional)")

try:
    from modules.gps_navigation import GPSNavigationModule
    GPS_AVAILABLE = True
except ImportError:
    GPS_AVAILABLE = False
    print("⚠️ GPS navigation not available (optional)")

try:
    from modules.slam_navigation import SLAMNavigationModule
    SLAM_AVAILABLE = True
except ImportError:
    SLAM_AVAILABLE = False
    print("⚠️ SLAM navigation not available (optional)")

try:
    from modules.haptic_feedback import HapticFeedbackModule
    HAPTIC_AVAILABLE = True
except ImportError:
    HAPTIC_AVAILABLE = False
    print("⚠️ Haptic feedback not available (optional)")

try:
    from modules.data_logger import DataLogger
    LOGGING_AVAILABLE = True
except ImportError:
    LOGGING_AVAILABLE = False
    print("⚠️ Data logging not available (optional)")

from config import *


class NavigationAssistant:
    """
    Complete Navigation Assistant with all features
    """
    
    def __init__(self, enable_slam=False, enable_logging=False, enable_face_recognition=True):
        """Initialize the complete system"""
        self.print_header()
        
        print("Initializing Complete Navigation System...")
        print("-" * 70)
        
        # === CORE MODULES (Required) ===
        print("\n[CORE MODULES]")
        self.detector = ObjectDetector()
        self.distance_estimator = DistanceEstimator()
        self.audio = AudioFeedback()
        
        # === OPTIONAL MODULES ===
        print("\n[OPTIONAL MODULES]")
        
        # Face Recognition
        self.face_recognition = None
        self.use_face_recognition = False
        if FACE_RECOGNITION_AVAILABLE and enable_face_recognition:
            try:
                self.face_recognition = FaceRecognitionModule()
                if len(self.face_recognition.known_names) > 0:
                    self.use_face_recognition = True
                    print(f"✅ Face Recognition: {len(self.face_recognition.known_names)} people")
                else:
                    print("⚠️ Face Recognition: No faces in database")
            except Exception as e:
                print(f"⚠️ Face Recognition disabled: {e}")
        else:
            print("⚠️ Face Recognition: Disabled")
        
        # SLAM Indoor Navigation
        self.slam = None
        self.use_slam = False
        if SLAM_AVAILABLE and enable_slam:
            try:
                self.slam = SLAMNavigationModule()
                self.use_slam = True
                print("✅ SLAM Indoor Navigation: Active")
            except Exception as e:
                print(f"⚠️ SLAM disabled: {e}")
        else:
            print("⚠️ SLAM: Disabled")
        
        # Haptic Feedback
        self.haptic = None
        self.use_haptic = False
        if HAPTIC_AVAILABLE:
            try:
                self.haptic = HapticFeedbackModule()
                self.use_haptic = self.haptic.enabled
                if self.use_haptic:
                    print("✅ Haptic Feedback: Active")
                else:
                    print("⚠️ Haptic Feedback: Simulation mode")
            except Exception as e:
                print(f"⚠️ Haptic disabled: {e}")
        else:
            print("⚠️ Haptic Feedback: Not available")
        
        # Data Logging
        self.logger = None
        self.use_logging = False
        if LOGGING_AVAILABLE and enable_logging:
            try:
                self.logger = DataLogger()
                self.use_logging = True
                print("✅ Data Logging: Active")
            except Exception as e:
                print(f"⚠️ Logging disabled: {e}")
        else:
            print("⚠️ Data Logging: Disabled")
        
        # GPS Navigation
        self.gps = None
        self.use_gps = False
        if GPS_AVAILABLE:
            try:
                self.gps = GPSNavigationModule()
                self.use_gps = True
                print("✅ GPS Navigation: Active")
            except Exception as e:
                print(f"⚠️ GPS disabled: {e}")
        else:
            print("⚠️ GPS Navigation: Not available")
        
        # === CAMERA SETUP ===
        print("\n[CAMERA INITIALIZATION]")
        self.cap = cv2.VideoCapture(CAMERA_ID)
        
        if not self.cap.isOpened():
            raise Exception(f"❌ Cannot open camera {CAMERA_ID}")
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, FPS)
        
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"✅ Camera: {actual_width}x{actual_height}")
        
        # === STATE VARIABLES ===
        self.frame_count = 0
        self.fps = 0
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.processing_time = 0
        
        self.paused = False
        self.debug_mode = DEBUG_MODE
        self.audio_enabled = True
        self.show_map = False
        
        # Statistics
        self.total_detections = 0
        self.total_alerts = 0
        self.session_start = datetime.now()
        
        # Calibration
        self.calibration_mode = False
        
        print("-" * 70)
        print("✅ ALL SYSTEMS READY!")
        print()
        
        self.audio.speak("Navigation assistant fully activated")
    
    def print_header(self):
        """Print application header"""
        print()
        print("=" * 70)
        print(" " * 15 + "COMPLETE NAVIGATION ASSISTANT")
        print(" " * 10 + "Advanced AI System for Visually Impaired")
        print("=" * 70)
        print()
    
    def calculate_fps(self):
        """Calculate frames per second"""
        self.fps_counter += 1
        elapsed = time.time() - self.fps_start_time
        
        if elapsed > 1.0:
            self.fps = self.fps_counter / elapsed
            self.fps_counter = 0
            self.fps_start_time = time.time()
    
    def process_frame(self, frame):
        """Main processing pipeline"""
        start_time = time.time()
        
        # 1. OBJECT DETECTION
        detections = self.detector.detect_objects(frame)
        self.total_detections += len(detections)
        
        # 2. DISTANCE ESTIMATION
        frame_width = frame.shape[1]
        detections = self.distance_estimator.process_detections(detections, frame_width)
        
        # 3. FILTER PRIORITY OBJECTS
        priority_detections = self.detector.filter_priority_objects(detections)
        
        # 4. AUDIO ALERTS
        if self.audio_enabled and not self.paused and priority_detections:
            self.audio.announce_detections(priority_detections)
            self.total_alerts += 1
            
            # 5. HAPTIC FEEDBACK
            if self.use_haptic and priority_detections:
                urgent = priority_detections[0]
                self.haptic.distance_feedback(urgent['distance'], urgent['position'])
        
        # 6. FACE RECOGNITION (every N frames)
        faces = []
        if self.use_face_recognition and self.frame_count % FACE_CHECK_INTERVAL == 0:
            faces = self.face_recognition.recognize_faces(frame)
            
            for face in faces:
                if face['name'] != "Unknown" and self.audio_enabled:
                    self.audio.announce_face(face['name'])
        
        # 7. SLAM PROCESSING
        slam_result = None
        if self.use_slam:
            slam_result = self.slam.process_frame(frame)
        
        # 8. DATA LOGGING
        if self.use_logging:
            self.logger.log_detections(self.frame_count, detections)
            self.logger.log_performance(
                self.frame_count,
                self.fps,
                self.processing_time,
                len(detections)
            )
        
        # Calculate processing time
        self.processing_time = (time.time() - start_time) * 1000
        
        return {
            'detections': detections,
            'priority_detections': priority_detections,
            'faces': faces,
            'slam_result': slam_result
        }
    
    def draw_visualizations(self, frame, results):
        """Draw all visualizations on frame"""
        detections = results['detections']
        priority_detections = results['priority_detections']
        faces = results['faces']
        
        # 1. Draw object detections
        frame = self.detector.draw_detections(frame, detections)
        
        # 2. Add distance labels
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            distance_text = f"{det['distance']:.1f}m | {det['position'].upper()}"
            
            color = self.get_urgency_color(det['category'])
            
            cv2.putText(
                frame, distance_text,
                (x1, y2 + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, color, 2
            )
        
        # 3. Draw faces
        if self.use_face_recognition:
            frame = self.face_recognition.draw_faces(frame, faces)
        
        # 4. Draw distance zones
        frame = self.draw_distance_zones(frame)
        
        # 5. Draw directional indicator
        if priority_detections:
            frame = self.draw_directional_indicator(frame, priority_detections)
        
        # 6. Draw info panel
        frame = self.draw_info_panel(frame, results)
        
        return frame
    
    def draw_distance_zones(self, frame):
        """Draw distance zone indicators"""
        height, width = frame.shape[:2]
        overlay = frame.copy()
        
        zone_height = height // 3
        
        # Critical zone (bottom)
        cv2.rectangle(overlay, (0, height - zone_height), (width, height),
                     (0, 0, 255), -1)
        
        # Warning zone (middle)
        cv2.rectangle(overlay, (0, height - 2*zone_height), (width, height - zone_height),
                     (0, 165, 255), -1)
        
        cv2.addWeighted(overlay, 0.1, frame, 0.9, 0, frame)
        
        # Labels
        cv2.putText(frame, "CRITICAL", (width - 150, height - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, "WARNING", (width - 150, height - zone_height - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 2)
        
        return frame
    
    def draw_directional_indicator(self, frame, detections):
        """Draw directional arrows"""
        height, width = frame.shape[:2]
        urgent = detections[0]
        position = urgent['position']
        
        arrow_y = height - 100
        arrow_size = 40
        
        if position == 'left':
            cv2.arrowedLine(frame, (width//2, arrow_y), (width//2 - arrow_size, arrow_y),
                          (0, 255, 255), 3, tipLength=0.5)
            cv2.putText(frame, "OBJECT LEFT", (width//2 - 120, arrow_y + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        elif position == 'right':
            cv2.arrowedLine(frame, (width//2, arrow_y), (width//2 + arrow_size, arrow_y),
                          (0, 255, 255), 3, tipLength=0.5)
            cv2.putText(frame, "OBJECT RIGHT", (width//2 - 20, arrow_y + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        else:
            cv2.arrowedLine(frame, (width//2, arrow_y + arrow_size), (width//2, arrow_y),
                          (0, 0, 255), 3, tipLength=0.5)
            cv2.putText(frame, "OBJECT AHEAD", (width//2 - 80, arrow_y + 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        return frame
    
    def draw_info_panel(self, frame, results):
        """Draw information panel"""
        height, width = frame.shape[:2]
        
        # Background
        overlay = frame.copy()
        panel_height = 200 if self.use_slam else 160
        cv2.rectangle(overlay, (10, 10), (360, panel_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Border
        cv2.rectangle(frame, (10, 10), (360, panel_height), (0, 255, 0), 2)
        
        # Text info
        y = 35
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # FPS
        color = (0, 255, 0) if self.fps > 15 else (0, 165, 255)
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (20, y), font, 0.6, color, 2)
        
        # Processing time
        y += 30
        cv2.putText(frame, f"Processing: {self.processing_time:.0f}ms", (20, y),
                   font, 0.6, (255, 255, 255), 2)
        
        # Detections
        y += 30
        cv2.putText(frame, f"Objects: {len(results['detections'])}", (20, y),
                   font, 0.6, (255, 255, 255), 2)
        
        # Status
        y += 30
        status = "PAUSED" if self.paused else "ACTIVE"
        status_color = (0, 165, 255) if self.paused else (0, 255, 0)
        cv2.putText(frame, f"Status: {status}", (20, y), font, 0.6, status_color, 2)
        
        # Most urgent detection
        if results['priority_detections']:
            urgent = results['priority_detections'][0]
            
            y += 35
            cv2.putText(frame, "ALERT:", (20, y), font, 0.5, (0, 255, 255), 1)
            
            y += 25
            color = self.get_urgency_color(urgent['category'])
            cv2.putText(frame, urgent['class'].upper(), (20, y), font, 0.6, color, 2)
            
            y += 25
            text = f"{urgent['distance']:.1f}m {urgent['position'].upper()}"
            cv2.putText(frame, text, (20, y), font, 0.5, (255, 255, 255), 2)
        
        # SLAM info
        if self.use_slam and results['slam_result']:
            y += 30
            cv2.putText(frame, f"Map Points: {results['slam_result']['num_map_points']}",
                       (20, y), font, 0.5, (255, 255, 0), 1)
        
        # Controls
        y = height - 20
        cv2.putText(frame, "Q:Quit | SPACE:Pause | H:Help | M:Map", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def get_urgency_color(self, category):
        """Get color based on urgency"""
        colors = {
            'critical': (0, 0, 255),
            'warning': (0, 165, 255),
            'safe': (0, 255, 0),
            'far': (255, 255, 255)
        }
        return colors.get(category, (255, 255, 255))
    
    def show_slam_map(self):
        """Show SLAM map in separate window"""
        if self.use_slam:
            map_view = self.slam.visualize_map()
            if map_view is not None:
                cv2.imshow('SLAM Map - Indoor Navigation', map_view)
    
    def print_controls(self):
        """Print keyboard controls"""
        print("\n" + "=" * 70)
        print("KEYBOARD CONTROLS:")
        print("-" * 70)
        print("Q          - Quit application")
        print("SPACE      - Pause/Resume")
        print("D          - Toggle debug display")
        print("A          - Toggle audio alerts")
        print("M          - Toggle SLAM map view")
        print("F          - Toggle face recognition")
        print("S          - Show statistics")
        print("H          - Show this help")
        print("C          - Calibrate distance")
        print("=" * 70)
        print()
    
    def show_statistics(self):
        """Display session statistics"""
        uptime = datetime.now() - self.session_start
        
        print("\n" + "=" * 70)
        print("SESSION STATISTICS")
        print("-" * 70)
        print(f"Uptime:              {uptime}")
        print(f"Total Frames:        {self.frame_count}")
        print(f"Total Detections:    {self.total_detections}")
        print(f"Total Alerts:        {self.total_alerts}")
        print(f"Average FPS:         {self.fps:.1f}")
        print(f"Face Recognition:    {'ON' if self.use_face_recognition else 'OFF'}")
        print(f"SLAM Navigation:     {'ON' if self.use_slam else 'OFF'}")
        print(f"Haptic Feedback:     {'ON' if self.use_haptic else 'OFF'}")
        print(f"Data Logging:        {'ON' if self.use_logging else 'OFF'}")
        print("=" * 70)
    
    def run(self):
        """Main application loop"""
        self.print_controls()
        
        print("🎥 Camera feed starting...")
        print("🔊 Audio alerts active")
        print("✅ System is now LIVE!")
        print()
        
        try:
            while True:
                if not self.paused:
                    # Read frame
                    ret, frame = self.cap.read()
                    if not ret:
                        print("❌ Failed to read frame")
                        break
                    
                    # Calculate FPS
                    self.calculate_fps()
                    self.frame_count += 1
                    
                    # Process frame
                    results = self.process_frame(frame)
                    
                    # Draw visualizations
                    if self.debug_mode:
                        frame = self.draw_visualizations(frame, results)
                    
                    # Show frame
                    cv2.imshow('Navigation Assistant - Press H for help', frame)
                    
                    # Show SLAM map
                    if self.show_map and self.use_slam:
                        self.show_slam_map()
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q') or key == ord('Q'):
                    print("\n🛑 Shutting down...")
                    self.audio.speak("Navigation assistant deactivating")
                    break
                
                elif key == ord(' '):
                    self.paused = not self.paused
                    status = "Paused" if self.paused else "Resumed"
                    print(f"⏸️  {status}")
                    self.audio.speak(status)
                
                elif key == ord('d') or key == ord('D'):
                    self.debug_mode = not self.debug_mode
                    status = "ON" if self.debug_mode else "OFF"
                    print(f"🐛 Debug mode: {status}")
                
                elif key == ord('a') or key == ord('A'):
                    self.audio_enabled = not self.audio_enabled
                    status = "ON" if self.audio_enabled else "OFF"
                    print(f"🔊 Audio: {status}")
                    if self.audio_enabled:
                        self.audio.speak("Audio enabled")
                
                elif key == ord('m') or key == ord('M'):
                    if self.use_slam:
                        self.show_map = not self.show_map
                        if not self.show_map:
                            cv2.destroyWindow('SLAM Map - Indoor Navigation')
                        print(f"🗺️  SLAM Map: {'ON' if self.show_map else 'OFF'}")
                    else:
                        print("⚠️  SLAM not available")
                
                elif key == ord('f') or key == ord('F'):
                    if self.face_recognition:
                        self.use_face_recognition = not self.use_face_recognition
                        status = "ON" if self.use_face_recognition else "OFF"
                        print(f"👤 Face Recognition: {status}")
                        self.audio.speak(f"Face recognition {status}")
                    else:
                        print("⚠️  Face recognition not available")
                
                elif key == ord('s') or key == ord('S'):
                    self.show_statistics()
                
                elif key == ord('h') or key == ord('H'):
                    self.print_controls()
        
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up resources...")
        
        # Show final stats
        self.show_statistics()
        
        # Save SLAM map
        if self.use_slam:
            self.slam.save_map()
        
        # Finalize logging
        if self.use_logging:
            self.logger.finalize()
        
        # Cleanup haptic
        if self.use_haptic:
            self.haptic.cleanup()
        
        # Release camera
        if self.cap:
            self.cap.release()
        
        # Close windows
        cv2.destroyAllWindows()
        
        print("✅ Shutdown complete")
        print("Thank you for using Navigation Assistant!")
        print()


def main():
    """Entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Navigation Assistant for Visually Impaired')
    parser.add_argument('--slam', action='store_true', help='Enable SLAM indoor navigation')
    parser.add_argument('--log', action='store_true', help='Enable data logging')
    parser.add_argument('--no-face', action='store_true', help='Disable face recognition')
    
    args = parser.parse_args()
    
    try:
        # Create and run assistant
        assistant = NavigationAssistant(
            enable_slam=args.slam,
            enable_logging=args.log,
            enable_face_recognition=not args.no_face
        )
        assistant.run()
    
    except Exception as e:
        print(f"\n❌ Failed to start: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()