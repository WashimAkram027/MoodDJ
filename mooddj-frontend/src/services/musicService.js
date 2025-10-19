import api from './api';

export const musicService = {
  // Get song recommendations based on mood
  getRecommendations: async (mood, limit = 30) => {
    return api.post('/api/music/recommend', { mood, limit });
  },

  // Play a track
  playTrack: async (trackId, deviceId = null) => {
    return api.post('/api/music/play', {
      track_id: trackId,
      device_id: deviceId,
    });
  },

  // Get current playback
  getCurrentPlayback: async () => {
    return api.get('/api/music/current');
  },

  // Sync Spotify library
  syncLibrary: async (limit = 50) => {
    return api.post('/api/music/sync', { limit });
  },

  // Create mood playlist
  createPlaylist: async (userId, mood, trackIds) => {
    return api.post('/api/music/playlist/create', {
      user_id: userId,
      mood,
      track_ids: trackIds,
    });
  },
};