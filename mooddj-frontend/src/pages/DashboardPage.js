import React from 'react';
import { Container, Grid, Paper } from '@mui/material';
import VideoFeed from '../components/VideoFeed/VideoFeed';
import MoodDisplay from '../components/MoodDisplay/MoodDisplay';
import MusicPlayer from '../components/MusicPlayer/MusicPlayer';
import Analytics from '../components/Analytics/Analytics';

function DashboardPage() {
  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Grid container spacing={3}>
        {/* Video Feed - Left Column */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 2, height: '100%' }}>
            <VideoFeed />
          </Paper>
        </Grid>

        {/* Right Column - Mood & Music */}
        <Grid item xs={12} md={6}>
          <Grid container spacing={3}>
            {/* Mood Display */}
            <Grid item xs={12}>
              <Paper elevation={3} sx={{ p: 2 }}>
                <MoodDisplay />
              </Paper>
            </Grid>

            {/* Music Player */}
            <Grid item xs={12}>
              <Paper elevation={3} sx={{ p: 2 }}>
                <MusicPlayer />
              </Paper>
            </Grid>
          </Grid>
        </Grid>

        {/* Analytics - Full Width Bottom */}
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ p: 2 }}>
            <Analytics />
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default DashboardPage;