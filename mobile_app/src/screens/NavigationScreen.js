/**
 * 🚶 NAVIGATION ACTIVE SCREEN
 * 
 * Audio-First Design:
 * - Black background
 * - Optional status text
 * - Large emergency button (bottom)
 * 
 * Primary Output:
 * - TTS → navigation instructions
 * - Haptic feedback → distance & urgency
 * 
 * Gestures:
 * - Single tap → Repeat last instruction
 * - Double tap → Pause / Resume
 * - Swipe up → Increase speech speed
 * - Swipe down → Decrease speech speed
 * - Long press → Emergency mode
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Pressable,
  PanResponder,
} from 'react-native';
import Tts from 'react-native-tts';
import ReactNativeHapticFeedback from 'react-native-haptic-feedback';

import { detectObjects } from '../services/APIService';

const NavigationScreen = ({ navigation }) => {
  const [status, setStatus] = useState('Navigation running');
  const [isPaused, setIsPaused] = useState(false);
  const [speechRate, setSpeechRate] = useState(0.5); // Default speech rate
  const [lastInstruction, setLastInstruction] = useState('Navigation started');
  
  const tapCountRef = useRef(0);
  const tapTimerRef = useRef(null);
  const detectionIntervalRef = useRef(null);

  useEffect(() => {
    // Set initial speech rate
    Tts.setDefaultRate(speechRate);
    
    // Announce navigation start
    Tts.speak('Navigation started');
    
    // Start detection loop (every 2 seconds)
    detectionIntervalRef.current = setInterval(() => {
      if (!isPaused) {
        performDetection();
      }
    }, 2000);

    return () => {
      if (detectionIntervalRef.current) {
        clearInterval(detectionIntervalRef.current);
      }
      Tts.stop();
      if (tapTimerRef.current) clearTimeout(tapTimerRef.current);
    };
  }, [isPaused]);

  const performDetection = async () => {
    try {
      // Call backend API
      const result = await detectObjects();
      
      if (result.urgent) {
        const { object, distance, direction, category } = result.urgent;
        
        // Generate instruction
        const instruction = `${object} ahead, ${direction}, ${distance} meters`;
        setLastInstruction(instruction);
        
        // Speak instruction
        Tts.speak(instruction);
        
        // Haptic feedback based on distance
        if (category === 'critical' || distance < 1.0) {
          ReactNativeHapticFeedback.trigger('notificationError');
        } else if (category === 'warning' || distance < 2.0) {
          ReactNativeHapticFeedback.trigger('notificationWarning');
        } else {
          ReactNativeHapticFeedback.trigger('impactLight');
        }
      }
    } catch (error) {
      console.log('Detection error:', error);
    }
  };

  const handleTap = () => {
    ReactNativeHapticFeedback.trigger('impactLight');
    
    tapCountRef.current += 1;

    if (tapTimerRef.current) clearTimeout(tapTimerRef.current);

    tapTimerRef.current = setTimeout(() => {
      const taps = tapCountRef.current;
      tapCountRef.current = 0;

      if (taps === 1) {
        // Single tap → Repeat last instruction
        Tts.speak(lastInstruction);
      } else if (taps === 2) {
        // Double tap → Pause / Resume
        setIsPaused(!isPaused);
        const message = !isPaused ? 'Navigation paused' : 'Navigation resumed';
        Tts.speak(message);
        setStatus(message);
      }
    }, 300);
  };

  const handleLongPress = () => {
    // Long press → Emergency mode
    ReactNativeHapticFeedback.trigger('notificationError');
    Tts.speak('Emergency mode activated');
    navigation.navigate('Emergency');
  };

  // Swipe gesture handler
  const panResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => true,
      onPanResponderRelease: (evt, gestureState) => {
        const { dy } = gestureState;
        
        if (Math.abs(dy) > 50) {
          if (dy < 0) {
            // Swipe up → Increase speech speed
            const newRate = Math.min(speechRate + 0.1, 1.0);
            setSpeechRate(newRate);
            Tts.setDefaultRate(newRate);
            Tts.speak('Speech speed increased');
            ReactNativeHapticFeedback.trigger('impactMedium');
          } else {
            // Swipe down → Decrease speech speed
            const newRate = Math.max(speechRate - 0.1, 0.3);
            setSpeechRate(newRate);
            Tts.setDefaultRate(newRate);
            Tts.speak('Speech speed decreased');
            ReactNativeHapticFeedback.trigger('impactMedium');
          }
        }
      },
    })
  ).current;

  return (
    <View style={styles.container} {...panResponder.panHandlers}>
      <Pressable
        style={styles.mainArea}
        onPress={handleTap}
        onLongPress={handleLongPress}
        accessible={true}
        accessibilityLabel={`Navigation screen. ${status}. Single tap to repeat. Double tap to pause. Long press for emergency.`}
        accessibilityRole="button"
      >
        <Text style={styles.statusText}>{status}</Text>
      </Pressable>

      {/* Emergency Button */}
      <Pressable
        style={styles.emergencyButton}
        onPress={() => {
          ReactNativeHapticFeedback.trigger('notificationError');
          Tts.speak('Emergency mode');
          navigation.navigate('Emergency');
        }}
        accessible={true}
        accessibilityLabel="Emergency button"
        accessibilityRole="button"
      >
        <Text style={styles.emergencyText}>EMERGENCY</Text>
      </Pressable>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
  },
  mainArea: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  statusText: {
    fontSize: 24,
    color: '#FFFFFF',
    textAlign: 'center',
    fontWeight: '500',
  },
  emergencyButton: {
    backgroundColor: '#FF0000',
    height: 120,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emergencyText: {
    fontSize: 32,
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
});

export default NavigationScreen;
