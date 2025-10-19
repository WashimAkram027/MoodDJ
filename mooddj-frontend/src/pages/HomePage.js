import React from 'react';
import { Container, Box, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import MusicNoteIcon from '@mui/icons-material/MusicNote';

function HomePage() {
  const navigate = useNavigate();

  return (
    <Container maxWidth="md">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          textAlign: 'center',
        }}
      >
        <MusicNoteIcon sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
        
        <Typography variant="h2" component="h1" gutterBottom>
          MoodDJ
        </Typography>
        
        <Typography variant="h5" color="text.secondary" paragraph>
          Your Mood, Your Music
        </Typography>
        
        <Typography variant="body1" color="text.secondary" paragraph sx={{ maxWidth: 600 }}>
          Let AI detect your mood through your camera and automatically adjust 
          your music to match how you're feeling.
        </Typography>

        <Button
          variant="contained"
          size="large"
          onClick={() => navigate('/dashboard')}
          sx={{ mt: 4, px: 6, py: 2 }}
        >
          Get Started
        </Button>

        <Typography variant="caption" color="text.secondary" sx={{ mt: 4 }}>
          Make sure your camera and Spotify are ready
        </Typography>
      </Box>
    </Container>
  );
}

export default HomePage;