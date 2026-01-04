"""
Real-Time Navigation Backend with WebSocket
Processes camera frames and sends live navigation instructions
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import base64
import json
import asyncio
from datetime import datetime
from typing import Dict, List
import uvicorn

# Import detection modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.object_detector import ObjectDetector
from modules.distance_estimator import DistanceEstimator

app = FastAPI(title="Navigation Assistant Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize detection modules
detector = ObjectDetector()
distance_estimator = DistanceEstimator()

print("✅ Real-Time Navigation Backend Ready")
print("📡 WebSocket endpoint: ws://localhost:8765/ws/navigate")


def decode_base64_image(base64_string: str) -> np.ndarray:
    """Decode base64 image to OpenCV format"""
    try:
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        img_data = base64.b64decode(base64_string)
        nparr = np.frombuffer(img_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    except Exception as e:
        print(f"❌ Image decode error: {e}")
        return None


def get_direction(x_center: float, frame_width: int) -> str:
    """Determine object direction: left, center, right"""
    third = frame_width / 3
    
    if x_center < third:
        return "left"
    elif x_center > 2 * third:
        return "right"
    else:
        return "center"


def determine_severity(distance: float, category: str) -> str:
    """Determine danger level"""
    if distance < 1.0 or category == "critical":
        return "high"
    elif distance < 2.0 or category == "warning":
        return "medium"
    else:
        return "low"


def generate_navigation_instruction(detections: List[Dict], frame_width: int) -> Dict:
    """
    Convert detections into navigation instruction
    Returns most urgent obstacle with guidance
    """
    if not detections:
        return None
    
    # Sort by distance (closest first)
    detections.sort(key=lambda x: x['distance'])
    
    # Get closest obstacle
    closest = detections[0]
    
    # Calculate direction
    x_center = (closest['bbox'][0] + closest['bbox'][2]) / 2
    direction = get_direction(x_center, frame_width)
    
    # Round distance
    distance_rounded = round(closest['distance'], 1)
    
    # Determine severity
    severity = determine_severity(closest['distance'], closest['category'])
    
    # Build navigation message
    instruction = {
        "object": closest['class'],
        "distance": distance_rounded,
        "direction": direction,
        "severity": severity,
        "timestamp": datetime.now().isoformat()
    }
    
    return instruction


@app.websocket("/ws/navigate")
async def websocket_navigate(websocket: WebSocket):
    """
    WebSocket endpoint for real-time navigation
    Receives camera frames, sends navigation instructions
    """
    await websocket.accept()
    print(f"📱 Client connected: {websocket.client}")
    
    try:
        while True:
            # Receive frame from mobile app
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get('type') == 'frame':
                # Decode image
                frame_base64 = message.get('frame')
                frame = decode_base64_image(frame_base64)
                
                if frame is not None:
                    frame_height, frame_width = frame.shape[:2]
                    
                    # Detect objects
                    detections = detector.detect_objects(frame)
                    
                    # Estimate distances
                    detections = distance_estimator.process_detections(
                        detections, 
                        frame_width
                    )
                    
                    # Filter priority objects
                    priority = detector.filter_priority_objects(detections)
                    
                    # Generate navigation instruction
                    instruction = generate_navigation_instruction(
                        priority, 
                        frame_width
                    )
                    
                    if instruction:
                        # Send navigation instruction to app
                        await websocket.send_json({
                            "type": "navigation",
                            "data": instruction
                        })
                    else:
                        # No obstacles
                        await websocket.send_json({
                            "type": "navigation",
                            "data": {
                                "object": "clear",
                                "severity": "low"
                            }
                        })
            
            elif message.get('type') == 'emergency':
                # Log emergency
                print(f"🚨 EMERGENCY: {message}")
                await websocket.send_json({
                    "type": "emergency_ack",
                    "status": "received"
                })
            
            # Small delay to prevent overwhelming
            await asyncio.sleep(0.1)
    
    except WebSocketDisconnect:
        print(f"📱 Client disconnected: {websocket.client}")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        await websocket.close()


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "service": "navigation-backend",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  🚀 REAL-TIME NAVIGATION BACKEND")
    print("="*70)
    print("\n📡 WebSocket Server: ws://0.0.0.0:8765/ws/navigate")
    print("🌐 Health Check: http://0.0.0.0:8765/health")
    print("\n⚠️  Make sure mobile app connects to: ws://YOUR_IP:8765/ws/navigate")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8765,
        log_level="info"
    )
