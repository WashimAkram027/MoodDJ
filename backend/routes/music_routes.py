from flask import Blueprint, request, jsonify, session
from services.spotify_service import SpotifyService

music_bp = Blueprint('music', __name__)
spotify_service = SpotifyService()


def get_spotify_client():
    """
    Helper function to get authenticated Spotify client from session

    Returns:
        tuple: (sp_client, error_response)
        - sp_client: Authenticated Spotify client or None
        - error_response: Error dict and status code if auth failed, or None
    """
    token_info = session.get('spotify_token_info')

    if not token_info:
        return None, (jsonify({'error': 'Not authenticated. Please connect with Spotify.'}), 401)

    # Create Spotify client (automatically refreshes token if expired)
    sp_client = spotify_service.create_spotify_client(token_info)

    if not sp_client:
        return None, (jsonify({'error': 'Failed to create Spotify client. Please re-authenticate.'}), 401)

    # Update session with refreshed token if it was refreshed
    if not spotify_service.is_token_expired(token_info):
        session['spotify_token_info'] = token_info

    return sp_client, None

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
        # Get authenticated Spotify client from session
        sp_client, error = get_spotify_client()
        if error:
            return error

        data = request.json
        track_id = data.get('track_id')
        device_id = data.get('device_id')

        if not track_id:
            return jsonify({'error': 'track_id is required'}), 400

        result = spotify_service.play_track(track_id, device_id, sp_client)

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
        # Get authenticated Spotify client from session
        sp_client, error = get_spotify_client()
        if error:
            return error

        playback = spotify_service.get_current_playback(sp_client)

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
        # Get authenticated Spotify client from session
        sp_client, error = get_spotify_client()
        if error:
            return error

        data = request.json or {}
        limit = data.get('limit', 50)

        result = spotify_service.fetch_and_store_user_tracks(limit, sp_client)

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
        # Get authenticated Spotify client from session
        sp_client, error = get_spotify_client()
        if error:
            return error

        data = request.json
        user_id = data.get('user_id') or session.get('user_id')  # Get from session if not provided
        mood = data.get('mood')
        track_ids = data.get('track_ids', [])

        if not user_id or not mood:
            return jsonify({'error': 'user_id and mood are required'}), 400

        result = spotify_service.create_mood_playlist(user_id, mood, track_ids, sp_client)

        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400

    except Exception as e:
        print(f"Error creating playlist: {e}")
        return jsonify({'error': str(e)}), 500