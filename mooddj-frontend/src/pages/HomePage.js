import React from 'react';
import { Container, Box, Typography, Button, Card, CardContent, Grid, Chip } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import MusicNoteIcon from '@mui/icons-material/MusicNote';
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import GraphicEqIcon from '@mui/icons-material/GraphicEq';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import { keyframes } from '@mui/system';

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

  const features = [
    {
      icon: <CameraAltIcon sx={{ fontSize: 32, color: '#667eea' }} />,
      title: 'Real-Time Detection',
      description: 'AI analyzes your expressions'
    },
    {
      icon: <GraphicEqIcon sx={{ fontSize: 32, color: '#1DB954' }} />,
      title: 'Smart Matching',
      description: 'Music that matches your mood'
    },
    {
      icon: <AutoAwesomeIcon sx={{ fontSize: 32, color: '#f093fb' }} />,
      title: 'Mood Analytics',
      description: 'Track emotional patterns'
    }
  ];

  return (
    <Box
      sx={{
        height: '100vh',
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
          width: 80,
          height: 80,
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
          width: 120,
          height: 120,
          borderRadius: '50%',
          background: 'rgba(255, 255, 255, 0.1)',
          animation: `${float} 8s ease-in-out infinite`,
        }}
      />

      <Container maxWidth="lg" sx={{ height: '100%' }}>
        <Box
          sx={{
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            textAlign: 'center',
            py: 3,
          }}
        >
          {/* Hero Section */}
          <Box sx={{ mb: 2, animation: `${pulse} 3s ease-in-out infinite` }}>
            <Box
              sx={{
                background: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
                borderRadius: '50%',
                width: 80,
                height: 80,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto',
                mb: 2,
                boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
              }}
            >
              <MusicNoteIcon sx={{ fontSize: 40, color: '#fff' }} />
            </Box>
          </Box>

          <Typography
            variant="h1"
            component="h1"
            gutterBottom
            sx={{
              color: 'white',
              fontWeight: 800,
              fontSize: { xs: '2.5rem', md: '3.5rem' },
              textShadow: '0 4px 12px rgba(0,0,0,0.3)',
              mb: 1,
            }}
          >
            🎵 MoodDJ
          </Typography>

          <Typography
            variant="h4"
            sx={{
              color: 'rgba(255, 255, 255, 0.95)',
              fontWeight: 500,
              mb: 1.5,
              fontSize: { xs: '1.25rem', md: '1.75rem' },
            }}
          >
            Your Mood, Your Music
          </Typography>

          <Typography
            variant="h6"
            sx={{
              color: 'rgba(255, 255, 255, 0.85)',
              maxWidth: 600,
              mb: 3,
              lineHeight: 1.5,
              px: 2,
              fontSize: { xs: '0.9rem', md: '1rem' },
            }}
          >
            Let AI detect your emotions and automatically curate the perfect soundtrack for your mood.
          </Typography>

          {/* Feature Cards */}
          <Grid container spacing={2} sx={{ mb: 3, maxWidth: 800 }}>
            {features.map((feature, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Card
                  sx={{
                    height: '100%',
                    background: 'rgba(255, 255, 255, 0.95)',
                    backdropFilter: 'blur(10px)',
                    borderRadius: 2,
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: '0 8px 16px rgba(0,0,0,0.2)',
                    },
                  }}
                >
                  <CardContent sx={{ textAlign: 'center', py: 2 }}>
                    <Box sx={{ mb: 1 }}>{feature.icon}</Box>
                    <Typography
                      variant="subtitle1"
                      gutterBottom
                      sx={{ fontWeight: 600, color: '#2d3748', fontSize: '0.95rem' }}
                    >
                      {feature.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.85rem' }}>
                      {feature.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* CTA Button */}
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate('/dashboard')}
            sx={{
              mt: 1,
              px: 6,
              py: 2,
              fontSize: '1.1rem',
              fontWeight: 600,
              background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
              color: 'white',
              borderRadius: 3,
              textTransform: 'none',
              boxShadow: '0 8px 24px rgba(240, 147, 251, 0.4)',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 12px 32px rgba(240, 147, 251, 0.6)',
                background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
              },
            }}
          >
            Get Started →
          </Button>

          {/* Requirements Chips */}
          <Box
            sx={{
              mt: 2.5,
              display: 'flex',
              gap: 1.5,
              flexWrap: 'wrap',
              justifyContent: 'center',
            }}
          >
            <Chip
              label="📹 Camera"
              size="small"
              sx={{
                bgcolor: 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                fontWeight: 500,
                backdropFilter: 'blur(10px)',
              }}
            />
            <Chip
              label="🎧 Spotify"
              size="small"
              sx={{
                bgcolor: 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                fontWeight: 500,
                backdropFilter: 'blur(10px)',
              }}
            />
            <Chip
              label="✨ AI Powered"
              size="small"
              sx={{
                bgcolor: 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                fontWeight: 500,
                backdropFilter: 'blur(10px)',
              }}
            />
          </Box>
        </Box>
      </Container>
    </Box>
  );
}

export default HomePage;
