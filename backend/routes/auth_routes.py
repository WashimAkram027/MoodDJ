from flask import Blueprint, request, jsonify
from services.spotify_service import SpotifyService
from config.database import execute_query

auth_bp = Blueprint('auth', __name__)
spotify_service = SpotifyService()

@auth_bp.route('/spotify', methods=['GET'])
def spotify_auth():
    """Get Spotify user profile"""
    try:
        profile = spotify_service.get_user_profile()
        
        if profile:
            # Store or update user in database
            query = """
                INSERT INTO users (spotify_id, display_name, email)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    display_name = VALUES(display_name),
                    email = VALUES(email)
            """
            execute_query(query, (
                profile['id'],
                profile.get('display_name', 'User'),
                profile.get('email', '')
            ))
            
            return jsonify({
                'success': True,
                'user': {
                    'id': profile['id'],
                    'display_name': profile.get('display_name'),
                    'email': profile.get('email'),
                    'profile_image': profile['images'][0]['url'] if profile.get('images') else None
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Could not authenticate with Spotify'
            }), 401
            
    except Exception as e:
        print(f"Error in Spotify auth: {e}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get user profile"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        query = """
            SELECT user_id, spotify_id, display_name, email, created_at
            FROM users
            WHERE spotify_id = %s
        """
        
        user = execute_query(query, (user_id,), fetch=True)
        
        if user:
            return jsonify({
                'success': True,
                'user': user[0]
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
            
    except Exception as e:
        print(f"Error getting profile: {e}")
        return jsonify({'error': str(e)}), 500