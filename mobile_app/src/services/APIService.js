/**
 * API Service
 * Handles communication with Python backend
 */

import axios from 'axios';

class APIService {
  constructor() {
    // Default API URL - should be configurable in settings
    this.baseURL = 'http://192.168.1.100:5000';
    this.timeout = 5000; // 5 seconds
  }

  setBaseURL(url) {
    this.baseURL = url;
  }

  async detectObjects(imageBase64) {
    try {
      const response = await axios.post(
        `${this.baseURL}/detect/stream`,
        {
          image: imageBase64,
        },
        {
          timeout: this.timeout,
          headers: {
            'Content-Type': 'application/json',
          },
        },
      );

      return response.data;
    } catch (error) {
      console.error('Detection API error:', error.message);
      return null;
    }
  }

  async detectObjectsFull(imageBase64, includeFaces = false) {
    try {
      const response = await axios.post(
        `${this.baseURL}/detect`,
        {
          image: imageBase64,
          include_faces: includeFaces,
        },
        {
          timeout: this.timeout * 2, // Longer timeout for full detection
          headers: {
            'Content-Type': 'application/json',
          },
        },
      );

      return response.data;
    } catch (error) {
      console.error('Full detection API error:', error.message);
      return null;
    }
  }

  async sendEmergency(data) {
    try {
      const response = await axios.post(
        `${this.baseURL}/emergency`,
        data,
        {
          timeout: this.timeout,
          headers: {
            'Content-Type': 'application/json',
          },
        },
      );

      return response.data;
    } catch (error) {
      console.error('Emergency API error:', error.message);
      throw error;
    }
  }

  async getSettings() {
    try {
      const response = await axios.get(`${this.baseURL}/settings`, {
        timeout: this.timeout,
      });

      return response.data;
    } catch (error) {
      console.error('Settings API error:', error.message);
      return null;
    }
  }

  async updateSettings(settings) {
    try {
      const response = await axios.post(
        `${this.baseURL}/settings`,
        settings,
        {
          timeout: this.timeout,
          headers: {
            'Content-Type': 'application/json',
          },
        },
      );

      return response.data;
    } catch (error) {
      console.error('Update settings API error:', error.message);
      return null;
    }
  }

  async healthCheck() {
    try {
      const response = await axios.get(`${this.baseURL}/health`, {
        timeout: 2000,
      });

      return response.data.status === 'healthy';
    } catch (error) {
      return false;
    }
  }
}

const apiService = new APIService();
export default apiService;
