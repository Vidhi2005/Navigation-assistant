"""
Haptic Feedback Module
Provides vibration feedback for distance and direction
Can work with:
- Arduino/Raspberry Pi with vibration motors
- Android phone vibration
- USB haptic devices
"""

import time
from threading import Thread
import os
import sys

# Check platform
IS_RASPBERRY_PI = os.path.exists('/sys/firmware/devicetree/base/model')
IS_ARDUINO = False  # Set True if using Arduino

# Import appropriate libraries
if IS_RASPBERRY_PI:
    try:
        import RPi.GPIO as GPIO
        HAS_GPIO = True
    except ImportError:
        HAS_GPIO = False
        print("⚠️ RPi.GPIO not available - Install with: pip install RPi.GPIO")
else:
    HAS_GPIO = False

from config import *


class HapticFeedbackModule:
    """
    Haptic feedback using vibration motors
    Provides distance and directional feedback
    """
    
    def __init__(self, motor_pins=None):
        """
        Initialize haptic feedback
        
        Args:
            motor_pins: [left_motor_pin, center_motor_pin, right_motor_pin]
                       Default: [17, 18, 27] for Raspberry Pi GPIO
        """
        print("Initializing haptic feedback...")
        
        self.enabled = False
        self.motor_pins = motor_pins or [17, 18, 27]
        
        if IS_RASPBERRY_PI and HAS_GPIO:
            self.setup_gpio()
            self.enabled = True
            print("✅ Haptic feedback ready (GPIO)")
        else:
            print("⚠️ Haptic feedback: Simulation mode (no hardware)")
            self.enabled = False
    
    def setup_gpio(self):
        """Setup GPIO pins for Raspberry Pi"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            for pin in self.motor_pins:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)
            
            print(f"✅ GPIO pins configured: {self.motor_pins}")
        
        except Exception as e:
            print(f"❌ GPIO setup failed: {e}")
            self.enabled = False
    
    def vibrate(self, motor_index, duration=0.3):
        """
        Vibrate a specific motor
        
        Args:
            motor_index: 0=left, 1=center, 2=right
            duration: Vibration duration in seconds
        """
        if not self.enabled:
            print(f"🔔 [SIM] Vibrate motor {motor_index} for {duration}s")
            return
        
        if motor_index >= len(self.motor_pins):
            return
        
        pin = self.motor_pins[motor_index]
        
        try:
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(duration)
            GPIO.output(pin, GPIO.LOW)
        except Exception as e:
            print(f"❌ Vibration error: {e}")
    
    def vibrate_pattern(self, motor_index, pattern):
        """
        Execute vibration pattern
        
        Args:
            motor_index: 0=left, 1=center, 2=right
            pattern: List of (on_duration, off_duration) tuples
                    Example: [(0.1, 0.1), (0.1, 0.1)] = two quick pulses
        """
        if not self.enabled:
            print(f"🔔 [SIM] Pattern on motor {motor_index}: {pattern}")
            return
        
        if motor_index >= len(self.motor_pins):
            return
        
        pin = self.motor_pins[motor_index]
        
        try:
            for on_time, off_time in pattern:
                GPIO.output(pin, GPIO.HIGH)
                time.sleep(on_time)
                GPIO.output(pin, GPIO.LOW)
                time.sleep(off_time)
        except Exception as e:
            print(f"❌ Pattern error: {e}")
    
    def distance_feedback(self, distance, position):
        """
        Provide haptic feedback based on distance and position
        
        Args:
            distance: Distance in meters
            position: 'left', 'center', 'right'
        
        Pattern logic:
        - Very close (< 0.5m): Continuous vibration
        - Close (< 1m): Rapid pulses (5 pulses)
        - Medium (< 2m): Medium pulses (3 pulses)
        - Far (< 3m): Slow pulses (2 pulses)
        """
        # Determine motor
        motor_map = {
            'left': 0,
            'center': 1,
            'front': 1,
            'right': 2
        }
        motor_index = motor_map.get(position, 1)
        
        # Generate pattern based on distance
        if distance < 0.5:
            # Very close: continuous vibration
            pattern = [(1.0, 0)]
        elif distance < 1.0:
            # Close: rapid pulses
            pattern = [(0.1, 0.1)] * 5
        elif distance < 2.0:
            # Medium: medium pulses
            pattern = [(0.2, 0.2)] * 3
        elif distance < 3.0:
            # Far: slow pulses
            pattern = [(0.3, 0.5)] * 2
        else:
            # Too far: single pulse
            pattern = [(0.5, 0)]
        
        # Execute pattern in background thread
        thread = Thread(target=self.vibrate_pattern, args=(motor_index, pattern))
        thread.daemon = True
        thread.start()
    
    def navigation_feedback(self, direction):
        """
        Provide haptic navigation cues
        
        Args:
            direction: 'left', 'right', 'straight', 'stop'
        """
        if direction == 'left':
            # Three pulses on left motor
            pattern = [(0.2, 0.1)] * 3
            thread = Thread(target=self.vibrate_pattern, args=(0, pattern))
        
        elif direction == 'right':
            # Three pulses on right motor
            pattern = [(0.2, 0.1)] * 3
            thread = Thread(target=self.vibrate_pattern, args=(2, pattern))
        
        elif direction == 'straight':
            # Single long pulse on center
            pattern = [(0.5, 0)]
            thread = Thread(target=self.vibrate_pattern, args=(1, pattern))
        
        elif direction == 'stop':
            # Alternating left-right pattern
            for _ in range(3):
                Thread(target=self.vibrate, args=(0, 0.1)).start()
                time.sleep(0.15)
                Thread(target=self.vibrate, args=(2, 0.1)).start()
                time.sleep(0.15)
            return
        
        else:
            return
        
        thread.daemon = True
        thread.start()
    
    def obstacle_warning(self, urgency='medium'):
        """
        Provide obstacle warning
        
        Args:
            urgency: 'low', 'medium', 'high', 'critical'
        """
        if urgency == 'critical':
            # All motors vibrate continuously
            for i in range(3):
                Thread(target=self.vibrate, args=(i, 1.0)).start()
        
        elif urgency == 'high':
            # All motors rapid pulse
            pattern = [(0.1, 0.1)] * 5
            for i in range(3):
                Thread(target=self.vibrate_pattern, args=(i, pattern)).start()
        
        elif urgency == 'medium':
            # Center motor medium pulse
            pattern = [(0.2, 0.2)] * 3
            Thread(target=self.vibrate_pattern, args=(1, pattern)).start()
        
        else:  # low
            # Center motor single pulse
            Thread(target=self.vibrate, args=(1, 0.3)).start()
    
    def test_all_motors(self):
        """Test all motors sequentially"""
        print("\nTesting haptic motors...")
        
        for i, position in enumerate(['LEFT', 'CENTER', 'RIGHT']):
            print(f"Testing {position} motor...")
            self.vibrate(i, 0.5)
            time.sleep(1)
        
        print("✅ Haptic test complete")
    
    def cleanup(self):
        """Clean up GPIO resources"""
        if self.enabled and HAS_GPIO:
            GPIO.cleanup()
            print("✅ GPIO cleaned up")


# Android vibration support (for mobile app)
class AndroidHapticFeedback:
    """
    Haptic feedback for Android devices
    Requires: pyjnius library and Android environment
    """
    
    def __init__(self):
        """Initialize Android vibrator"""
        self.enabled = False
        
        try:
            from jnius import autoclass
            
            # Get Android context and vibrator service
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Context = autoclass('android.content.Context')
            self.vibrator = PythonActivity.mActivity.getSystemService(Context.VIBRATOR_SERVICE)
            
            self.enabled = True
            print("✅ Android vibrator ready")
        
        except ImportError:
            print("⚠️ Android haptics: Not in Android environment")
        except Exception as e:
            print(f"⚠️ Android haptics failed: {e}")
    
    def vibrate(self, duration_ms=300):
        """
        Vibrate for specified duration
        
        Args:
            duration_ms: Duration in milliseconds
        """
        if not self.enabled:
            return
        
        try:
            self.vibrator.vibrate(duration_ms)
        except Exception as e:
            print(f"❌ Vibration error: {e}")
    
    def vibrate_pattern(self, pattern):
        """
        Vibrate with pattern
        
        Args:
            pattern: List of [wait, vibrate, wait, vibrate, ...]
                    in milliseconds
        """
        if not self.enabled:
            return
        
        try:
            from jnius import autoclass
            
            # Convert to Java long array
            pattern_array = autoclass('java.util.Arrays').copyOf(
                pattern, len(pattern)
            )
            
            self.vibrator.vibrate(pattern_array, -1)
        except Exception as e:
            print(f"❌ Pattern error: {e}")


# Test the module
if __name__ == "__main__":
    print("="*60)
    print("HAPTIC FEEDBACK TEST")
    print("="*60)
    print()
    
    haptic = HapticFeedbackModule()
    
    if not haptic.enabled:
        print("Running in SIMULATION mode (no hardware)")
        print()
    
    # Test all motors
    haptic.test_all_motors()
    
    # Test distance feedback
    print("\nTesting distance feedback...")
    test_cases = [
        (0.3, 'left', 'Very close left'),
        (0.8, 'center', 'Close center'),
        (1.5, 'right', 'Medium right'),
        (2.5, 'center', 'Far center')
    ]
    
    for distance, position, description in test_cases:
        print(f"  {description}: {distance}m {position}")
        haptic.distance_feedback(distance, position)
        time.sleep(2)
    
    # Test navigation feedback
    print("\nTesting navigation feedback...")
    for direction in ['left', 'right', 'straight', 'stop']:
        print(f"  Direction: {direction}")
        haptic.navigation_feedback(direction)
        time.sleep(2)
    
    # Test obstacle warnings
    print("\nTesting obstacle warnings...")
    for urgency in ['low', 'medium', 'high', 'critical']:
        print(f"  Urgency: {urgency}")
        haptic.obstacle_warning(urgency)
        time.sleep(2)
    
    haptic.cleanup()
    print("\n✅ All tests complete!")