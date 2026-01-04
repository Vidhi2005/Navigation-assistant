"""
Flask API Server for Navigation Assistant
Provides REST API for mobile app
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
import base64
import io
from PIL import Image
import time
from datetime import datetime

# Import navigation modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.object_detector import ObjectDetector
from modules.distance_estimator import DistanceEstimator

app = Flask(__name__)
CORS(app)  # Enable CORS for mobile app

# Initialize modules
print("🚀 Starting Navigation Assistant API Server...")
detector = ObjectDetector()
distance_estimator = DistanceEstimator()
face_recognition_enabled = False

print(f"✅ API Server initialized")
print(f"   Object Detection: ✅")
print(f"   Face Recognition: ❌ (disabled for testing)")


# Dashboard route
@app.route('/', methods=['GET'])
def dashboard():
    """Serve the web dashboard"""
    dashboard_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dashboard.html')
    return send_file(dashboard_path)


def decode_image(base64_string):
    """
    Decode base64 image to OpenCV format
    
    Args:
        base64_string: Base64 encoded image
    
    Returns:
        OpenCV image (numpy array)
    """
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64
        img_data = base64.b64decode(base64_string)
        
        # Convert to PIL Image
        pil_image = Image.open(io.BytesIO(img_data))
        
        # Convert to OpenCV (BGR)
        opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        return opencv_image
    
    except Exception as e:
        raise ValueError(f"Failed to decode image: {e}")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'object_detection': True,
            'face_recognition': face_recognition_enabled
        }
    })


@app.route('/detect', methods=['POST'])
def detect_objects():
    """
    Object detection endpoint
    
    Request:
    {
        "image": "base64_encoded_image",
        "include_faces": false  // optional
    }
    
    Response:
    {
        "objects": [
            {
                "object": "person",
                "distance": 1.8,
                "direction": "left",
                "category": "warning",
                "confidence": 0.95
            }
        ],
        "faces": [...],  // if include_faces=true
        "timestamp": "2025-12-28T10:30:00",
        "processing_time_ms": 45
    }
    """
    start_time = time.time()
    
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Decode image
        image = decode_image(data['image'])
        frame_width = image.shape[1]
        
        # Object detection
        detections = detector.detect_objects(image)
        
        # Distance estimation
        detections = distance_estimator.process_detections(detections, frame_width)
        
        # Format response for mobile
        objects = []
        for det in detections:
            obj = {
                'object': det['class'],
                'distance': round(det['distance'], 1),
                'direction': det['position'],
                'category': det['category'],
                'confidence': round(det['confidence'], 2)
            }
            objects.append(obj)
        
        response = {
            'objects': objects,
            'timestamp': datetime.now().isoformat(),
            'processing_time_ms': round((time.time() - start_time) * 1000, 1)
        }
        
        # Face recognition (optional)
        if data.get('include_faces', False) and face_recognition_enabled:
            faces = face_recognition_module.recognize_faces(image)
            response['faces'] = [
                {
                    'name': f['name'],
                    'confidence': round(f['confidence'], 2)
                }
                for f in faces
            ]
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/detect/stream', methods=['POST'])
def detect_stream():
    """
    Optimized detection for real-time streaming
    Returns only critical information
    
    Response format optimized for audio output
    """
    start_time = time.time()
    
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Decode and process
        image = decode_image(data['image'])
        frame_width = image.shape[1]
        
        detections = detector.detect_objects(image)
        detections = distance_estimator.process_detections(detections, frame_width)
        
        # Filter priority objects only
        priority_detections = detector.filter_priority_objects(detections)
        
        # Get most urgent object
        urgent_object = None
        if priority_detections:
            # Sort by distance
            priority_detections.sort(key=lambda x: x['distance'])
            urgent = priority_detections[0]
            
            urgent_object = {
                'object': urgent['class'],
                'distance': round(urgent['distance'], 1),
                'direction': urgent['position'],
                'category': urgent['category']
            }
        
        response = {
            'urgent': urgent_object,
            'total_objects': len(detections),
            'processing_ms': round((time.time() - start_time) * 1000, 1)
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """
    Get/Update detection settings
    """
    if request.method == 'GET':
        from config import CONFIDENCE_THRESHOLD, CRITICAL_DISTANCE, WARNING_DISTANCE
        
        return jsonify({
            'confidence_threshold': CONFIDENCE_THRESHOLD,
            'critical_distance': CRITICAL_DISTANCE,
            'warning_distance': WARNING_DISTANCE,
            'face_recognition_enabled': face_recognition_enabled
        })
    
    elif request.method == 'POST':
        # Update settings (implement config changes)
        data = request.get_json()
        return jsonify({'message': 'Settings updated', 'settings': data})


@app.route('/emergency', methods=['POST'])
def emergency():
    """
    Emergency endpoint - log emergency events
    """
    data = request.get_json()
    
    # Log emergency (implement proper logging)
    print(f"🚨 EMERGENCY: {data}")
    
    return jsonify({
        'status': 'emergency_logged',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/feedback', methods=['POST'])
def feedback():
    """
    Log user feedback for improving detection
    """
    data = request.get_json()
    
    # Store feedback for model improvement
    # Implement feedback logging
    
    return jsonify({'status': 'feedback_received'})


# Development only - test with sample image
@app.route('/test', methods=['GET'])
def test():
    """Test endpoint with webcam"""
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return jsonify({'error': 'Cannot access camera', 'message': 'Camera is in use or not available'}), 500
        
        # Process frame
        detections = detector.detect_objects(frame)
        detections = distance_estimator.process_detections(detections, frame.shape[1])
        
        # Convert numpy types to Python types for JSON serialization
        objects = []
        for d in detections:
            objects.append({
                'object': str(d['class']),
                'distance': float(round(d['distance'], 1)),
                'direction': str(d['position']),
                'confidence': float(round(d['confidence'], 2))
            })
        
        return jsonify({
            'status': 'success',
            'message': 'Test successful - camera working!',
            'detections': int(len(detections)),
            'objects': objects
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'message': 'Internal error - check server logs'
        }), 500


if __name__ == '__main__':
    # Run server
    print("\n" + "="*70)
    print("🚀 NAVIGATION ASSISTANT API SERVER")
    print("="*70)
    print("\n📡 Server starting on http://0.0.0.0:5000")
    print("\nEndpoints:")
    print("  GET  /health          - Health check")
    print("  POST /detect          - Full object detection")
    print("  POST /detect/stream   - Optimized for real-time")
    print("  GET  /settings        - Get detection settings")
    print("  POST /emergency       - Log emergency event")
    print("  GET  /test            - Test with webcam")
    print("\n" + "="*70 + "\n")
    
    # Run in production with proper WSGI server
    # For production: gunicorn -w 4 -b 0.0.0.0:5000 api.server:app
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
