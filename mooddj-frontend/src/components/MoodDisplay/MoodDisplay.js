import React from 'react';
import { Box, Typography, Chip } from '@mui/material';
import SentimentSatisfiedAltIcon from '@mui/icons-material/SentimentSatisfiedAlt';
import SentimentNeutralIcon from '@mui/icons-material/SentimentNeutral';
import SentimentDissatisfiedIcon from '@mui/icons-material/SentimentDissatisfied';
import SentimentVerySatisfiedIcon from '@mui/icons-material/SentimentVerySatisfied';
import useStore from '../../store/useStore';

const moodConfig = {
  happy: {
    icon: SentimentVerySatisfiedIcon,
    color: '#4CAF50',
    label: 'Happy',
  },
  sad: {
    icon: SentimentDissatisfiedIcon,
    color: '#2196F3',
    label: 'Sad',
  },
  neutral: {
    icon: SentimentNeutralIcon,
    color: '#9E9E9E',
    label: 'Neutral',
  },
  angry: {
    icon: SentimentDissatisfiedIcon,
    color: '#F44336',
    label: 'Angry',
  },
  surprised: {
    icon: SentimentSatisfiedAltIcon,
    color: '#FF9800',
    label: 'Surprised',
  },
  excited: {
    icon: SentimentVerySatisfiedIcon,
    color: '#FF6F00',
    label: 'Excited',
  },
  calm: {
    icon: SentimentNeutralIcon,
    color: '#00BCD4',
    label: 'Calm',
  },
};

function MoodDisplay() {
  const { currentMood, moodConfidence, moodHistory } = useStore();

  const MoodIcon = moodConfig[currentMood]?.icon || SentimentNeutralIcon;
  const moodColor = moodConfig[currentMood]?.color || '#9E9E9E';
  const moodLabel = moodConfig[currentMood]?.label || 'Unknown';

  // Get last 3 moods for history
  const recentMoods = moodHistory.slice(0, 3).map(h => h.mood);

  return (
    <Box>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          py: 3,
        }}
      >
        <MoodIcon
          sx={{
            fontSize: 80,
            color: moodColor,
            mb: 2,
            transition: 'all 0.3s ease',
          }}
        />

        <Typography variant="h4" sx={{ color: moodColor, mb: 1 }}>
          {moodLabel}
        </Typography>

        <Chip
          label={`${Math.round(moodConfidence * 100)}% confident`}
          size="small"
          sx={{ bgcolor: 'background.default' }}
        />
      </Box>

      <Box sx={{ mt: 2 }}>
        <Typography variant="caption" color="text.secondary">
          Mood history: {recentMoods.length > 0 ? recentMoods.join(' → ') : 'No history yet'}
        </Typography>
      </Box>
    </Box>
  );
}

export default MoodDisplay;
