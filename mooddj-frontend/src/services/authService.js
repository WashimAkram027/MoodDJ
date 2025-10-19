import api from './api';

export const authService = {
  // Get Spotify user profile
  getSpotifyProfile: async () => {
    return api.get('/api/auth/spotify');
  },

  // Get user profile
  getUserProfile: async (userId) => {
    return api.get('/api/auth/profile', {
      params: { user_id: userId },
    });
  },
};