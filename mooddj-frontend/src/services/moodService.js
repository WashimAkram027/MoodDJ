import api from './api';

export const moodService = {
  // Detect mood from image
  detectMood: async (imageData) => {
    return api.post('/api/mood/detect', { image: imageData });
  },

  // Log mood detection
  logMood: async (mood, confidence, userId = 1) => {
    return api.post('/api/mood/log', {
      user_id: userId,
      mood,
      confidence,
    });
  },

  // Get mood history
  getMoodHistory: async (userId = 1, limit = 10) => {
    return api.get('/api/mood/history', {
      params: { user_id: userId, limit },
    });
  },

  // Get mood statistics
  getMoodStats: async (userId = 1) => {
    return api.get('/api/mood/stats', {
      params: { user_id: userId },
    });
  },

  // Reset mood detector
  resetDetector: async () => {
    return api.post('/api/mood/reset');
  },
};