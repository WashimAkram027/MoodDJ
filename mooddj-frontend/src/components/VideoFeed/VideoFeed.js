// mooddj-frontend/src/components/VideoFeed/VideoFeed.js
// UPDATED - Uses browser-based detection (no server calls!)

import React, { useRef, useState, useEffect } from 'react';
import Webcam from 'react-webcam';
import { Box, Button, Typography, Alert, Chip, CircularProgress } from '@mui/material';
import VideocamIcon from '@mui/icons-material/Videocam';
import VideocamOffIcon from '@mui/icons-material/VideocamOff';
import SpeedIcon from '@mui/icons-material/Speed';
import CloudOffIcon from '@mui/icons-material/CloudOff';
import browserMoodDetector from '../../services/browserMoodDetector';
import useStore from '../../store/useStore';
import websocketService from '../../services/websocket';

function VideoFeed() {
  const webcamRef = useRef(null);
  const videoRef = useRef(null);
  const [isActive, setIsActive] = useState(false);
  const [error, setError] = useState(null);
  const [isInitializing, setIsInitializing] = useState(false);
  const [lastDetectionTime, setLastDetectionTime] = useState(0);
  const [fps, setFps] = useState(0);
  
  const { setCurrentMood, isDetecting, setIsDetecting } = useStore();

  // Detection runs at ~10 FPS (100ms interval) - much faster than before!
  const DETECTION_INTERVAL = 100; // 100ms = 10 times per second

  useEffect(() => {
    let intervalId;
    let fpsCounter = 0;
    let fpsInterval;

    if (isActive && isDetecting && videoRef.current) {
      // Start detection loop
      intervalId = setInterval(() => {
        detectMoodFromVideo();
        fpsCounter++;
      }, DETECTION_INTERVAL);

      // Update FPS counter every second
      fpsInterval = setInterval(() => {
        setFps(fpsCounter);
        fpsCounter = 0;
      }, 1000);
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
      if (fpsInterval) clearInterval(fpsInterval);
    };
  }, [isActive, isDetecting]);

  const detectMoodFromVideo = () => {
    if (!videoRef.current || !videoRef.current.video) return;

    const startTime = performance.now();

    try {
      // Detect mood directly from video element (no image upload!)
      const result = browserMoodDetector.detectMood(videoRef.current.video);
      
      if (result && result.detected) {
        const detectionTime = performance.now() - startTime;
        setLastDetectionTime(detectionTime);
        
        // Update store
        setCurrentMood(result.mood, result.confidence);
        
        // Send via WebSocket for real-time updates (optional)
        websocketService.sendMoodUpdate(result.mood, result.confidence);
      }
      
    } catch (error) {
      console.error('Error detecting mood:', error);
    }
  };

  const handleStartCamera = async () => {
    try {
      setIsInitializing(true);
      setError(null);

      // Initialize MediaPipe (only happens once)
      await browserMoodDetector.initialize();

      setIsActive(true);
      setIsDetecting(true);
      
      // Connect WebSocket (optional - for multi-user features)
      websocketService.connect();
      websocketService.startDetection();
      
    } catch (err) {
      console.error('Failed to initialize:', err);
      setError('Failed to initialize mood detection. Please refresh and try again.');
    } finally {
      setIsInitializing(false);
    }
  };

  const handleStopCamera = () => {
    setIsActive(false);
    setIsDetecting(false);
    setFps(0);
    
    // Reset detector history
    browserMoodDetector.reset();
    
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Camera Feed
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Chip
            icon={<CloudOffIcon sx={{ fontSize: 16 }} />}
            label="100% Local"
            size="small"
            color="success"
            sx={{ fontWeight: 600 }}
          />
          {fps > 0 && (
            <Chip
              icon={<SpeedIcon sx={{ fontSize: 16 }} />}
              label={`${fps} FPS`}
              size="small"
              color="primary"
              sx={{ fontWeight: 600 }}
            />
          )}
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Alert severity="info" sx={{ mb: 2 }}>
        <strong>🚀 Performance Mode:</strong> Mood detection runs entirely in your browser - no server calls, no data usage!
      </Alert>

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
              ref={(ref) => {
                webcamRef.current = ref;
                videoRef.current = ref;
              }}
              audio={false}
              videoConstraints={{
                width: 640,
                height: 480,
                facingMode: 'user',
              }}
              onUserMediaError={handleUserMediaError}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
              }}
            />
            
            {/* Processing indicator */}
            <Box
              sx={{
                position: 'absolute',
                top: 8,
                right: 8,
                bgcolor: isDetecting ? 'success.main' : 'grey.700',
                color: 'white',
                px: 2,
                py: 0.5,
                borderRadius: 1,
                fontSize: '0.75rem',
                display: 'flex',
                alignItems: 'center',
                gap: 1,
              }}
            >
              <Box
                sx={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  bgcolor: isDetecting ? '#4CAF50' : '#666',
                  animation: isDetecting ? 'pulse 1s ease-in-out infinite' : 'none',
                  '@keyframes pulse': {
                    '0%, 100%': { opacity: 1 },
                    '50%': { opacity: 0.3 },
                  },
                }}
              />
              {isDetecting ? 'Detecting' : 'Paused'}
            </Box>

            {/* Performance stats */}
            {lastDetectionTime > 0 && (
              <Chip
                label={`${lastDetectionTime.toFixed(0)}ms`}
                size="small"
                sx={{
                  position: 'absolute',
                  top: 8,
                  left: 8,
                  bgcolor: 'rgba(0,0,0,0.7)',
                  color: 'white',
                  fontSize: '0.7rem',
                }}
              />
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
            {isInitializing && (
              <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                <CircularProgress size={20} />
                <Typography variant="caption">Loading MediaPipe...</Typography>
              </Box>
            )}
          </Box>
        )}
      </Box>

      <Box sx={{ display: 'flex', gap: 2 }}>
        <Button
          variant="contained"
          startIcon={isInitializing ? <CircularProgress size={20} /> : <VideocamIcon />}
          onClick={handleStartCamera}
          disabled={isActive || isInitializing}
          fullWidth
        >
          {isInitializing ? 'Initializing...' : 'Start Detection'}
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
        {isDetecting 
          ? `🟢 Processing ${Math.round(1000/DETECTION_INTERVAL)} frames per second • 100% client-side` 
          : '🔒 All processing happens in your browser - no data leaves your device'}
      </Typography>
    </Box>
  );
}

export default VideoFeed;