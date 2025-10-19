from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Enable CORS for React frontend
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize SocketIO with CORS
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000", async_mode='threading')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import routes
from routes.auth_routes import auth_bp
from routes.mood_routes import mood_bp
from routes.music_routes import music_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(mood_bp, url_prefix='/api/mood')
app.register_blueprint(music_bp, url_prefix='/api/music')

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    logger.info(f'Client connected: {request.sid}')
    emit('connection_response', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f'Client disconnected: {request.sid}')

@socketio.on('mood_update')
def handle_mood_update(data):
    """Handle mood updates from frontend"""
    logger.info(f'Mood update received: {data}')
    # Broadcast to all connected clients
    emit('mood_changed', data, broadcast=True)

@socketio.on('start_detection')
def handle_start_detection(data):
    """Start mood detection"""
    logger.info('Starting mood detection')
    emit('detection_started', {'status': 'started'})

@socketio.on('stop_detection')
def handle_stop_detection(data):
    """Stop mood detection"""
    logger.info('Stopping mood detection')
    emit('detection_stopped', {'status': 'stopped'})

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'MoodDJ Backend is running'
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info('Starting MoodDJ Backend Server...')
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)