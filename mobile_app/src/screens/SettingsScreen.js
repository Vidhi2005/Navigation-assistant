/**
 * ⚙️ SETTINGS SCREEN (Hidden / Caregiver Only)
 * 
 * Access:
 * - Triple tap on Home
 * 
 * Options:
 * - Detection distance (meters)
 * - Object types (person, vehicle, stairs)
 * - Language
 * - Voice speed
 * - Emergency contact
 * 
 * ⚠️ This screen is not for blind usage during navigation
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  Pressable,
} from 'react-native';
import Tts from 'react-native-tts';
import ReactNativeHapticFeedback from 'react-native-haptic-feedback';

const SettingsScreen = ({ navigation }) => {
  const [detectionDistance, setDetectionDistance] = useState('5');
  const [emergencyContact, setEmergencyContact] = useState('');
  const [voiceSpeed, setVoiceSpeed] = useState('0.5');

  const saveSetting = (settingName) => {
    ReactNativeHapticFeedback.trigger('impactMedium');
    Tts.speak(`${settingName} saved`);
  };

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <Text style={styles.title}>Settings</Text>
        
        {/* Detection Distance */}
        <View style={styles.settingGroup}>
          <Text style={styles.label}>Detection Distance (meters)</Text>
          <TextInput
            style={styles.input}
            value={detectionDistance}
            onChangeText={setDetectionDistance}
            keyboardType="numeric"
            placeholder="5"
            placeholderTextColor="#666"
            accessible={true}
            accessibilityLabel="Detection distance in meters"
          />
        </View>

        {/* Voice Speed */}
        <View style={styles.settingGroup}>
          <Text style={styles.label}>Voice Speed (0.3 - 1.0)</Text>
          <TextInput
            style={styles.input}
            value={voiceSpeed}
            onChangeText={setVoiceSpeed}
            keyboardType="numeric"
            placeholder="0.5"
            placeholderTextColor="#666"
            accessible={true}
            accessibilityLabel="Voice speed"
          />
        </View>

        {/* Emergency Contact */}
        <View style={styles.settingGroup}>
          <Text style={styles.label}>Emergency Contact Number</Text>
          <TextInput
            style={styles.input}
            value={emergencyContact}
            onChangeText={setEmergencyContact}
            keyboardType="phone-pad"
            placeholder="Emergency contact"
            placeholderTextColor="#666"
            accessible={true}
            accessibilityLabel="Emergency contact number"
          />
        </View>

        {/* Object Types */}
        <View style={styles.settingGroup}>
          <Text style={styles.label}>Detect Objects:</Text>
          <Text style={styles.infoText}>• Person</Text>
          <Text style={styles.infoText}>• Vehicle</Text>
          <Text style={styles.infoText}>• Stairs</Text>
          <Text style={styles.infoText}>• Obstacles</Text>
        </View>

        {/* Save Button */}
        <Pressable
          style={styles.saveButton}
          onPress={() => {
            saveSetting('All settings');
            setTimeout(() => navigation.goBack(), 1000);
          }}
          accessible={true}
          accessibilityLabel="Save settings and return"
          accessibilityRole="button"
        >
          <Text style={styles.saveButtonText}>SAVE</Text>
        </Pressable>

        {/* Back Button */}
        <Pressable
          style={styles.backButton}
          onPress={() => {
            Tts.speak('Returning to home');
            navigation.goBack();
          }}
          accessible={true}
          accessibilityLabel="Return to home screen"
          accessibilityRole="button"
        >
          <Text style={styles.backButtonText}>BACK</Text>
        </Pressable>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  scrollView: {
    flex: 1,
    padding: 20,
  },
  title: {
    fontSize: 32,
    color: '#FFFFFF',
    fontWeight: 'bold',
    marginBottom: 30,
    marginTop: 20,
  },
  settingGroup: {
    marginBottom: 30,
  },
  label: {
    fontSize: 18,
    color: '#FFFFFF',
    fontWeight: '600',
    marginBottom: 10,
  },
  input: {
    backgroundColor: '#2a2a2a',
    color: '#FFFFFF',
    fontSize: 20,
    padding: 15,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#444',
  },
  infoText: {
    fontSize: 16,
    color: '#CCCCCC',
    marginLeft: 10,
    marginVertical: 5,
  },
  saveButton: {
    backgroundColor: '#4CAF50',
    padding: 20,
    borderRadius: 8,
    marginTop: 20,
    alignItems: 'center',
  },
  saveButtonText: {
    fontSize: 24,
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
  backButton: {
    backgroundColor: '#666',
    padding: 15,
    borderRadius: 8,
    marginTop: 15,
    marginBottom: 40,
    alignItems: 'center',
  },
  backButtonText: {
    fontSize: 20,
    color: '#FFFFFF',
    fontWeight: '600',
  },
});

export default SettingsScreen;
