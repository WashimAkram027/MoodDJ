import React, { useEffect, useState } from 'react';
import { Box, Typography, IconButton, LinearProgress, Avatar, Alert, Card, CardContent } from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';
import SkipNextIcon from '@mui/icons-material/SkipNext';
import SkipPreviousIcon from '@mui/icons-material/SkipPrevious';
import MusicNoteIcon from '@mui/icons-material/MusicNote';
import useStore from '../../store/useStore';
import { musicService } from '../../services/musicService';

function MusicPlayer() {
  const { currentMood, currentTrack, isPlaying, playlist, setCurrentTrack, setIsPlaying, setPlaylist } = useStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);

  // Fetch recommendations when mood changes
  useEffect(() => {
    if (currentMood && currentMood !== 'neutral') {
      fetchRecommendations(currentMood);
    }
  }, [currentMood]);

  const fetchRecommendations = async (mood) => {
    try {
      setLoading(true);
      setError(null);
      const response = await musicService.getRecommendations(mood, 20);
      
      if (response.success && response.songs.length > 0) {
        setPlaylist(response.songs);
        setCurrentIndex(0);
        // Auto-play first song
        if (response.songs[0]) {
          playTrack(response.songs[0]);
        }
      } else {
        setError('No songs found for this mood. Try syncing your Spotify library first.');
      }
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      setError('Failed to load music recommendations');
    } finally {
      setLoading(false);
    }
  };

  const playTrack = async (track) => {
    try {
      setError(null);
      const result = await musicService.playTrack(track.spotify_song_id);
      
      if (result.success) {
        setCurrentTrack({
          id: track.spotify_song_id,
          title: track.title,
          artist: track.artist,
          album: track.album,
        });
        setIsPlaying(true);
      } else {
        setError(result.error || 'Failed to play track. Make sure Spotify is open.');
      }
    } catch (err) {
      console.error('Error playing track:', err);
      setError('Failed to play track. Make sure Spotify is open and active.');
    }
  };

  const handlePlayPause = () => {
    // This would call Spotify API to pause/resume
    setIsPlaying(!isPlaying);
  };

  const handleNext = () => {
    if (playlist.length > 0) {
      const nextIndex = (currentIndex + 1) % playlist.length;
      setCurrentIndex(nextIndex);
      playTrack(playlist[nextIndex]);
    }
  };

  const handlePrevious = () => {
    if (playlist.length > 0) {
      const prevIndex = currentIndex === 0 ? playlist.length - 1 : currentIndex - 1;
      setCurrentIndex(prevIndex);
      playTrack(playlist[prevIndex]);
    }
  };

  const displayTrack = currentTrack || {
    title: 'No track playing',
    artist: 'Start mood detection to play music',
    album: '',
  };

  // Get mood color for visual feedback
  const moodColors = {
    happy: '#4CAF50',
    sad: '#2196F3',
    neutral: '#9E9E9E',
    angry: '#F44336',
    surprised: '#FF9800',
    excited: '#FF6F00',
    calm: '#00BCD4',
  };
  
  const currentMoodColor = moodColors[currentMood] || '#9E9E9E';

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Now Playing
      </Typography>

      {error && (
        <Alert severity="warning" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Card
        sx={{
          background: `linear-gradient(135deg, ${currentMoodColor}15 0%, ${currentMoodColor}05 100%)`,
          borderRadius: 2,
          border: `1px solid ${currentMoodColor}30`,
        }}
      >
        <CardContent>
          {loading && <LinearProgress sx={{ mb: 2, borderRadius: 1 }} />}

          <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
            <Avatar
              variant="rounded"
              sx={{
                width: 80,
                height: 80,
                bgcolor: currentMoodColor,
                boxShadow: `0 4px 12px ${currentMoodColor}40`,
              }}
            >
              <MusicNoteIcon sx={{ fontSize: 40 }} />
            </Avatar>

            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography variant="subtitle1" noWrap sx={{ fontWeight: 600, mb: 0.5 }}>
                {displayTrack.title}
              </Typography>
              <Typography variant="body2" color="text.secondary" noWrap>
                {displayTrack.artist}
              </Typography>
              {displayTrack.album && (
                <Typography variant="caption" color="text.secondary" noWrap>
                  {displayTrack.album}
                </Typography>
              )}
            </Box>
          </Box>

          <Box sx={{ mb: 3 }}>
            <LinearProgress
              variant="determinate"
              value={isPlaying ? 50 : 0}
              sx={{
                height: 6,
                borderRadius: 3,
                bgcolor: 'action.hover',
                '& .MuiLinearProgress-bar': {
                  bgcolor: currentMoodColor,
                  borderRadius: 3,
                },
              }}
            />
          </Box>

          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              gap: 2,
            }}
          >
            <IconButton
              onClick={handlePrevious}
              disabled={!playlist.length}
              sx={{
                color: currentMoodColor,
                '&:hover': { bgcolor: `${currentMoodColor}15` },
                '&:disabled': { color: 'action.disabled' },
              }}
            >
              <SkipPreviousIcon sx={{ fontSize: 32 }} />
            </IconButton>

            <IconButton
              onClick={handlePlayPause}
              disabled={!currentTrack}
              sx={{
                bgcolor: currentMoodColor,
                color: 'white',
                width: 56,
                height: 56,
                boxShadow: `0 4px 12px ${currentMoodColor}40`,
                '&:hover': {
                  bgcolor: currentMoodColor,
                  transform: 'scale(1.05)',
                  boxShadow: `0 6px 16px ${currentMoodColor}60`,
                },
                '&:disabled': {
                  bgcolor: 'action.disabledBackground',
                  color: 'action.disabled',
                },
                transition: 'all 0.2s ease',
              }}
            >
              {isPlaying ? <PauseIcon sx={{ fontSize: 32 }} /> : <PlayArrowIcon sx={{ fontSize: 32 }} />}
            </IconButton>

            <IconButton
              onClick={handleNext}
              disabled={!playlist.length}
              sx={{
                color: currentMoodColor,
                '&:hover': { bgcolor: `${currentMoodColor}15` },
                '&:disabled': { color: 'action.disabled' },
              }}
            >
              <SkipNextIcon sx={{ fontSize: 32 }} />
            </IconButton>
          </Box>

          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ mt: 3, display: 'block', textAlign: 'center' }}
          >
            {currentMood !== 'neutral' 
              ? `🎵 Playing ${currentMood} mood music ${playlist.length > 0 ? `• ${playlist.length} songs` : ''}`
              : '🎵 Music adapts to your mood in real-time'}
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}

export default MusicPlayer;