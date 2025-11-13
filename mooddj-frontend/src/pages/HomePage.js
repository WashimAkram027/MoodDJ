import React, { useState } from 'react';
import { Container, Box, Typography, Button, Card, CardContent, Grid, Chip, CircularProgress } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import MusicNoteIcon from '@mui/icons-material/MusicNote';
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import GraphicEqIcon from '@mui/icons-material/GraphicEq';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import { keyframes } from '@mui/system';
import { authService } from '../services/authService';

// Animation for floating effect
const float = keyframes`
  0% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
  100% { transform: translateY(0px); }
`;

const pulse = keyframes`
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
`;

function HomePage() {
  const navigate = useNavigate();
  const [isConnecting, setIsConnecting] = useState(false);

  const handleConnectSpotify = async () => {
    try {
      setIsConnecting(true);
      await authService.initiateSpotifyLogin();
      // Will redirect to Spotify, so no need to setIsConnecting(false)
    } catch (error) {
      console.error('Failed to connect to Spotify:', error);
      setIsConnecting(false);
      alert('Failed to connect to Spotify. Please try again.');
    }
  };

  const features = [
    {
      icon: <CameraAltIcon sx={{ fontSize: 40, color: '#667eea' }} />,
      title: 'Real-Time Detection',
      description: 'AI analyzes your facial expressions every 2 seconds'
    },
    {
      icon: <GraphicEqIcon sx={{ fontSize: 40, color: '#1DB954' }} />,
      title: 'Smart Matching',
      description: 'Automatically plays music that matches your mood'
    },
    {
      icon: <AutoAwesomeIcon sx={{ fontSize: 40, color: '#f093fb' }} />,
      title: 'Mood Analytics',
      description: 'Track your emotional patterns over time'
    }
  ];

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Animated Background Elements */}
      <Box
        sx={{
          position: 'absolute',
          top: '10%',
          left: '5%',
          width: 100,
          height: 100,
          borderRadius: '50%',
          background: 'rgba(255, 255, 255, 0.1)',
          animation: `${float} 6s ease-in-out infinite`,
        }}
      />
      <Box
        sx={{
          position: 'absolute',
          bottom: '15%',
          right: '10%',
          width: 150,
          height: 150,
          borderRadius: '50%',
          background: 'rgba(255, 255, 255, 0.1)',
          animation: `${float} 8s ease-in-out infinite`,
        }}
      />

      <Container maxWidth="lg">
        <Box
          sx={{
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            textAlign: 'center',
            py: 4,
          }}
        >
          {/* Hero Section */}
          <Box sx={{ mb: 6, animation: `${pulse} 3s ease-in-out infinite` }}>
            <Box
              sx={{
                background: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
                borderRadius: '50%',
                width: 120,
                height: 120,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto',
                mb: 3,
                boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
              }}
            >
              <MusicNoteIcon sx={{ fontSize: 60, color: '#fff' }} />
            </Box>
          </Box>

          <Typography
            variant="h1"
            component="h1"
            gutterBottom
            sx={{
              color: 'white',
              fontWeight: 800,
              fontSize: { xs: '3rem', md: '4.5rem' },
              textShadow: '0 4px 12px rgba(0,0,0,0.3)',
              mb: 2,
            }}
          >
            🎵 MoodDJ
          </Typography>

          <Typography
            variant="h4"
            sx={{
              color: 'rgba(255, 255, 255, 0.95)',
              fontWeight: 500,
              mb: 2,
              fontSize: { xs: '1.5rem', md: '2rem' },
            }}
          >
            Your Mood, Your Music
          </Typography>

          <Typography
            variant="h6"
            sx={{
              color: 'rgba(255, 255, 255, 0.85)',
              maxWidth: 700,
              mb: 4,
              lineHeight: 1.6,
              px: 2,
              fontSize: { xs: '1rem', md: '1.25rem' },
            }}
          >
            Experience the future of personalized music. Let AI detect your emotions
            through your camera and automatically curate the perfect soundtrack for your mood.
          </Typography>

          {/* Feature Cards */}
          <Grid container spacing={3} sx={{ mb: 5, maxWidth: 900 }}>
            {features.map((feature, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Card
                  sx={{
                    height: '100%',
                    background: 'rgba(255, 255, 255, 0.95)',
                    backdropFilter: 'blur(10px)',
                    borderRadius: 3,
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-8px)',
                      boxShadow: '0 12px 24px rgba(0,0,0,0.2)',
                    },
                  }}
                >
                  <CardContent sx={{ textAlign: 'center', py: 3 }}>
                    <Box sx={{ mb: 2 }}>{feature.icon}</Box>
                    <Typography
                      variant="h6"
                      gutterBottom
                      sx={{ fontWeight: 600, color: '#2d3748' }}
                    >
                      {feature.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {feature.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* CTA Button with OAuth */}
          <Button
            variant="contained"
            size="large"
            onClick={handleConnectSpotify}
            disabled={isConnecting}
            sx={{
              mt: 2,
              px: 8,
              py: 2.5,
              fontSize: '1.2rem',
              fontWeight: 600,
              background: isConnecting
                ? 'rgba(29, 185, 84, 0.6)'
                : 'linear-gradient(135deg, #1DB954 0%, #1ed760 100%)',
              color: 'white',
              borderRadius: 3,
              textTransform: 'none',
              boxShadow: '0 8px 24px rgba(29, 185, 84, 0.4)',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: isConnecting ? 'none' : 'translateY(-4px)',
                boxShadow: isConnecting ? '0 8px 24px rgba(29, 185, 84, 0.4)' : '0 12px 32px rgba(29, 185, 84, 0.6)',
                background: isConnecting
                  ? 'rgba(29, 185, 84, 0.6)'
                  : 'linear-gradient(135deg, #1DB954 0%, #1ed760 100%)',
              },
              '&:disabled': {
                color: 'white',
              },
            }}
          >
            {isConnecting ? (
              <>
                <CircularProgress size={24} sx={{ color: 'white', mr: 2 }} />
                Connecting to Spotify...
              </>
            ) : (
              <>
                🎵 Connect with Spotify →
              </>
            )}
          </Button>

          {/* Requirements Chips */}
          <Box
            sx={{
              mt: 5,
              display: 'flex',
              gap: 2,
              flexWrap: 'wrap',
              justifyContent: 'center',
            }}
          >
            <Chip
              label="📹 Camera Required"
              sx={{
                bgcolor: 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                fontWeight: 500,
                backdropFilter: 'blur(10px)',
              }}
            />
            <Chip
              label="🎧 Spotify Premium"
              sx={{
                bgcolor: 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                fontWeight: 500,
                backdropFilter: 'blur(10px)',
              }}
            />
            <Chip
              label="✨ AI Powered"
              sx={{
                bgcolor: 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                fontWeight: 500,
                backdropFilter: 'blur(10px)',
              }}
            />
          </Box>

          {/* Footer Note */}
          <Typography
            variant="body2"
            sx={{
              mt: 6,
              color: 'rgba(255, 255, 255, 0.8)',
              fontSize: '0.95rem',
            }}
          >
            💡 Make sure your camera and Spotify are ready before starting
          </Typography>
        </Box>
      </Container>
    </Box>
  );
}

export default HomePage;
