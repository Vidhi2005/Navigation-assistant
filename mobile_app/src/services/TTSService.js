/**
 * Text-to-Speech Service
 * Primary output method for visually impaired users
 */

import Tts from 'react-native-tts';

class TTSService {
  constructor() {
    this.initialized = false;
    this.speechRate = 0.5; // Default rate (0.0 - 1.0)
    this.lastAnnouncement = '';
    this.lastAnnouncementTime = 0;
    this.cooldownMs = 2000; // Prevent rapid repetition
  }

  async initialize() {
    if (this.initialized) return;

    try {
      // Set default language
      await Tts.setDefaultLanguage('en-US');

      // Set speech rate
      await Tts.setDefaultRate(this.speechRate);

      // Set default pitch
      await Tts.setDefaultPitch(1.0);

      // Get available voices
      const voices = await Tts.voices();
      console.log('Available voices:', voices.length);

      // Use first available voice
      if (voices.length > 0) {
        await Tts.setDefaultVoice(voices[0].id);
      }

      this.initialized = true;
      console.log('✅ TTS initialized');
    } catch (error) {
      console.error('TTS initialization error:', error);
    }
  }

  speak(text, urgent = false) {
    if (!text) return;

    // Check cooldown (unless urgent)
    if (!urgent) {
      const now = Date.now();
      if (
        text === this.lastAnnouncement &&
        now - this.lastAnnouncementTime < this.cooldownMs
      ) {
        // Skip duplicate announcement
        return;
      }
    }

    // Stop current speech if urgent
    if (urgent) {
      Tts.stop();
    }

    // Speak
    Tts.speak(text);

    // Update tracking
    this.lastAnnouncement = text;
    this.lastAnnouncementTime = Date.now();

    console.log(`🔊 TTS: ${text}`);
  }

  stop() {
    Tts.stop();
  }

  setSpeechRate(rate) {
    // Rate: 0.0 (slow) to 1.0 (fast)
    this.speechRate = Math.max(0.0, Math.min(1.0, rate));
    Tts.setDefaultRate(this.speechRate);
  }

  increaseSpeechRate() {
    this.setSpeechRate(this.speechRate + 0.1);
  }

  decreaseSpeechRate() {
    this.setSpeechRate(this.speechRate - 0.1);
  }

  isSpeaking() {
    return Tts.isSpeaking();
  }
}

// Singleton instance
const ttsService = new TTSService();
export default ttsService;
