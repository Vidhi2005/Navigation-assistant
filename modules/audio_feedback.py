"""
Audio Feedback Module
Converts visual information to speech for visually impaired users
"""

import pyttsx3
import time
from threading import Thread, Lock
from config import *

class AudioFeedback:
    def __init__(self):
        """Initialize text-to-speech engine"""
        print("Initializing text-to-speech...")
        
        try:
            self.engine = pyttsx3.init()
            
            # Configure voice
            self.engine.setProperty('rate', TTS_RATE)
            self.engine.setProperty('volume', TTS_VOLUME)
            
            # Get available voices
            voices = self.engine.getProperty('voices')
            if voices:
                # Use first available voice (usually default)
                self.engine.setProperty('voice', voices[0].id)
            
            print("✅ Audio system ready")
            
        except Exception as e:
            print(f"❌ Error initializing TTS: {e}")
            raise
        
        # Alert cooldown tracking
        self.last_alert_time = {}
        self.alert_lock = Lock()
        
        # Speaking queue
        self.is_speaking = False
    
    def speak(self, text, priority=False):
        """
        Convert text to speech
        
        Args:
            text: String to speak
            priority: If True, interrupt current speech
        """
        if not text:
            return
        
        if LOG_DETECTIONS:
            print(f"🔊 Speaking: {text}")
        
        if priority and self.is_speaking:
            self.engine.stop()
        
        self.is_speaking = True
        
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"❌ Speech error: {e}")
        finally:
            self.is_speaking = False
    
    def speak_async(self, text):
        """
        Speak in background thread (non-blocking)
        """
        thread = Thread(target=self.speak, args=(text,))
        thread.daemon = True
        thread.start()
    
    def generate_alert(self, detection):
        """
        Generate natural language alert from detection
        
        Args:
            detection: Detection dict with distance, position, class
        
        Returns:
            Alert message string
        """
        obj_class = detection['class']
        distance = detection['distance']
        position = detection['position']
        category = detection['category']
        
        # Create urgency prefix
        if category == 'critical':
            urgency = "Warning! "
        elif category == 'warning':
            urgency = "Caution. "
        else:
            urgency = ""
        
        # Format distance
        if distance < 1:
            dist_text = f"{distance*100:.0f} centimeters"
        else:
            dist_text = f"{distance:.1f} meters"
        
        # Position text
        position_text = {
            'left': 'on your left',
            'right': 'on your right',
            'center': 'ahead'
        }.get(position, 'ahead')
        
        # Generate message
        if obj_class == 'person':
            message = f"{urgency}Person {position_text}, {dist_text}"
        else:
            message = f"{urgency}{obj_class} {position_text}, {dist_text}"
        
        return message
    
    def should_alert(self, detection):
        """
        Check if enough time has passed since last alert for this object
        Prevents spam
        """
        key = f"{detection['class']}_{detection['position']}"
        current_time = time.time()
        
        with self.alert_lock:
            last_time = self.last_alert_time.get(key, 0)
            
            if current_time - last_time >= ALERT_COOLDOWN:
                self.last_alert_time[key] = current_time
                return True
        
        return False
    
    def announce_detections(self, detections):
        """
        Announce important detections
        Only announces most urgent detection to avoid information overload
        """
        if not detections:
            return
        
        # Get most urgent detection
        urgent = detections[0]  # Already sorted by urgency
        
        # Check if we should alert
        if urgent['urgency'] >= 2 and self.should_alert(urgent):
            message = self.generate_alert(urgent)
            self.speak_async(message)
    
    def announce_navigation(self, instruction):
        """
        Announce navigation instruction
        """
        self.speak(instruction, priority=True)
    
    def announce_face(self, name):
        """
        Announce recognized face
        """
        if name and name != "Unknown":
            self.speak_async(f"Hello {name}")
    
    def test_audio(self):
        """
        Test audio system
        """
        print("Testing audio system...")
        self.speak("Audio system working correctly")
        print("✅ Audio test complete")


# Test the module
if __name__ == "__main__":
    print("Testing Audio Feedback...")
    
    audio = AudioFeedback()
    
    # Test basic speech
    audio.speak("Hello, I am your navigation assistant")
    
    # Test detection alert
    test_detection = {
        'class': 'person',
        'distance': 1.5,
        'position': 'left',
        'category': 'warning',
        'urgency': 2
    }
    
    message = audio.generate_alert(test_detection)
    print(f"Generated message: {message}")
    audio.speak(message)
    
    print("✅ Audio test complete!")

    import pyttsx3

_engine = None

def speak(text):
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()

    _engine.say(text)
    _engine.runAndWait()


if __name__ == "__main__":
    speak("Audio feedback module is working")
