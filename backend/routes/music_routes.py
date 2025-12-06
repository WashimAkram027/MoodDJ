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
        # Get user_id from session (optional - fallback to global if not provided)
        user_id = session.get('user_id')

        data = request.json
        mood = data.get('mood', 'neutral')
        limit = data.get('limit', 30)

        songs = spotify_service.get_songs_for_mood(mood, limit, user_id)

        return jsonify({
            'success': True,
            'mood': mood,
            'songs': songs,
            'count': len(songs),
            'user_specific': user_id is not None
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


@music_bp.route('/pause', methods=['POST'])
def pause_playback():
    """Pause current playback"""
    try:
        sp_client, error = get_spotify_client()
        if error:
            return error

        data = request.json or {}
        device_id = data.get('device_id')

        result = spotify_service.pause_playback(device_id, sp_client)

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        print(f"Error pausing playback: {e}")
        return jsonify({'error': str(e)}), 500


@music_bp.route('/resume', methods=['POST'])
def resume_playback():
    """Resume paused playback"""
    try:
        sp_client, error = get_spotify_client()
        if error:
            return error

        data = request.json or {}
        device_id = data.get('device_id')

        result = spotify_service.resume_playback(device_id, sp_client)

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400

    except Exception as e:
        print(f"Error resuming playback: {e}")
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

@music_bp.route('/sync/status', methods=['GET'])
def get_sync_status():
    """Check if user has synced their Spotify library"""
    try:
        from config.database import execute_query

        # Get user_id from session
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not authenticated. Please log in.'}), 401

        # Check how many songs the user has synced
        query = """
            SELECT COUNT(DISTINCT us.song_id) as song_count
            FROM user_songs us
            INNER JOIN users u ON us.user_id = u.user_id
            WHERE u.spotify_id = %s
        """
        result = execute_query(query, (user_id,), fetch=True)
        song_count = result[0]['song_count'] if result else 0

        return jsonify({
            'success': True,
            'synced': song_count > 0,
            'song_count': song_count,
            'needs_sync': song_count == 0
        }), 200

    except Exception as e:
        print(f"Error checking sync status: {e}")
        return jsonify({'error': str(e)}), 500


@music_bp.route('/sync', methods=['POST'])
def sync_user_library():
    """Sync user's Spotify library to database"""
    try:
        # Get authenticated Spotify client from session
        sp_client, error = get_spotify_client()
        if error:
            return error

        # Get user_id from session
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not authenticated. Please log in.'}), 401

        data = request.json or {}
        limit = data.get('limit', 25)

        result = spotify_service.fetch_and_store_user_tracks(limit, sp_client, user_id)

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


@music_bp.route('/reset', methods=['POST'])
def reset_library():
    """Reset user's synced library - delete all their synced songs"""
    try:
        from config.database import execute_query

        # Get user_id from session
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401

        # Delete user's song links from user_songs table
        delete_user_songs = """
            DELETE us FROM user_songs us
            INNER JOIN users u ON us.user_id = u.user_id
            WHERE u.spotify_id = %s
        """
        execute_query(delete_user_songs, (user_id,))

        # Clean up orphaned songs (songs not linked to any user)
        delete_orphaned = """
            DELETE FROM songs
            WHERE song_id NOT IN (SELECT DISTINCT song_id FROM user_songs)
        """
        execute_query(delete_orphaned)

        return jsonify({
            'success': True,
            'message': 'Library reset successfully'
        }), 200

    except Exception as e:
        print(f"Error resetting library: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500