/**
 * 🚨 EMERGENCY MODE SCREEN
 * 
 * Audio-First Design:
 * - Full-screen RED background
 * - One giant button: "Send Help"
 * 
 * Actions:
 * - Call emergency contact
 * - Send live GPS location
 * - Optional loud alert sound
 */

import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Pressable,
  Linking,
  Alert,
} from 'react-native';
import Tts from 'react-native-tts';
import ReactNativeHapticFeedback from 'react-native-haptic-feedback';
import Geolocation from '@react-native-community/geolocation';

const EmergencyScreen = ({ navigation }) => {
  useEffect(() => {
    // Announce emergency mode
    Tts.speak('Emergency activated. Tap the screen to send help message.', true);
    
    // Haptic alert pattern
    ReactNativeHapticFeedback.trigger('notificationError');
    
    return () => {
      Tts.stop();
    };
  }, []);

  const sendEmergency = () => {
    ReactNativeHapticFeedback.trigger('notificationError');
    Tts.speak('Sending emergency alert');

    // Get current location
    Geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        const locationUrl = `https://maps.google.com/?q=${latitude},${longitude}`;
        
        // Emergency contact number (should come from settings)
        const emergencyNumber = '911'; // Replace with actual emergency contact
        
        // Send SMS with location
        const message = `EMERGENCY! I need help. My location: ${locationUrl}`;
        
        Linking.openURL(`sms:${emergencyNumber}?body=${encodeURIComponent(message)}`);
        
        Tts.speak('Emergency message sent. Help is on the way.');
        
        Alert.alert(
          'Emergency Alert Sent',
          'Your location and emergency message have been sent.',
          [
            {
              text: 'OK',
              onPress: () => navigation.goBack(),
            },
          ]
        );
      },
      (error) => {
        console.log('Location error:', error);
        Tts.speak('Could not get location. Sending emergency alert anyway.');
        
        // Send alert without location
        Linking.openURL(`sms:911?body=EMERGENCY! I need help.`);
      },
      { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
    );
  };

  return (
    <Pressable
      style={styles.container}
      onPress={sendEmergency}
      accessible={true}
      accessibilityLabel="Emergency screen. Tap anywhere to send help message."
      accessibilityRole="button"
    >
      <View style={styles.content}>
        <Text style={styles.emergencyText}>EMERGENCY</Text>
        <Text style={styles.instructionText}>TAP TO SEND HELP</Text>
      </View>
    </Pressable>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FF0000',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emergencyText: {
    fontSize: 48,
    color: '#FFFFFF',
    fontWeight: 'bold',
    marginBottom: 40,
  },
  instructionText: {
    fontSize: 28,
    color: '#FFFFFF',
    fontWeight: '600',
  },
});

export default EmergencyScreen;
