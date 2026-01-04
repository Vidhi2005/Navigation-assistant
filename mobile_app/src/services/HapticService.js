/**
 * Haptic Feedback Service
 * Provides vibration patterns for different situations
 */

import ReactNativeHapticFeedback from 'react-native-haptic-feedback';

const options = {
  enableVibrateFallback: true,
  ignoreAndroidSystemSettings: false,
};

class HapticService {
  light() {
    // Light tap - for UI feedback
    ReactNativeHapticFeedback.trigger('impactLight', options);
  }

  medium() {
    // Medium impact - for warnings
    ReactNativeHapticFeedback.trigger('impactMedium', options);
  }

  strong() {
    // Strong impact - for critical alerts
    ReactNativeHapticFeedback.trigger('impactHeavy', options);
  }

  success() {
    // Success pattern
    ReactNativeHapticFeedback.trigger('notificationSuccess', options);
  }

  warning() {
    // Warning pattern
    ReactNativeHapticFeedback.trigger('notificationWarning', options);
  }

  error() {
    // Error pattern
    ReactNativeHapticFeedback.trigger('notificationError', options);
  }

  // Distance-based feedback
  distanceFeedback(distance) {
    // distance in meters
    if (distance < 0.5) {
      // Very close - continuous strong
      this.strong();
      setTimeout(() => this.strong(), 200);
      setTimeout(() => this.strong(), 400);
    } else if (distance < 1.0) {
      // Critical - double tap
      this.strong();
      setTimeout(() => this.strong(), 200);
    } else if (distance < 2.0) {
      // Warning - single medium
      this.medium();
    } else if (distance < 3.0) {
      // Caution - single light
      this.light();
    }
    // No haptic for distances > 3m
  }

  // Direction-based feedback
  directionFeedback(direction) {
    // direction: 'left', 'right', 'center'
    if (direction === 'left') {
      // Short-long pattern for left
      this.light();
      setTimeout(() => this.medium(), 200);
    } else if (direction === 'right') {
      // Long-short pattern for right
      this.medium();
      setTimeout(() => this.light(), 200);
    } else if (direction === 'center') {
      // Double tap for center
      this.medium();
      setTimeout(() => this.medium(), 100);
    }
  }
}

const hapticService = new HapticService();
export default hapticService;
