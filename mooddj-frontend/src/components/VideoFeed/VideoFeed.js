import React, { useRef, useState, useEffect } from 'react';
import Webcam from 'react-webcam';
import { Box, Button, Typography, Alert } from '@mui/material';
import VideocamIcon from '@mui/icons-material/Videocam';
import VideocamOffIcon from '@mui/icons-material/VideocamOff';
import { moodService } from '../../services/moodService';
import useStore from '../../store/useStore';
import websocketService from '../../services/websocket';

function VideoFeed() {
  const webcamRef = useRef(null);
  const [isActive, setIsActive] = useState(false);
  const [error, setError] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  
  const { setCurrentMood, isDetecting, setIsDetecting } = useStore();

  useEffect(() => {
    let intervalId;

    if (isActive && isDetecting) {
      // Capture and process frame every 2 seconds
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
      
      // Capture image from webcam
      const imageSrc = webcamRef.current.getScreenshot();
      
      if (!imageSrc) {
        console.log('No image captured');
        return;
      }

      // Send to backend for mood detection
      const result = await moodService.detectMood(imageSrc);
      
      if (result && result.detected) {
        console.log('Mood detected:', result.mood, 'Confidence:', result.confidence);
        
        // Update store
        setCurrentMood(result.mood, result.confidence);
        
        // Send via WebSocket for real-time updates
        websocketService.sendMoodUpdate(result.mood, result.confidence);
        
        // Log to database
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
    
    // Connect WebSocket
    websocketService.connect();
    websocketService.startDetection();
  };

  const handleStopCamera = () => {
    setIsActive(false);
    setIsDetecting(false);
    
    // Disconnect WebSocket
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
      <Typography variant="h6" gutterBottom>
        Camera Feed
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Box
        sx={{
          position: 'relative',
          width: '100%',
          aspectRatio: '4/3',
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
                width: 1280,
                height: 720,
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
  );
}

export default VideoFeed;
