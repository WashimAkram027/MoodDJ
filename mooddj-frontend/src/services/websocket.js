import io from 'socket.io-client';

const WS_URL = process.env.REACT_APP_WS_URL || 'http://localhost:5000';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
  }

  connect() {
    if (this.socket) {
      return;
    }

    this.socket = io(WS_URL, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    this.socket.on('connect', () => {
      this.isConnected = true;
    });

    this.socket.on('disconnect', () => {
      this.isConnected = false;
    });

    this.socket.on('connection_response', () => {
      // Connection established
    });

    return this.socket;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }

  // Send mood update
  sendMoodUpdate(mood, confidence) {
    if (this.socket && this.isConnected) {
      this.socket.emit('mood_update', { mood, confidence });
    }
  }

  // Listen for mood changes
  onMoodChanged(callback) {
    if (this.socket) {
      this.socket.on('mood_changed', callback);
    }
  }

  // Start detection
  startDetection() {
    if (this.socket && this.isConnected) {
      this.socket.emit('start_detection', {});
    }
  }

  // Stop detection
  stopDetection() {
    if (this.socket && this.isConnected) {
      this.socket.emit('stop_detection', {});
    }
  }

  getSocket() {
    return this.socket;
  }
}

// Export singleton instance
export default new WebSocketService();