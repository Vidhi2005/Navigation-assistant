/**
 * 🟢 HOME / READY SCREEN
 * 
 * Audio-First Design:
 * - Full-screen pressable area
 * - Black background, minimal text
 * - Gesture-driven (no buttons)
 * 
 * Gestures:
 * - Double tap → Start navigation
 * - Triple tap → Settings
 */

import React, { useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Pressable,
} from 'react-native';
import Tts from 'react-native-tts';
import ReactNativeHapticFeedback from 'react-native-haptic-feedback';

const HomeScreen = ({ navigation }) => {
  const tapCountRef = useRef(0);
  const tapTimerRef = useRef(null);

  useEffect(() => {
    // Announce on app open
    Tts.speak('Navigation ready. Double tap to start.');

    return () => {
      Tts.stop();
      if (tapTimerRef.current) clearTimeout(tapTimerRef.current);
    };
  }, []);

  const handlePress = () => {
    // Haptic feedback on every tap
    ReactNativeHapticFeedback.trigger('impactLight');
    
    tapCountRef.current += 1;

    // Clear previous timer
    if (tapTimerRef.current) clearTimeout(tapTimerRef.current);

    // Wait for multi-tap detection (300ms window)
    tapTimerRef.current = setTimeout(() => {
      const taps = tapCountRef.current;
      tapCountRef.current = 0;

      if (taps === 2) {
        // Double tap → Start navigation
        ReactNativeHapticFeedback.trigger('impactMedium');
        Tts.speak('Starting navigation');
        navigation.navigate('Navigation');
      } else if (taps === 3) {
        // Triple tap → Settings
        ReactNativeHapticFeedback.trigger('impactHeavy');
        Tts.speak('Opening settings');
        navigation.navigate('Settings');
      }
    }, 300);
  };

  return (
    <Pressable
      style={styles.container}
      onPress={handlePress}
      accessible={true}
      accessibilityLabel="Home screen. Double tap to start navigation. Triple tap for settings."
      accessibilityRole="button"
    >
      <View style={styles.content}>
        <Text style={styles.centerText}>Double tap to start navigation</Text>
      </View>
    </Pressable>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  centerText: {
    fontSize: 28,
    color: '#FFFFFF',
    textAlign: 'center',
    fontWeight: '600',
  },
});

export default HomeScreen;
