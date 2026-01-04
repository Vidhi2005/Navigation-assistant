/**
 * PRODUCTION NAVIGATION ASSISTANT
 * Real-time camera → backend → TTS → haptics
 *
 * MUST WORK: Camera capture → WebSocket → Speech → Vibration
 */

import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Pressable,
  AppState,
  PermissionsAndroid,
  Platform,
  Alert,
} from 'react-native';
import { Camera, useCameraDevice } from 'react-native-vision-camera';
import Tts from 'react-native-tts';
import ReactNativeHapticFeedback from 'react-native-haptic-feedback';

// CHANGE THIS TO YOUR BACKEND IP
const BACKEND_URL = 'ws://172.24.192.1:8765/ws/navigate';

const NavigationScreen = ({ navigation }) => {
  const [isNavigating, setIsNavigating] = useState(false);
  const [lastInstruction, setLastInstruction] = useState('Navigation started');
  const [ws, setWs] = useState(null);
  const [cameraPermission, setCameraPermission] = useState(false);

  const device = useCameraDevice('back');
  const tapCountRef = React.useRef(0);
  const tapTimerRef = React.useRef(null);
  const frameIntervalRef = React.useRef(null);
  const cameraRef = React.useRef(null);

  useEffect(() => {
    requestCameraPermission();
    setupTTS();
    connectWebSocket();

    return () => {
      cleanup();
    };
  }, []);

  const requestCameraPermission = async () => {
    try {
      if (Platform.OS === 'android') {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.CAMERA,
        );
        setCameraPermission(granted === PermissionsAndroid.RESULTS.GRANTED);
      } else {
        const permission = await Camera.requestCameraPermission();
        setCameraPermission(permission === 'granted');
      }
    } catch (err) {
      console.error('Camera permission error:', err);
    }
  };

  const setupTTS = () => {
    Tts.setDefaultRate(0.5);
    Tts.setDefaultLanguage('en-US');
  };

  const connectWebSocket = () => {
    try {
      const websocket = new WebSocket(BACKEND_URL);

      websocket.onopen = () => {
        console.log('✅ Connected to backend');
        Tts.speak('Backend connected');
      };

      websocket.onmessage = event => {
        const message = JSON.parse(event.data);

        if (message.type === 'navigation') {
          handleNavigationData(message.data);
        }
      };

      websocket.onerror = error => {
        console.error('❌ WebSocket error:', error);
        Tts.speak('Connection error');
      };

      websocket.onclose = () => {
        console.log('WebSocket closed, reconnecting...');
        setTimeout(connectWebSocket, 3000);
      };

      setWs(websocket);
    } catch (error) {
      console.error('WebSocket connection failed:', error);
    }
  };

  const handleNavigationData = data => {
    const { object, distance, direction, severity } = data;

    if (object === 'clear') {
      // Path is clear, no announcement
      return;
    }

    // Build spoken instruction
    let instruction = '';

    if (direction === 'center') {
      instruction = `${object} ahead, ${distance} meters`;
    } else {
      instruction = `${object} on the ${direction}, ${distance} meters`;
    }

    setLastInstruction(instruction);

    // Speak instruction
    Tts.speak(instruction);

    // Haptic feedback based on severity
    if (severity === 'high') {
      ReactNativeHapticFeedback.trigger('notificationError');
    } else if (severity === 'medium') {
      ReactNativeHapticFeedback.trigger('notificationWarning');
    } else {
      ReactNativeHapticFeedback.trigger('impactLight');
    }
  };

  const startNavigation = async () => {
    if (!cameraPermission) {
      Alert.alert('Camera permission required');
      return;
    }

    setIsNavigating(true);
    Tts.speak('Navigation started');

    // Start sending frames to backend
    frameIntervalRef.current = setInterval(captureAndSendFrame, 500); // 2 FPS
  };

  const stopNavigation = () => {
    setIsNavigating(false);
    Tts.speak('Navigation paused');

    if (frameIntervalRef.current) {
      clearInterval(frameIntervalRef.current);
    }
  };

  const captureAndSendFrame = async () => {
    if (!cameraRef.current || !ws || ws.readyState !== WebSocket.OPEN) {
      return;
    }

    try {
      // Capture photo
      const photo = await cameraRef.current.takePhoto({
        qualityPrioritization: 'speed',
        skipMetadata: true,
      });

      // Read file and convert to base64
      const fileUri =
        Platform.OS === 'ios' ? photo.path : `file://${photo.path}`;

      // Send to backend via WebSocket
      ws.send(
        JSON.stringify({
          type: 'frame',
          frame: fileUri, // Backend will decode
        }),
      );
    } catch (error) {
      console.error('Frame capture error:', error);
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
        // Single tap → Repeat
        Tts.speak(lastInstruction);
      } else if (taps === 2) {
        // Double tap → Pause/Resume
        if (isNavigating) {
          stopNavigation();
        } else {
          startNavigation();
        }
      }
    }, 300);
  };

  const handleLongPress = () => {
    // Emergency
    ReactNativeHapticFeedback.trigger('notificationError');
    Tts.speak('Emergency mode');
    navigation.navigate('Emergency');
  };

  const cleanup = () => {
    if (frameIntervalRef.current) clearInterval(frameIntervalRef.current);
    if (tapTimerRef.current) clearTimeout(tapTimerRef.current);
    if (ws) ws.close();
    Tts.stop();
  };

  // Check if camera is available
  if (!device || !cameraPermission) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Camera not available</Text>
        <Text style={styles.errorText}>Check permissions</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Camera (running in background) */}
      <Camera
        ref={cameraRef}
        style={StyleSheet.absoluteFill}
        device={device}
        isActive={isNavigating}
        photo={true}
      />

      {/* Overlay */}
      <Pressable
        style={styles.overlay}
        onPress={handleTap}
        onLongPress={handleLongPress}
        accessible={true}
        accessibilityLabel={`Navigation screen. ${
          isNavigating ? 'Running' : 'Paused'
        }. Single tap to repeat. Double tap to ${
          isNavigating ? 'pause' : 'resume'
        }. Long press for emergency.`}
      >
        <Text style={styles.statusText}>
          {isNavigating
            ? 'Navigation Running'
            : 'Paused - Double tap to resume'}
        </Text>
      </Pressable>

      {/* Emergency Button */}
      <Pressable
        style={styles.emergencyButton}
        onPress={() => {
          ReactNativeHapticFeedback.trigger('notificationError');
          Tts.speak('Emergency');
          navigation.navigate('Emergency');
        }}
        accessible={true}
        accessibilityLabel="Emergency button"
      >
        <Text style={styles.emergencyText}>EMERGENCY</Text>
      </Pressable>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  overlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.7)',
  },
  statusText: {
    fontSize: 24,
    color: '#fff',
    textAlign: 'center',
    fontWeight: '500',
    padding: 20,
  },
  emergencyButton: {
    backgroundColor: '#ff0000',
    height: 120,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
  },
  emergencyText: {
    fontSize: 32,
    color: '#fff',
    fontWeight: 'bold',
  },
  errorText: {
    fontSize: 20,
    color: '#fff',
    textAlign: 'center',
    margin: 20,
  },
});

export default NavigationScreen;
