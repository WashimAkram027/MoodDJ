from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from flask_session import Session
from dotenv import load_dotenv
import os
import logging
from datetime import timedelta
import redis

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Secret key for session encryption
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Session configuration - support both filesystem and Redis
session_type = os.getenv('SESSION_TYPE', 'filesystem')
app.config['SESSION_TYPE'] = session_type

if session_type == 'redis':
    # Production: Use Redis for session storage (required for ECS Fargate)
    redis_url = os.getenv('SESSION_REDIS', 'redis://localhost:6379')
    app.config['SESSION_REDIS'] = redis.from_url(redis_url)
    logger = logging.getLogger(__name__)
    logger.info(f"Using Redis session storage: {redis_url}")
else:
    # Development: Use filesystem session storage
    app.config['SESSION_TYPE'] = 'filesystem'

app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Sessions last 7 days
app.config['SESSION_COOKIE_NAME'] = 'mooddj_session'
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')  # CSRF protection
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'  # HTTPS only in production
# Don't set SESSION_COOKIE_DOMAIN - let it default to current domain
# This ensures cookies work properly for the requesting domain

# Initialize Flask-Session for server-side sessions
Session(app)

# Enable CORS for React frontend with credentials support
CORS(app, resources={
    r"/*": {
        "origins": [
            os.getenv('FRONTEND_URL', 'http://127.0.0.1:3000'),
            "http://localhost:3000",
            "http://127.0.0.1:3000"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True  # Required for session cookies
    }
})

# Initialize SocketIO with CORS
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000", "http://127.0.0.1:3000"], async_mode='threading')

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

# Health check endpoint (for ALB/ECS health checks)
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for load balancer"""
    return jsonify({'status': 'healthy', 'service': 'mooddj-backend'}), 200

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

# Startup hook for auto-sync
def check_and_sync_library():
    """
    Check if database is empty and auto-sync Spotify library if needed
    This runs once when the backend starts
    """
    try:
        from config.database import execute_query
        from services.spotify_service import SpotifyService

        # Check if songs table has any records
        result = execute_query("SELECT COUNT(*) as count FROM songs", fetch=True)
        song_count = result[0]['count'] if result else 0

        logger.info(f"Database check: Found {song_count} songs in database")

        # Auto-sync only if database is empty
        if song_count == 0:
            logger.info("="*70)
            logger.info("🔄 DATABASE IS EMPTY - Starting auto-sync...")
            logger.info("="*70)

            # Initialize Spotify service and trigger sync
            spotify_service = SpotifyService()
            sync_result = spotify_service.fetch_and_store_user_tracks(limit=50)

            if sync_result['success']:
                logger.info("="*70)
                logger.info("✅ AUTO-SYNC COMPLETE!")
                logger.info(f"   Total tracks: {sync_result['total_processed']}")
                logger.info(f"   With features: {sync_result['with_features']}")
                logger.info(f"   Without features: {sync_result['without_features']}")
                logger.info("="*70)
            else:
                logger.error(f"❌ Auto-sync failed: {sync_result.get('error', 'Unknown error')}")
                logger.info("   You can manually sync by calling POST /api/music/sync")

        else:
            logger.info(f"✅ Database already populated with {song_count} songs")
            logger.info("   Skipping auto-sync. Use POST /api/music/sync to refresh.")

    except Exception as e:
        logger.error(f"❌ Error during startup sync check: {e}")
        logger.info("   Backend will continue without auto-sync")
        logger.info("   You can manually sync by calling POST /api/music/sync")

if __name__ == '__main__':
    logger.info('Starting MoodDJ Backend Server...')
    logger.info('-'*70)

    # Run startup check and sync if needed
    check_and_sync_library()

    logger.info('-'*70)
    logger.info('🚀 Server ready! Running on http://0.0.0.0:5000')
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)