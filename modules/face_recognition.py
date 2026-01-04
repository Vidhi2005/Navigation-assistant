"""
Face Recognition Module
Recognizes known faces from database
"""

import face_recognition
import cv2
import numpy as np
import os
import pickle
from config import FACE_DATABASE_PATH, FACE_IMAGES_PATH, FACE_RECOGNITION_TOLERANCE


class FaceRecognitionModule:
    """
    Face recognition for identifying known people
    """
    
    def __init__(self, database_path=FACE_DATABASE_PATH, images_path=FACE_IMAGES_PATH):
        """Initialize face recognition"""
        print("Initializing face recognition...")
        
        self.database_path = database_path
        self.images_path = images_path
        
        self.known_encodings = []
        self.known_names = []
        
        # Load existing database or create new
        if os.path.exists(database_path):
            self.load_database()
        else:
            print("⚠️ No face database found. Creating new...")
            self.scan_and_encode_faces()
        
        print(f"✅ Face recognition ready: {len(self.known_names)} people")
    
    def scan_and_encode_faces(self):
        """
        Scan faces directory and encode all faces
        
        Directory structure:
        data/faces/
            person1/
                photo1.jpg
                photo2.jpg
            person2/
                photo1.jpg
        """
        if not os.path.exists(self.images_path):
            os.makedirs(self.images_path)
            print(f"⚠️ Created {self.images_path}. Add face images there.")
            return
        
        encodings = []
        names = []
        
        # Scan each person directory
        for person_name in os.listdir(self.images_path):
            person_dir = os.path.join(self.images_path, person_name)
            
            if not os.path.isdir(person_dir):
                continue
            
            print(f"Encoding faces for: {person_name}")
            
            # Encode each photo
            for filename in os.listdir(person_dir):
                if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    continue
                
                image_path = os.path.join(person_dir, filename)
                
                try:
                    # Load image
                    image = face_recognition.load_image_file(image_path)
                    
                    # Find faces
                    face_encodings = face_recognition.face_encodings(image)
                    
                    if len(face_encodings) > 0:
                        # Use first face found
                        encoding = face_encodings[0]
                        encodings.append(encoding)
                        names.append(person_name)
                        print(f"  ✅ Encoded: {filename}")
                    else:
                        print(f"  ⚠️ No face found in: {filename}")
                
                except Exception as e:
                    print(f"  ❌ Error encoding {filename}: {e}")
        
        self.known_encodings = encodings
        self.known_names = names
        
        # Save database
        self.save_database()
        
        print(f"✅ Encoded {len(encodings)} faces for {len(set(names))} people")
    
    def save_database(self):
        """Save encodings to disk"""
        os.makedirs(os.path.dirname(self.database_path), exist_ok=True)
        
        data = {
            'encodings': self.known_encodings,
            'names': self.known_names
        }
        
        with open(self.database_path, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"💾 Database saved to {self.database_path}")
    
    def load_database(self):
        """Load encodings from disk"""
        try:
            with open(self.database_path, 'rb') as f:
                data = pickle.load(f)
            
            self.known_encodings = data['encodings']
            self.known_names = data['names']
            
            print(f"✅ Loaded database: {len(self.known_names)} faces")
        
        except Exception as e:
            print(f"❌ Error loading database: {e}")
            self.known_encodings = []
            self.known_names = []
    
    def recognize_faces(self, frame):
        """
        Recognize faces in a frame
        
        Args:
            frame: OpenCV image (BGR)
        
        Returns:
            List of face detections: [{
                'name': 'John',
                'confidence': 0.85,
                'bbox': [x, y, w, h],
                'location': (top, right, bottom, left)
            }]
        """
        if len(self.known_encodings) == 0:
            return []
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Find all faces
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        faces = []
        
        for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
            # Compare with known faces
            matches = face_recognition.compare_faces(
                self.known_encodings,
                encoding,
                tolerance=FACE_RECOGNITION_TOLERANCE
            )
            
            name = "Unknown"
            confidence = 0.0
            
            # Calculate distances to all known faces
            face_distances = face_recognition.face_distance(
                self.known_encodings,
                encoding
            )
            
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index]:
                    name = self.known_names[best_match_index]
                    # Convert distance to confidence (0-1)
                    confidence = 1.0 - face_distances[best_match_index]
            
            # Calculate bounding box
            width = right - left
            height = bottom - top
            
            face = {
                'name': name,
                'confidence': confidence,
                'bbox': [left, top, width, height],
                'location': (top, right, bottom, left)
            }
            
            faces.append(face)
        
        return faces
    
    def draw_faces(self, frame, faces):
        """
        Draw face bounding boxes and names
        
        Args:
            frame: OpenCV image
            faces: List of face detections
        
        Returns:
            Annotated frame
        """
        annotated = frame.copy()
        
        for face in faces:
            top, right, bottom, left = face['location']
            name = face['name']
            confidence = face['confidence']
            
            # Choose color based on recognition
            if name == "Unknown":
                color = (0, 0, 255)  # Red for unknown
            else:
                color = (0, 255, 0)  # Green for known
            
            # Draw rectangle
            cv2.rectangle(annotated, (left, top), (right, bottom), color, 2)
            
            # Draw label background
            label = f"{name} ({confidence:.2f})"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            
            cv2.rectangle(
                annotated,
                (left, bottom - label_size[1] - 10),
                (left + label_size[0], bottom),
                color,
                -1
            )
            
            # Draw label text
            cv2.putText(
                annotated,
                label,
                (left, bottom - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
        
        return annotated
    
    def add_person(self, name, image):
        """
        Add a new person to the database
        
        Args:
            name: Person's name
            image: OpenCV image (BGR) or path to image
        """
        # Load image if path provided
        if isinstance(image, str):
            image = face_recognition.load_image_file(image)
        else:
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Encode face
        face_encodings = face_recognition.face_encodings(image)
        
        if len(face_encodings) == 0:
            raise ValueError("No face found in image")
        
        # Add to database
        self.known_encodings.append(face_encodings[0])
        self.known_names.append(name)
        
        # Save updated database
        self.save_database()
        
        print(f"✅ Added {name} to database")
    
    def remove_person(self, name):
        """Remove a person from the database"""
        indices_to_remove = [i for i, n in enumerate(self.known_names) if n == name]
        
        if not indices_to_remove:
            print(f"⚠️ {name} not found in database")
            return
        
        # Remove in reverse order to maintain indices
        for i in reversed(indices_to_remove):
            del self.known_encodings[i]
            del self.known_names[i]
        
        self.save_database()
        
        print(f"✅ Removed {name} from database ({len(indices_to_remove)} faces)")
    
    def list_people(self):
        """List all people in database"""
        unique_names = list(set(self.known_names))
        return unique_names


# Test module
if __name__ == "__main__":
    print("Testing Face Recognition Module...")
    
    fr = FaceRecognitionModule()
    
    print(f"\nPeople in database: {fr.list_people()}")
    
    # Test with webcam
    print("\nPress 'q' to quit")
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Recognize faces (every frame - reduce for performance)
        faces = fr.recognize_faces(frame)
        
        # Draw faces
        annotated = fr.draw_faces(frame, faces)
        
        # Show
        cv2.imshow('Face Recognition Test', annotated)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("Test complete!")
