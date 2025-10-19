import { create } from 'zustand';

const useStore = create((set) => ({
  // Mood state
  currentMood: 'neutral',
  moodConfidence: 0,
  moodHistory: [],
  
  setCurrentMood: (mood, confidence) =>
    set((state) => ({
      currentMood: mood,
      moodConfidence: confidence,
      moodHistory: [
        { mood, confidence, timestamp: new Date().toISOString() },
        ...state.moodHistory.slice(0, 9), // Keep last 10
      ],
    })),

  // Music state
  currentTrack: null,
  isPlaying: false,
  playlist: [],
  
  setCurrentTrack: (track) => set({ currentTrack: track }),
  setIsPlaying: (isPlaying) => set({ isPlaying }),
  setPlaylist: (playlist) => set({ playlist }),

  // User state
  user: null,
  setUser: (user) => set({ user }),

  // Detection state
  isDetecting: false,
  setIsDetecting: (isDetecting) => set({ isDetecting }),

  // Stats
  stats: {
    songsPlayed: 0,
    moodChanges: 0,
    sessionTime: 0,
  },
  updateStats: (stats) => set({ stats }),
}));

export default useStore;