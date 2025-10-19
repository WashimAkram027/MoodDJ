from flask import Blueprint, request, jsonify
from services.spotify_service import SpotifyService

music_bp = Blueprint('music', __name__)
spotify_service = SpotifyService()

@music_bp.route('/recommend', methods=['POST'])
def recommend_songs():
    """Get song recommendations based on mood"""
    try:
        data = request.json
        mood = data.get('mood', 'neutral')
        limit = data.get('limit', 30)
        
        songs = spotify_service.get_songs_for_mood(mood, limit)
        
        return jsonify({
            'success': True,
            'mood': mood,
            'songs': songs,
            'count': len(songs)
        }), 200
        
    except Exception as e:
        print(f"Error recommending songs: {e}")
        return jsonify({'error': str(e)}), 500

@music_bp.route('/play', methods=['POST'])
def play_track():
    """Play a specific track"""
    try:
        data = request.json
        track_id = data.get('track_id')
        device_id = data.get('device_id')
        
        if not track_id:
            return jsonify({'error': 'track_id is required'}), 400
        
        result = spotify_service.play_track(track_id, device_id)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        print(f"Error playing track: {e}")
        return jsonify({'error': str(e)}), 500

@music_bp.route('/current', methods=['GET'])
def get_current_track():
    """Get currently playing track"""
    try:
        playback = spotify_service.get_current_playback()
        
        if playback:
            return jsonify({
                'success': True,
                'playback': playback
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'No track currently playing'
            }), 200
            
    except Exception as e:
        print(f"Error getting current track: {e}")
        return jsonify({'error': str(e)}), 500

@music_bp.route('/sync', methods=['POST'])
def sync_user_library():
    """Sync user's Spotify library to database"""
    try:
        data = request.json
        limit = data.get('limit', 50)
        
        result = spotify_service.fetch_and_store_user_tracks(limit)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        print(f"Error syncing library: {e}")
        return jsonify({'error': str(e)}), 500

@music_bp.route('/playlist/create', methods=['POST'])
def create_playlist():
    """Create a mood-based playlist"""
    try:
        data = request.json
        user_id = data.get('user_id')
        mood = data.get('mood')
        track_ids = data.get('track_ids', [])
        
        if not user_id or not mood:
            return jsonify({'error': 'user_id and mood are required'}), 400
        
        result = spotify_service.create_mood_playlist(user_id, mood, track_ids)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        print(f"Error creating playlist: {e}")
        return jsonify({'error': str(e)}), 500