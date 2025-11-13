from flask import Blueprint, request, jsonify, session, redirect
import os
from services.spotify_service import SpotifyService
from config.database import execute_query

auth_bp = Blueprint('auth', __name__)
spotify_service = SpotifyService()


# ============================================================================
# OAuth Flow Endpoints
# ============================================================================

@auth_bp.route('/login', methods=['GET'])
def login():
    """
    Initiate Spotify OAuth flow

    Returns authorization URL for user to be redirected to Spotify login
    """
    try:
        auth_url = spotify_service.get_auth_url()
        return jsonify({
            'success': True,
            'auth_url': auth_url
        }), 200
    except Exception as e:
        print(f"[ERROR] Failed to generate auth URL: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to initiate authentication'
        }), 500


@auth_bp.route('/callback', methods=['GET'])
def callback():
    """
    Handle Spotify OAuth callback

    Exchanges authorization code for access token and stores in session
    """
    try:
        # Get authorization code from query params
        code = request.args.get('code')
        error = request.args.get('error')

        if error:
            print(f"[ERROR] OAuth error: {error}")
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            return redirect(f"{frontend_url}/?error=auth_failed")

        if not code:
            return jsonify({
                'success': False,
                'error': 'No authorization code provided'
            }), 400

        # Exchange code for token
        token_info = spotify_service.exchange_code_for_token(code)

        if not token_info:
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            return redirect(f"{frontend_url}/?error=token_exchange_failed")

        # Store token in session
        session.permanent = True  # Make session last beyond browser close
        session['spotify_token_info'] = token_info

        # Get user profile and store in session
        sp_client = spotify_service.create_spotify_client(token_info)
        if sp_client:
            profile = spotify_service.get_user_profile(sp_client)
            if profile:
                session['user_id'] = profile['id']
                session['display_name'] = profile.get('display_name', 'User')

                # Store user in database (optional)
                try:
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
                except Exception as db_error:
                    print(f"[WARN] Failed to store user in database: {db_error}")

        # Redirect to frontend dashboard
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return redirect(f"{frontend_url}/dashboard")

    except Exception as e:
        print(f"[ERROR] OAuth callback error: {e}")
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return redirect(f"{frontend_url}/?error=auth_error")


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Logout user by clearing session
    """
    try:
        session.clear()
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
    except Exception as e:
        print(f"[ERROR] Logout error: {e}")
        return jsonify({
            'success': False,
            'error': 'Logout failed'
        }), 500


@auth_bp.route('/status', methods=['GET'])
def status():
    """
    Check authentication status

    Returns whether user is authenticated and their profile info
    """
    try:
        token_info = session.get('spotify_token_info')
        user_id = session.get('user_id')

        if not token_info or not user_id:
            return jsonify({
                'authenticated': False
            }), 200

        # Check if token is expired and refresh if needed
        if spotify_service.is_token_expired(token_info):
            print("[INFO] Token expired, refreshing...")
            new_token_info = spotify_service.refresh_access_token(token_info.get('refresh_token'))

            if new_token_info:
                session['spotify_token_info'] = new_token_info
                token_info = new_token_info
            else:
                # Refresh failed, clear session
                session.clear()
                return jsonify({
                    'authenticated': False
                }), 200

        return jsonify({
            'authenticated': True,
            'user': {
                'id': user_id,
                'display_name': session.get('display_name', 'User')
            }
        }), 200

    except Exception as e:
        print(f"[ERROR] Status check error: {e}")
        return jsonify({
            'authenticated': False
        }), 200


# ============================================================================
# Legacy Endpoints (kept for compatibility)
# ============================================================================

@auth_bp.route('/spotify', methods=['GET'])
def spotify_auth():
    """Get Spotify user profile (legacy endpoint - requires existing session)"""
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