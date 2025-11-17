import React, { useState, useEffect, useContext } from 'react';
import { Container, Grid, Paper, Typography, Box, Chip, Alert, CircularProgress, Button, Card, CardContent } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { Videocam, MusicNote, Mood, CloudSync, CheckCircle, Refresh } from '@mui/icons-material';
import VideoFeed from '../components/VideoFeed/VideoFeed';
import MoodDisplay from '../components/MoodDisplay/MoodDisplay';
import MusicPlayer from '../components/MusicPlayer/MusicPlayer';
import { AuthContext } from '../App';
import { musicService } from '../services/musicService';

function DashboardPage() {
  const navigate = useNavigate();
  const { isAuthenticated, user, authLoading } = useContext(AuthContext);

  // You can connect these to your actual state management (Zustand)
  const [isConnected, setIsConnected] = useState(true);
  const [cameraActive, setCameraActive] = useState(false);

  // Sync status state
  const [syncStatus, setSyncStatus] = useState(null);
  const [checkingSyncStatus, setCheckingSyncStatus] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [syncError, setSyncError] = useState(null);

  // Check authentication and redirect if not logged in
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      console.log('User not authenticated, redirecting to home...');
      navigate('/');
    }
  }, [isAuthenticated, authLoading, navigate]);

  // Check sync status when dashboard loads
  useEffect(() => {
    if (isAuthenticated) {
      checkSyncStatus();
    }
  }, [isAuthenticated]);

  const checkSyncStatus = async () => {
    try {
      setCheckingSyncStatus(true);
      const response = await musicService.getSyncStatus();
      if (response.success) {
        setSyncStatus(response);
      }
    } catch (error) {
      console.error('Error checking sync status:', error);
    } finally {
      setCheckingSyncStatus(false);
    }
  };

 const handleSyncLibrary = async () => {
  try {
    setSyncing(true);
    setSyncError(null);
    const response = await musicService.syncLibrary(50); // ← Changed back to 50

    if (response.success) {
      // Refresh sync status after successful sync
      await checkSyncStatus();
    } else {
      setSyncError(response.error || 'Failed to sync library');
    }
  } catch (error) {
    console.error('Error syncing library:', error);
    setSyncError('Failed to sync library. Please try again.');
  } finally {
    setSyncing(false);
  }
};

  // Show loading while checking auth
  if (authLoading) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        }}
      >
        <Box sx={{ textAlign: 'center' }}>
          <CircularProgress size={60} sx={{ color: 'white', mb: 2 }} />
          <Typography variant="h6" sx={{ color: 'white' }}>
            Loading...
          </Typography>
        </Box>
      </Box>
    );
  }

  // Don't render dashboard if not authenticated
  if (!isAuthenticated) {
    return null;
  }

  return (
    <Box sx={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      py: 4
    }}>
      <Container maxWidth="xl">
        {/* Header Section */}
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <Typography
            variant="h3"
            sx={{
              color: 'white',
              fontWeight: 700,
              mb: 1,
              textShadow: '0 2px 4px rgba(0,0,0,0.2)'
            }}
          >
            🎵 MoodDJ Dashboard
          </Typography>
          <Typography variant="subtitle1" sx={{ color: 'rgba(255,255,255,0.9)', mb: 2 }}>
            Your mood, your music - personalized in real-time
          </Typography>

          {/* Status Indicators */}
          <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Chip
              label={isConnected ? "✓ Connected" : "✗ Disconnected"}
              color={isConnected ? "success" : "error"}
              size="small"
              sx={{ bgcolor: isConnected ? '#4caf50' : '#f44336', color: 'white', fontWeight: 600 }}
            />
            <Chip
              label={cameraActive ? "✓ Camera Active" : "Camera Inactive"}
              color={cameraActive ? "success" : "default"}
              size="small"
              sx={{ bgcolor: cameraActive ? '#4caf50' : '#757575', color: 'white', fontWeight: 600 }}
            />
            <Chip
              label="✓ Spotify Connected"
              color="success"
              size="small"
              sx={{ bgcolor: '#1DB954', color: 'white', fontWeight: 600 }}
            />
          </Box>
        </Box>

        {/* Help Alert */}
        <Alert
          severity="info"
          sx={{ mb: 3, borderRadius: 2, fontSize: '0.95rem' }}
        >
          <strong>Getting Started:</strong> Click "Start Detection" in the video feed below.
          Make sure Spotify is open and playing on your device for the best experience.
        </Alert>

        {/* Sync Library Prompt */}
        {!checkingSyncStatus && syncStatus && syncStatus.needs_sync && (
          <Card
            sx={{
              mb: 3,
              borderRadius: 3,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              boxShadow: '0 8px 24px rgba(102, 126, 234, 0.3)',
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <CloudSync sx={{ fontSize: 48, color: 'white' }} />
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
                      Welcome to MoodDJ!
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.95 }}>
                      Sync your Spotify library to get personalized music recommendations based on your mood.
                    </Typography>
                  </Box>
                </Box>
                <Button
                  variant="contained"
                  size="large"
                  onClick={handleSyncLibrary}
                  disabled={syncing}
                  startIcon={syncing ? <CircularProgress size={20} color="inherit" /> : <CloudSync />}
                  sx={{
                    bgcolor: 'white',
                    color: '#667eea',
                    fontWeight: 600,
                    px: 4,
                    py: 1.5,
                    borderRadius: 2,
                    '&:hover': {
                      bgcolor: 'rgba(255,255,255,0.9)',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 6px 16px rgba(0,0,0,0.2)',
                    },
                    '&:disabled': {
                      bgcolor: 'rgba(255,255,255,0.7)',
                      color: '#667eea',
                    },
                    transition: 'all 0.2s ease',
                  }}
                >
                  {syncing ? 'Re-Syncing...' : 'Re-Sync Library (50 random songs)'}
                </Button>
              </Box>
              {syncError && (
                <Alert severity="error" sx={{ mt: 2 }} onClose={() => setSyncError(null)}>
                  {syncError}
                </Alert>
              )}
            </CardContent>
          </Card>
        )}

        {/* Sync Success Message with Re-Sync Button */}
        {!checkingSyncStatus && syncStatus && syncStatus.synced && (
          <Card
            sx={{
              mb: 3,
              borderRadius: 3,
              background: 'linear-gradient(135deg, #4caf50 0%, #45a049 100%)',
              color: 'white',
              boxShadow: '0 8px 24px rgba(76, 175, 80, 0.3)',
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <CheckCircle sx={{ fontSize: 48, color: 'white' }} />
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
                      Library Synced!
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.95 }}>
                      You have {syncStatus.song_count} songs ready for mood-based playback.
                    </Typography>
                  </Box>
                </Box>
                <Button
                  variant="contained"
                  size="medium"
                  onClick={handleSyncLibrary}
                  disabled={syncing}
                  startIcon={syncing ? <CircularProgress size={20} color="inherit" /> : <Refresh />}
                  sx={{
                    bgcolor: 'white',
                    color: '#4caf50',
                    fontWeight: 600,
                    px: 3,
                    py: 1,
                    borderRadius: 2,
                    '&:hover': {
                      bgcolor: 'rgba(255,255,255,0.9)',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 6px 16px rgba(0,0,0,0.2)',
                    },
                    '&:disabled': {
                      bgcolor: 'rgba(255,255,255,0.7)',
                      color: '#4caf50',
                    },
                    transition: 'all 0.2s ease',
                  }}
                >
                  {syncing ? 'Re-Syncing...' : 'Re-Sync Library (50 songs)'}
                </Button>
              </Box>
              {syncError && (
                <Alert severity="error" sx={{ mt: 2 }} onClose={() => setSyncError(null)}>
                  {syncError}
                </Alert>
              )}
            </CardContent>
          </Card>
        )}

        <Grid container spacing={3}>
          {/* Video Feed - Left Column */}
          <Grid item xs={12} lg={6}>
            <Paper
              elevation={8}
              sx={{
                p: 3,
                height: '100%',
                borderRadius: 3,
                background: 'linear-gradient(to bottom, #ffffff, #f8f9fa)',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: '0 12px 24px rgba(0,0,0,0.15)'
                }
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Videocam sx={{ mr: 1, color: '#667eea', fontSize: 28 }} />
                <Typography variant="h5" sx={{ fontWeight: 600, color: '#2d3748' }}>
                  Live Camera Feed
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                📸 Your facial expressions are analyzed every 5 seconds to detect your mood
              </Typography>
              <VideoFeed />
            </Paper>
          </Grid>

          {/* Right Column - Mood & Music */}
          <Grid item xs={12} lg={6}>
            <Grid container spacing={3}>
              {/* Mood Display */}
              <Grid item xs={12}>
                <Paper
                  elevation={8}
                  sx={{
                    p: 3,
                    borderRadius: 3,
                    background: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 12px 24px rgba(0,0,0,0.15)'
                    }
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Mood sx={{ mr: 1, color: '#d84315', fontSize: 28 }} />
                    <Typography variant="h5" sx={{ fontWeight: 600, color: '#2d3748' }}>
                      Current Mood
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    🎭 Detected from your facial expressions in real-time
                  </Typography>
                  <MoodDisplay />
                </Paper>
              </Grid>

              {/* Music Player */}
              <Grid item xs={12}>
                <Paper
                  elevation={8}
                  sx={{
                    p: 3,
                    borderRadius: 3,
                    background: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 12px 24px rgba(0,0,0,0.15)'
                    }
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <MusicNote sx={{ mr: 1, color: '#1DB954', fontSize: 28 }} />
                    <Typography variant="h5" sx={{ fontWeight: 600, color: '#2d3748' }}>
                      Music Player
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    🎶 Automatically matched to your current mood
                  </Typography>
                  <MusicPlayer />
                </Paper>
              </Grid>
            </Grid>
          </Grid>

        </Grid>

        {/* Footer Help Text */}
        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)', fontSize: '0.95rem' }}>
            💡 <strong>Pro Tip:</strong> For best results, ensure good lighting and face the camera directly
          </Typography>
        </Box>
      </Container>
    </Box>
  );
}

export default DashboardPage;