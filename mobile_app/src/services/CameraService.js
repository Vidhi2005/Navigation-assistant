/**
 * Camera Service
 * Captures frames for object detection
 * Uses react-native-vision-camera
 */

import {Camera} from 'react-native-vision-camera';

class CameraService {
  constructor() {
    this.camera = null;
    this.device = null;
    this.isActive = false;
  }

  async initialize() {
    try {
      // Request camera permission
      const permission = await Camera.requestCameraPermission();

      if (permission === 'denied') {
        throw new Error('Camera permission denied');
      }

      // Get back camera device
      const devices = await Camera.getAvailableCameraDevices();
      this.device = devices.find(d => d.position === 'back');

      if (!this.device) {
        throw new Error('No back camera found');
      }

      this.isActive = true;
      console.log('✅ Camera initialized');
    } catch (error) {
      console.error('Camera initialization error:', error);
      throw error;
    }
  }

  setCamera(cameraRef) {
    this.camera = cameraRef;
  }

  async captureFrame() {
    if (!this.camera || !this.isActive) {
      console.warn('Camera not ready');
      return null;
    }

    try {
      // Take photo
      const photo = await this.camera.takePhoto({
        flash: 'off',
        qualityPrioritization: 'speed',
        enableShutterSound: false,
      });

      // Convert to base64
      const base64 = await this.photoToBase64(photo.path);

      return base64;
    } catch (error) {
      console.error('Frame capture error:', error);
      return null;
    }
  }

  async photoToBase64(photoPath) {
    // This is a placeholder - implement actual conversion
    // You'll need react-native-fs or similar
    try {
      const RNFS = require('react-native-fs');
      const base64 = await RNFS.readFile(photoPath, 'base64');
      return `data:image/jpeg;base64,${base64}`;
    } catch (error) {
      console.error('Base64 conversion error:', error);
      // Fallback: return path (API will need to handle)
      return photoPath;
    }
  }

  stop() {
    this.isActive = false;
    this.camera = null;
  }

  // Alternative: Use snapshot instead of photo
  async captureSnapshot() {
    if (!this.camera || !this.isActive) {
      return null;
    }

    try {
      const snapshot = await this.camera.takeSnapshot({
        quality: 70,
        skipMetadata: true,
      });

      const base64 = await this.photoToBase64(snapshot.path);
      return base64;
    } catch (error) {
      console.error('Snapshot capture error:', error);
      return null;
    }
  }
}

const cameraService = new CameraService();
export default cameraService;
