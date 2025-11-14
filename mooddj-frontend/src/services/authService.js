import api from './api';

export const authService = {
  // ============================================================================
  // OAuth Flow Methods
  // ============================================================================

  /**
   * Initiate Spotify OAuth login
   * Gets authorization URL and redirects user to Spotify login
   */
  initiateSpotifyLogin: async () => {
    try {
      // Note: api.js interceptor already returns response.data
      const data = await api.get('/api/auth/login');
      if (data.success && data.auth_url) {
        // Redirect to Spotify authorization page
        window.location.href = data.auth_url;
      } else {
        throw new Error('Failed to get authorization URL');
      }
    } catch (error) {
      console.error('Error initiating Spotify login:', error);
      throw error;
    }
  },

  /**
   * Check if user is authenticated
   * Returns authentication status and user info
   */
  checkAuthStatus: async () => {
    try {
      // Note: api.js interceptor already returns response.data
      const data = await api.get('/api/auth/status');
      return data;
    } catch (error) {
      console.error('Error checking auth status:', error);
      return { authenticated: false };
    }
  },

  /**
   * Logout user
   * Clears session on backend
   */
  logout: async () => {
    try {
      // Note: api.js interceptor already returns response.data
      const data = await api.post('/api/auth/logout');
      return data;
    } catch (error) {
      console.error('Error logging out:', error);
      throw error;
    }
  },

  // ============================================================================
  // Legacy Methods (kept for compatibility)
  // ============================================================================

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