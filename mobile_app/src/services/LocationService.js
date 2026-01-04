/**
 * Location Service
 * Gets GPS coordinates for emergency situations
 */

import {Platform, PermissionsAndroid} from 'react-native';
import Geolocation from '@react-native-community/geolocation';

class LocationService {
  constructor() {
    this.watchId = null;
  }

  async requestPermission() {
    if (Platform.OS === 'android') {
      try {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
          {
            title: 'Location Permission',
            message: 'Navigation Assistant needs access to your location for emergency services.',
            buttonNeutral: 'Ask Me Later',
            buttonNegative: 'Cancel',
            buttonPositive: 'OK',
          },
        );

        return granted === PermissionsAndroid.RESULTS.GRANTED;
      } catch (err) {
        console.warn(err);
        return false;
      }
    }

    // iOS permission is handled via Info.plist
    return true;
  }

  async getCurrentLocation() {
    const hasPermission = await this.requestPermission();

    if (!hasPermission) {
      throw new Error('Location permission denied');
    }

    return new Promise((resolve, reject) => {
      Geolocation.getCurrentPosition(
        position => {
          const {latitude, longitude, accuracy} = position.coords;
          resolve({
            latitude,
            longitude,
            accuracy,
            timestamp: position.timestamp,
          });
        },
        error => {
          console.error('Location error:', error);
          reject(error);
        },
        {
          enableHighAccuracy: true,
          timeout: 15000,
          maximumAge: 10000,
        },
      );
    });
  }

  watchLocation(callback, errorCallback) {
    this.watchId = Geolocation.watchPosition(
      position => {
        const {latitude, longitude, accuracy} = position.coords;
        callback({
          latitude,
          longitude,
          accuracy,
          timestamp: position.timestamp,
        });
      },
      error => {
        console.error('Location watch error:', error);
        if (errorCallback) errorCallback(error);
      },
      {
        enableHighAccuracy: true,
        distanceFilter: 10, // Update every 10 meters
        interval: 5000, // Update every 5 seconds
      },
    );
  }

  clearWatch() {
    if (this.watchId) {
      Geolocation.clearWatch(this.watchId);
      this.watchId = null;
    }
  }
}

const locationService = new LocationService();
export default locationService;
