import React, { useRef, useState, useEffect } from 'react';
import Webcam from 'react-webcam';
import { Box, Button, Typography, Alert, Chip } from '@mui/material';
import VideocamIcon from '@mui/icons-material/Videocam';
import VideocamOffIcon from '@mui/icons-material/VideocamOff';
import SentimentSatisfiedAltIcon from '@mui/icons-material/SentimentSatisfiedAlt';
import SentimentNeutralIcon from '@mui/icons-material/SentimentNeutral';
import SentimentDissatisfiedIcon from '@mui/icons-material/SentimentDissatisfied';
import SentimentVerySatisfiedIcon from '@mui/icons-material/SentimentVerySatisfied';
import { moodService } from '../../services/moodService';
import useStore from '../../store/useStore';
import websocketService from '../../services/websocket';

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

function MoodDetectionView() {
  const webcamRef = useRef(null);
  const [isActive, setIsActive] = useState(false);
  const [error, setError] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  
  const { currentMood, moodConfidence, moodHistory, setCurrentMood, isDetecting, setIsDetecting } = useStore();

  const MoodIcon = moodConfig[currentMood]?.icon || SentimentNeutralIcon;
  const moodColor = moodConfig[currentMood]?.color || '#9E9E9E';
  const moodLabel = moodConfig[currentMood]?.label || 'Unknown';
  const recentMoods = moodHistory.slice(0, 3).map(h => h.mood);

  useEffect(() => {
    let intervalId;

    if (isActive && isDetecting) {
      intervalId = setInterval(async () => {
        await captureAndDetectMood();
      }, 2000);
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [isActive, isDetecting]);

  const captureAndDetectMood = async () => {
    if (!webcamRef.current || isProcessing) return;

    try {
      setIsProcessing(true);
      
      const imageSrc = webcamRef.current.getScreenshot();
      
      if (!imageSrc) {
        console.log('No image captured');
        return;
      }

      const result = await moodService.detectMood(imageSrc);
      
      if (result && result.detected) {
        console.log('Mood detected:', result.mood, 'Confidence:', result.confidence);
        
        setCurrentMood(result.mood, result.confidence);
        websocketService.sendMoodUpdate(result.mood, result.confidence);
        await moodService.logMood(result.mood, result.confidence);
      }
      
    } catch (error) {
      console.error('Error detecting mood:', error);
      setError('Failed to detect mood. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleStartCamera = () => {
    setIsActive(true);
    setIsDetecting(true);
    setError(null);
    
    websocketService.connect();
    websocketService.startDetection();
  };

  const handleStopCamera = () => {
    setIsActive(false);
    setIsDetecting(false);
    
    websocketService.stopDetection();
    websocketService.disconnect();
  };

  const handleUserMediaError = (err) => {
    console.error('Camera error:', err);
    setError('Unable to access camera. Please check permissions.');
    setIsActive(false);
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Mood Detection
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Main content - Video and Mood side by side */}
      <Box
        sx={{
          display: 'flex',
          gap: 3,
          flexDirection: { xs: 'column', md: 'row' },
          alignItems: 'stretch',
        }}
      >
        {/* Video Feed Section */}
        <Box sx={{ flex: 1 }}>
          <Typography variant="h6" gutterBottom>
            Camera Feed
          </Typography>

          <Box
            sx={{
              position: 'relative',
              width: '100%',
              aspectRatio: '16/9',
              bgcolor: 'background.default',
              borderRadius: 1,
              overflow: 'hidden',
              mb: 2,
            }}
          >
            {isActive ? (
              <>
                <Webcam
                  ref={webcamRef}
                  audio={false}
                  screenshotFormat="image/jpeg"
                  videoConstraints={{
                    width: 640,
                    height: 360,
                    facingMode: 'user',
                  }}
                  onUserMediaError={handleUserMediaError}
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                  }}
                />
                {isProcessing && (
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 8,
                      right: 8,
                      bgcolor: 'primary.main',
                      color: 'white',
                      px: 2,
                      py: 0.5,
                      borderRadius: 1,
                      fontSize: '0.75rem',
                    }}
                  >
                    Detecting...
                  </Box>
                )}
              </>
            ) : (
              <Box
                sx={{
                  width: '100%',
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center',
                  alignItems: 'center',
                  color: 'text.secondary',
                }}
              >
                <VideocamOffIcon sx={{ fontSize: 60, mb: 2 }} />
                <Typography>Camera is off</Typography>
              </Box>
            )}
          </Box>

          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              startIcon={<VideocamIcon />}
              onClick={handleStartCamera}
              disabled={isActive}
              fullWidth
            >
              Start Detection
            </Button>
            <Button
              variant="outlined"
              startIcon={<VideocamOffIcon />}
              onClick={handleStopCamera}
              disabled={!isActive}
              fullWidth
            >
              Stop Detection
            </Button>
          </Box>

          <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
            {isDetecting ? '🟢 Detecting mood every 2 seconds...' : 'Your video is processed locally and never stored'}
          </Typography>
        </Box>

        {/* Mood Display Section */}
        <Box sx={{ flex: 1 }}>
          <Typography variant="h6" gutterBottom>
            Current Mood
          </Typography>
          
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              py: 3,
              bgcolor: 'background.default',
              borderRadius: 1,
              minHeight: { xs: 'auto', md: '100%' },
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
              sx={{ bgcolor: 'background.paper' }}
            />

            <Box sx={{ mt: 3, textAlign: 'center', px: 2 }}>
              <Typography variant="caption" color="text.secondary">
                Mood history: {recentMoods.length > 0 ? recentMoods.join(' → ') : 'No history yet'}
              </Typography>
            </Box>
          </Box>
        </Box>
      </Box>
    </Box>
  );
}

export default MoodDetectionView;
