import os
import json
import csv
from datetime import datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from collections import defaultdict, Counter

from config import *


class DataLogger:
    """
    Logs navigation assistant data for analysis
    """
    
    def __init__(self, log_dir="data/logs"):
        """Initialize logger"""
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Session info
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_start = datetime.now()
        
        # Log files
        self.detection_log_file = os.path.join(
            log_dir,
            f"detections_{self.session_id}.csv"
        )
        self.event_log_file = os.path.join(
            log_dir,
            f"events_{self.session_id}.json"
        )
        self.performance_log_file = os.path.join(
            log_dir,
            f"performance_{self.session_id}.csv"
        )
        
        # Initialize CSV files
        self.init_detection_log()
        self.init_performance_log()
        
        # Event buffer
        self.events = []
        
        # Statistics
        self.stats = {
            'total_frames': 0,
            'total_detections': 0,
            'total_alerts': 0,
            'object_counts': Counter(),
            'distance_histogram': defaultdict(int),
            'position_counts': Counter(),
            'fps_history': [],
            'processing_times': []
        }
        
        print(f"✅ Data logger initialized: {self.session_id}")
    
    def init_detection_log(self):
        """Initialize detection log CSV"""
        with open(self.detection_log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp',
                'frame_number',
                'object_class',
                'confidence',
                'distance',
                'position',
                'category',
                'urgency',
                'bbox_x1',
                'bbox_y1',
                'bbox_x2',
                'bbox_y2'
            ])
    
    def init_performance_log(self):
        """Initialize performance log CSV"""
        with open(self.performance_log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp',
                'frame_number',
                'fps',
                'processing_time_ms',
                'num_detections',
                'memory_usage_mb'
            ])
    
    def log_detection(self, frame_number, detection):
        """
        Log a single detection
        
        Args:
            frame_number: Current frame number
            detection: Detection dictionary
        """
        timestamp = datetime.now().isoformat()
        
        with open(self.detection_log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                frame_number,
                detection.get('class', ''),
                detection.get('confidence', 0),
                detection.get('distance', 0),
                detection.get('position', ''),
                detection.get('category', ''),
                detection.get('urgency', 0),
                detection.get('bbox', [0,0,0,0])[0],
                detection.get('bbox', [0,0,0,0])[1],
                detection.get('bbox', [0,0,0,0])[2],
                detection.get('bbox', [0,0,0,0])[3]
            ])
        
        # Update statistics
        self.stats['total_detections'] += 1
        self.stats['object_counts'][detection.get('class', 'unknown')] += 1
        
        # Distance histogram (in 0.5m bins)
        distance = detection.get('distance', 0)
        bin_key = int(distance / 0.5) * 0.5
        self.stats['distance_histogram'][bin_key] += 1
        
        # Position counts
        self.stats['position_counts'][detection.get('position', 'unknown')] += 1
    
    def log_detections(self, frame_number, detections):
        """
        Log multiple detections from a frame
        
        Args:
            frame_number: Current frame number
            detections: List of detection dictionaries
        """
        for detection in detections:
            self.log_detection(frame_number, detection)
    
    def log_performance(self, frame_number, fps, processing_time, num_detections):
        """
        Log performance metrics
        
        Args:
            frame_number: Current frame number
            fps: Frames per second
            processing_time: Processing time in ms
            num_detections: Number of detections in frame
        """
        timestamp = datetime.now().isoformat()
        
        # Get memory usage
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
        except:
            memory_mb = 0
        
        with open(self.performance_log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                frame_number,
                fps,
                processing_time,
                num_detections,
                memory_mb
            ])
        
        # Update statistics
        self.stats['total_frames'] += 1
        self.stats['fps_history'].append(fps)
        self.stats['processing_times'].append(processing_time)
    
    def log_event(self, event_type, data):
        """
        Log a custom event
        
        Args:
            event_type: Type of event (e.g., 'alert', 'face_recognized')
            data: Event data dictionary
        """
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'data': data
        }
        
        self.events.append(event)
        
        # Update stats
        if event_type == 'alert':
            self.stats['total_alerts'] += 1
    
    def save_events(self):
        """Save events to JSON file"""
        with open(self.event_log_file, 'w') as f:
            json.dump(self.events, f, indent=2)
        
        print(f"✅ Events saved: {len(self.events)} events")
    
    def generate_report(self):
        """
        Generate comprehensive analysis report
        """
        report_file = os.path.join(
            self.log_dir,
            f"report_{self.session_id}.txt"
        )
        
        session_duration = datetime.now() - self.session_start
        
        with open(report_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("NAVIGATION ASSISTANT - SESSION REPORT\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Session ID: {self.session_id}\n")
            f.write(f"Start Time: {self.session_start}\n")
            f.write(f"Duration: {session_duration}\n\n")
            
            f.write("-"*70 + "\n")
            f.write("SUMMARY STATISTICS\n")
            f.write("-"*70 + "\n")
            f.write(f"Total Frames Processed: {self.stats['total_frames']}\n")
            f.write(f"Total Detections: {self.stats['total_detections']}\n")
            f.write(f"Total Alerts: {self.stats['total_alerts']}\n\n")
            
            if self.stats['fps_history']:
                avg_fps = np.mean(self.stats['fps_history'])
                f.write(f"Average FPS: {avg_fps:.2f}\n")
            
            if self.stats['processing_times']:
                avg_time = np.mean(self.stats['processing_times'])
                f.write(f"Average Processing Time: {avg_time:.2f}ms\n\n")
            
            f.write("-"*70 + "\n")
            f.write("DETECTED OBJECTS\n")
            f.write("-"*70 + "\n")
            for obj, count in self.stats['object_counts'].most_common():
                f.write(f"{obj}: {count}\n")
            f.write("\n")
            
            f.write("-"*70 + "\n")
            f.write("POSITION DISTRIBUTION\n")
            f.write("-"*70 + "\n")
            for position, count in self.stats['position_counts'].most_common():
                f.write(f"{position}: {count}\n")
            f.write("\n")
            
            f.write("-"*70 + "\n")
            f.write("DISTANCE DISTRIBUTION (meters)\n")
            f.write("-"*70 + "\n")
            for distance in sorted(self.stats['distance_histogram'].keys()):
                count = self.stats['distance_histogram'][distance]
                f.write(f"{distance:.1f}m - {distance+0.5:.1f}m: {count}\n")
            f.write("\n")
            
            f.write("="*70 + "\n")
        
        print(f"✅ Report generated: {report_file}")
        return report_file
    
    def generate_visualizations(self):
        """
        Generate visualization charts
        """
        viz_dir = os.path.join(self.log_dir, f"viz_{self.session_id}")
        os.makedirs(viz_dir, exist_ok=True)
        
        # 1. Object detection frequency
        if self.stats['object_counts']:
            plt.figure(figsize=(12, 6))
            objects = list(self.stats['object_counts'].keys())
            counts = list(self.stats['object_counts'].values())
            plt.bar(objects, counts, color='skyblue')
            plt.xlabel('Object Class')
            plt.ylabel('Count')
            plt.title('Object Detection Frequency')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(os.path.join(viz_dir, 'object_frequency.png'))
            plt.close()
        
        # 2. Distance histogram
        if self.stats['distance_histogram']:
            plt.figure(figsize=(10, 6))
            distances = sorted(self.stats['distance_histogram'].keys())
            counts = [self.stats['distance_histogram'][d] for d in distances]
            plt.bar(distances, counts, width=0.4, color='coral')
            plt.xlabel('Distance (meters)')
            plt.ylabel('Count')
            plt.title('Distance Distribution')
            plt.tight_layout()
            plt.savefig(os.path.join(viz_dir, 'distance_histogram.png'))
            plt.close()
        
        # 3. FPS over time
        if self.stats['fps_history']:
            plt.figure(figsize=(12, 6))
            plt.plot(self.stats['fps_history'], color='green', linewidth=1)
            plt.axhline(y=np.mean(self.stats['fps_history']), 
                       color='r', linestyle='--', label='Average')
            plt.xlabel('Frame Number')
            plt.ylabel('FPS')
            plt.title('Frames Per Second Over Time')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(os.path.join(viz_dir, 'fps_over_time.png'))
            plt.close()
        
        # 4. Processing time over time
        if self.stats['processing_times']:
            plt.figure(figsize=(12, 6))
            plt.plot(self.stats['processing_times'], color='purple', linewidth=1)
            plt.axhline(y=np.mean(self.stats['processing_times']),
                       color='r', linestyle='--', label='Average')
            plt.xlabel('Frame Number')
            plt.ylabel('Processing Time (ms)')
            plt.title('Processing Time Over Time')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(os.path.join(viz_dir, 'processing_time.png'))
            plt.close()
        
        # 5. Position distribution pie chart
        if self.stats['position_counts']:
            plt.figure(figsize=(8, 8))
            positions = list(self.stats['position_counts'].keys())
            counts = list(self.stats['position_counts'].values())
            plt.pie(counts, labels=positions, autopct='%1.1f%%', startangle=90)
            plt.title('Object Position Distribution')
            plt.tight_layout()
            plt.savefig(os.path.join(viz_dir, 'position_distribution.png'))
            plt.close()
        
        print(f"✅ Visualizations saved in: {viz_dir}")
        return viz_dir
    
    def finalize(self):
        """
        Finalize logging session and generate reports
        """
        print("\nFinalizing data logging...")
        
        # Save events
        self.save_events()
        
        # Generate report
        report_file = self.generate_report()
        
        # Generate visualizations
        try:
            viz_dir = self.generate_visualizations()
        except Exception as e:
            print(f"⚠️ Could not generate visualizations: {e}")
            viz_dir = None
        
        print("\n" + "="*70)
        print("SESSION COMPLETE")
        print("="*70)
        print(f"Session ID: {self.session_id}")
        print(f"Total Frames: {self.stats['total_frames']}")
        print(f"Total Detections: {self.stats['total_detections']}")
        print(f"Total Alerts: {self.stats['total_alerts']}")
        print(f"\nReport: {report_file}")
        if viz_dir:
            print(f"Visualizations: {viz_dir}")
        print("="*70)


# Test the module
if __name__ == "__main__":
    print("="*60)
    print("DATA LOGGER TEST")
    print("="*60)
    print()
    
    # Create logger
    logger = DataLogger()
    
    # Simulate some data
    print("Simulating detection data...")
    
    for frame in range(100):
        # Simulate detections
        num_detections = np.random.randint(0, 5)
        
        for i in range(num_detections):
            detection = {
                'class': np.random.choice(['person', 'chair', 'car', 'door']),
                'confidence': np.random.uniform(0.5, 0.99),
                'distance': np.random.uniform(0.5, 5.0),
                'position': np.random.choice(['left', 'center', 'right']),
                'category': np.random.choice(['critical', 'warning', 'safe']),
                'urgency': np.random.randint(0, 4),
                'bbox': [100, 100, 200, 200]
            }
            logger.log_detection(frame, detection)
        
        # Log performance
        fps = np.random.uniform(15, 30)
        processing_time = np.random.uniform(20, 50)
        logger.log_performance(frame, fps, processing_time, num_detections)
        
        # Random events
        if np.random.random() < 0.1:
            logger.log_event('alert', {'message': 'Obstacle detected'})
    
    print("✅ Simulation complete")
    print()
    
    # Finalize and generate reports
    logger.finalize()

