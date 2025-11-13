import logging
import os
import time
from typing import List, Optional

import requests
import spotipy
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

from config.database import execute_query
from services.audio_features_service import AudioFeaturesService

load_dotenv()

class SpotifyService:
    """Handles all Spotify API interactions with web-based OAuth support"""

    def __init__(self):
        self.sp = None  # Will be created per-request from session token

        # Spotify OAuth configuration
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:5000/api/auth/callback")
        self.scope = "user-library-read playlist-modify-private user-modify-playback-state user-read-playback-state"

        # Audio features service (RapidAPI SoundNet - primary source)
        self.audio_features_service = AudioFeaturesService()

        if not self.audio_features_service.is_enabled():
            print("[WARN] AudioFeaturesService not configured. Audio features will not be available.")
            print("[WARN] Add RAPIDAPI_KEY to .env to enable audio features.")

    def get_oauth_manager(self):
        """Get SpotifyOAuth instance for web OAuth flow"""
        return SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            cache_path=None,  # No file cache for web OAuth
            show_dialog=True  # Always show Spotify auth dialog
        )

    def get_auth_url(self):
        """
        Generate Spotify authorization URL for OAuth flow

        Returns:
            str: Authorization URL to redirect user to
        """
        oauth = self.get_oauth_manager()
        auth_url = oauth.get_authorize_url()
        return auth_url

    def exchange_code_for_token(self, code: str):
        """
        Exchange authorization code for access token

        Args:
            code: Authorization code from Spotify callback

        Returns:
            dict: Token information containing access_token, refresh_token, expires_at
        """
        try:
            oauth = self.get_oauth_manager()
            token_info = oauth.get_access_token(code, as_dict=True, check_cache=False)
            return token_info
        except Exception as e:
            print(f"[ERROR] Failed to exchange code for token: {e}")
            return None

    def refresh_access_token(self, refresh_token: str):
        """
        Refresh an expired access token

        Args:
            refresh_token: Refresh token from previous authorization

        Returns:
            dict: New token information
        """
        try:
            oauth = self.get_oauth_manager()
            token_info = oauth.refresh_access_token(refresh_token)
            return token_info
        except Exception as e:
            print(f"[ERROR] Failed to refresh token: {e}")
            return None

    def is_token_expired(self, token_info: dict) -> bool:
        """
        Check if access token is expired

        Args:
            token_info: Token information dict with expires_at timestamp

        Returns:
            bool: True if token is expired
        """
        if not token_info or 'expires_at' not in token_info:
            return True

        import time
        return token_info['expires_at'] < int(time.time())

    def create_spotify_client(self, token_info: dict):
        """
        Create Spotify client from token information

        Args:
            token_info: Token information from session

        Returns:
            spotipy.Spotify: Authenticated Spotify client or None if failed
        """
        if not token_info:
            return None

        # Refresh token if expired
        if self.is_token_expired(token_info):
            print("[INFO] Token expired, refreshing...")
            token_info = self.refresh_access_token(token_info.get('refresh_token'))
            if not token_info:
                return None

        try:
            sp = spotipy.Spotify(auth=token_info['access_token'])
            return sp
        except Exception as e:
            print(f"[ERROR] Failed to create Spotify client: {e}")
            return None
    
    def get_user_profile(self, sp_client=None):
        """
        Get current user's Spotify profile

        Args:
            sp_client: Spotify client instance (from session token)

        Returns:
            dict: User profile information
        """
        if not sp_client:
            return None

        try:
            return sp_client.current_user()
        except Exception as e:
            print(f"[ERROR] Error fetching user profile: {e}")
            return None
    
    def get_songs_for_mood(self, mood, limit=30):
        """Get songs from database that match the mood"""
        try:
            # Mood to audio feature mappings
            mood_params = {
                'happy': {'valence': (0.6, 1.0), 'energy': (0.5, 1.0), 'tempo': (100, 180)},
                'sad': {'valence': (0.0, 0.4), 'energy': (0.2, 0.5), 'tempo': (60, 100)},
                'excited': {'valence': (0.7, 1.0), 'energy': (0.7, 1.0), 'tempo': (120, 200)},
                'calm': {'valence': (0.3, 0.7), 'energy': (0.2, 0.5), 'tempo': (60, 100)},
                'neutral': {'valence': (0.4, 0.7), 'energy': (0.4, 0.7), 'tempo': (80, 130)},
                'angry': {'valence': (0.0, 0.4), 'energy': (0.6, 1.0), 'tempo': (120, 180)},
                'surprised': {'valence': (0.5, 1.0), 'energy': (0.6, 1.0), 'tempo': (110, 180)}
            }
            
            params = mood_params.get(mood, mood_params['neutral'])
            
            query = """
                SELECT * FROM songs 
                WHERE valence BETWEEN %s AND %s
                AND energy BETWEEN %s AND %s
                AND tempo BETWEEN %s AND %s
                ORDER BY RAND()
                LIMIT %s
            """
            
            songs = execute_query(
                query,
                (
                    params['valence'][0], params['valence'][1],
                    params['energy'][0], params['energy'][1],
                    params['tempo'][0], params['tempo'][1],
                    limit
                ),
                fetch=True
            )
            
            return songs
        except Exception as e:
            print(f"[ERROR] Error fetching songs for mood: {e}")
            return []
    
    def fetch_and_store_user_tracks(self, limit=50, sp_client=None):
        """
        Fetch user's saved tracks and store them with audio features from RapidAPI

        Args:
            limit: Number of tracks to fetch
            sp_client: Spotify client instance (from session token)

        Flow:
        1. Get track metadata from Spotify (id, title, artist, album, duration)
        2. Fetch audio features from RapidAPI SoundNet (valence, energy, tempo)
        3. Store complete record in database

        Note: Spotify's audio_features API is deprecated and not used.
        """
        if not sp_client:
            return {'success': False, 'error': 'No Spotify client provided'}

        try:
            offset = 0
            total_processed = 0
            tracks_with_features = 0
            tracks_without_features = 0

            print(f"[INFO] Starting sync of {limit} tracks...")
            print(f"[INFO] Audio features source: RapidAPI SoundNet")

            while offset < limit:
                # Fetch tracks metadata from Spotify
                results = sp_client.current_user_saved_tracks(limit=min(50, limit - offset), offset=offset)

                if not results['items']:
                    break

                print(f"[INFO] Processing batch: tracks {offset + 1} to {offset + len(results['items'])}")

                # Process each track: metadata + audio features
                for idx, item in enumerate(results['items'], 1):
                    track = item['track']
                    track_id = track['id']
                    title = track['name']
                    artist = track['artists'][0]['name'] if track['artists'] else 'Unknown'
                    album = track['album']['name']
                    duration_ms = track['duration_ms']

                    print(f"  [{offset + idx}] {title} by {artist}...", end=' ')

                    # Fetch audio features from RapidAPI (primary and only source)
                    features = self.audio_features_service.get_audio_features(track_id)

                    # Store track in database
                    query = """
                        INSERT INTO songs (spotify_song_id, title, artist, album, duration_ms, valence, energy, tempo)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            title=VALUES(title),
                            artist=VALUES(artist),
                            album=VALUES(album),
                            duration_ms=VALUES(duration_ms),
                            valence=VALUES(valence),
                            energy=VALUES(energy),
                            tempo=VALUES(tempo)
                    """

                    execute_query(query, (
                        track_id,
                        title,
                        artist,
                        album,
                        duration_ms,
                        features['valence'] if features else None,
                        features['energy'] if features else None,
                        features['tempo'] if features else None
                    ))

                    total_processed += 1

                    if features:
                        tracks_with_features += 1
                        print(f"✓ (v:{features['valence']:.2f}, e:{features['energy']:.2f}, t:{features['tempo']:.0f})")
                    else:
                        tracks_without_features += 1
                        print(f"✗ No features")

                    # Rate limiting: 1 second between RapidAPI calls
                    time.sleep(1.0)

                offset += len(results['items'])
                print(f"[INFO] Batch complete. Progress: {total_processed}/{limit}")

            print(f"[INFO] Sync complete!")
            print(f"[INFO] Total: {total_processed}, With features: {tracks_with_features}, Without: {tracks_without_features}")

            return {
                'success': True,
                'total_processed': total_processed,
                'with_features': tracks_with_features,
                'without_features': tracks_without_features
            }
        except Exception as e:
            print(f"[ERROR] Error fetching tracks: {e}")
            return {'success': False, 'error': str(e)}
    
    def play_track(self, track_id, device_id=None, sp_client=None):
        """
        Play a specific track

        Args:
            track_id: Spotify track ID
            device_id: Optional device ID to play on
            sp_client: Spotify client instance (from session token)

        Returns:
            dict: Success status
        """
        if not sp_client:
            return {'success': False, 'error': 'Not authenticated'}

        try:
            if not device_id:
                devices = sp_client.devices()
                if devices['devices']:
                    device_id = devices['devices'][0]['id']
                else:
                    return {'success': False, 'error': 'No active devices found'}

            sp_client.start_playback(
                device_id=device_id,
                uris=[f"spotify:track:{track_id}"]
            )
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_current_playback(self, sp_client=None):
        """
        Get current playback state

        Args:
            sp_client: Spotify client instance (from session token)

        Returns:
            dict: Playback information
        """
        if not sp_client:
            return None

        try:
            playback = sp_client.current_playback()
            if playback and playback.get('item'):
                return {
                    'is_playing': playback['is_playing'],
                    'track': {
                        'id': playback['item']['id'],
                        'title': playback['item']['name'],
                        'artist': playback['item']['artists'][0]['name'],
                        'album': playback['item']['album']['name'],
                        'album_art': playback['item']['album']['images'][0]['url'] if playback['item']['album']['images'] else None,
                        'duration_ms': playback['item']['duration_ms'],
                        'progress_ms': playback['progress_ms']
                    }
                }
            return None
        except Exception as e:
            print(f"[ERROR] Error getting playback: {e}")
            return None

    def create_mood_playlist(self, user_id, mood, track_ids, sp_client=None):
        """
        Create a Spotify playlist for a mood

        Args:
            user_id: Spotify user ID
            mood: Mood name
            track_ids: List of track IDs to add
            sp_client: Spotify client instance (from session token)

        Returns:
            dict: Success status and playlist info
        """
        if not sp_client:
            return {'success': False, 'error': 'Not authenticated'}

        try:
            playlist_name = f"MoodDJ - {mood.capitalize()} Vibes"
            playlist = sp_client.user_playlist_create(
                user_id,
                playlist_name,
                public=False,
                description=f"Auto-generated playlist for {mood} mood by MoodDJ"
            )

            # Add tracks in batches of 100 (Spotify limit)
            track_uris = [f"spotify:track:{tid}" for tid in track_ids[:100]]

            if track_uris:
                sp_client.playlist_add_items(playlist['id'], track_uris)

            return {
                'success': True,
                'playlist_id': playlist['id'],
                'playlist_url': playlist['external_urls']['spotify']
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
