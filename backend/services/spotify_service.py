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

load_dotenv()

class SpotifyService:
    """Handles all Spotify API interactions"""

    def __init__(self):
        self.sp = None
        self._init_spotify()

        # SoundNet API configuration (fallback for audio features)
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY")
        self.rapidapi_host = os.getenv("RAPIDAPI_HOST", "track-analysis.p.rapidapi.com")
        self.soundnet_enabled = bool(self.rapidapi_key and self.rapidapi_key != "your_rapidapi_key_here")

    def _fetch_audio_features_batch(self, track_ids: List[Optional[str]]) -> List[Optional[dict]]:
        """
        Fetch audio features for a batch of track IDs.

        Spotify's audio feature/analysis endpoints can return 403 if the app
        has not been granted access yet. We treat those as recoverable so the
        sync process can continue without aborting entirely.
        """
        if not track_ids:
            return []

        try:
            return self.sp.audio_features(track_ids)
        except SpotifyException as err:
            if err.http_status not in (400, 403, 404, 429):
                raise

            print(f"[WARN] Bulk audio feature fetch failed ({err.http_status}). Falling back to per-track requests.")
            spotipy_logger = logging.getLogger("spotipy.client")
            previous_level = spotipy_logger.level
            spotipy_logger.setLevel(logging.CRITICAL)

            features: List[Optional[dict]] = []
            denied_tracks: List[str] = []
            missing_tracks: List[str] = []
            failed_tracks: List[str] = []

            try:
                for track_id in track_ids:
                    if not track_id:
                        features.append(None)
                        continue

                    try:
                        single = self.sp.audio_features([track_id])
                        features.append(single[0] if single else None)
                        continue
                    except SpotifyException as single_err:
                        if single_err.http_status == 429:
                            retry_after_header = None
                            if getattr(single_err, "headers", None):
                                retry_after_header = single_err.headers.get("Retry-After")
                            retry_after = int(retry_after_header or 1)
                            print(f"[WARN] Rate limited when fetching audio features for {track_id}. Retrying in {retry_after} seconds.")
                            time.sleep(retry_after)
                            try:
                                single_retry = self.sp.audio_features([track_id])
                                features.append(single_retry[0] if single_retry else None)
                                continue
                            except SpotifyException as retry_err:
                                failed_tracks.append(f"{track_id} (retry failed: {retry_err})")
                        elif single_err.http_status == 403:
                            denied_tracks.append(track_id)
                        elif single_err.http_status == 404:
                            missing_tracks.append(track_id)
                        else:
                            failed_tracks.append(f"{track_id} ({single_err})")

                    features.append(None)
            finally:
                spotipy_logger.setLevel(previous_level)

            if denied_tracks:
                print(f"[WARN] Spotify denied audio feature access for {len(denied_tracks)} track(s). "
                      f"First example: {denied_tracks[0]}")
            if missing_tracks:
                print(f"[WARN] Audio features unavailable (HTTP 404) for {len(missing_tracks)} track(s). "
                      f"First example: {missing_tracks[0]}")
            if failed_tracks:
                print(f"[WARN] Audio feature fetch failed for {len(failed_tracks)} track(s). "
                      f"First example: {failed_tracks[0]}")

            return features

    def _fetch_audio_features_from_soundnet(self, track_id: str) -> Optional[dict]:
        """
        Fetch audio features from SoundNet Track Analysis API (RapidAPI)
        This is used as a fallback when Spotify's audio_features endpoint fails

        Uses the /pktx/spotify/{trackID} endpoint which accepts Spotify Track IDs directly

        Args:
            track_id: Spotify track ID (e.g., "7s25THrKz86DM225dOYwnr")

        Returns:
            dict with 'valence', 'energy', 'tempo' or None if failed
        """
        if not self.soundnet_enabled:
            return None

        headers = {
            "x-rapidapi-key": self.rapidapi_key,
            "x-rapidapi-host": self.rapidapi_host
        }

        try:
            # Use the Spotify Track ID endpoint for accurate results
            url = f"https://{self.rapidapi_host}/pktx/spotify/{track_id}"
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Map SoundNet fields to Spotify equivalents
                # SoundNet returns: tempo, energy (0-100), happiness (0-100), danceability, etc.
                features = {
                    'valence': data.get('happiness') / 100.0 if data.get('happiness') is not None else None,  # Convert 0-100 to 0.0-1.0
                    'energy': data.get('energy') / 100.0 if data.get('energy') is not None else None,        # Convert 0-100 to 0.0-1.0
                    'tempo': float(data.get('tempo')) if data.get('tempo') is not None else None
                }

                # Validate all fields are present
                if all(v is not None for v in features.values()):
                    return features
                else:
                    print(f"[WARN] SoundNet returned incomplete data for track {track_id}: {features}")
                    return None

            elif response.status_code == 404:
                print(f"[WARN] Track {track_id} not found in SoundNet database")
                return None

            elif response.status_code == 429:
                print(f"[WARN] Rate limited by SoundNet API")
                return None

            else:
                print(f"[WARN] SoundNet API returned status {response.status_code} for track {track_id}")
                return None

        except Exception as e:
            print(f"[WARN] SoundNet API failed for track {track_id}: {e}")
            return None

    def _init_spotify(self):
        """Initialize Spotify client"""
        try:
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback"),
                scope="user-library-read playlist-modify-private user-modify-playback-state user-read-playback-state",
                open_browser=True,
                cache_path=".spotify_cache"
            ))
            print("[INFO] Spotify client initialized")
        except Exception as e:
            print(f"[ERROR] Error initializing Spotify: {e}")
    
    def get_user_profile(self):
        """Get current user's Spotify profile"""
        try:
            return self.sp.current_user()
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
    
    def fetch_and_store_user_tracks(self, limit=50):
        """Fetch user's saved tracks and store them with audio features"""
        try:
            offset = 0
            total_added = 0
            tracks_with_features = 0
            tracks_without_features = 0
            
            while offset < limit:
                results = self.sp.current_user_saved_tracks(limit=min(50, limit - offset), offset=offset)
                
                if not results['items']:
                    break
                
                # Collect track IDs for batch audio features request
                track_ids = []
                track_data = []
                
                for item in results['items']:
                    track = item['track']
                    track_data.append({
                        'id': track['id'],
                        'title': track['name'],
                        'artist': track['artists'][0]['name'],
                        'album': track['album']['name'],
                        'duration_ms': track['duration_ms']
                    })
                    track_ids.append(track['id'])
                
                # Get audio features for all tracks at once
                audio_features = self._fetch_audio_features_batch(track_ids)

                # Store tracks with their features (with SoundNet fallback)
                for track, features in zip(track_data, audio_features):
                    # If Spotify audio features failed, try SoundNet as fallback
                    if not features and self.soundnet_enabled:
                        print(f"[INFO] Spotify audio features unavailable for '{track['title']}', trying SoundNet...")
                        features = self._fetch_audio_features_from_soundnet(track['id'])
                        if features:
                            print(f"[INFO] SoundNet fallback successful! (valence: {features['valence']:.3f}, energy: {features['energy']:.3f}, tempo: {features['tempo']:.1f})")
                        else:
                            print(f"[WARN] SoundNet fallback also failed")

                    query = """
                        INSERT INTO songs (spotify_song_id, title, artist, album, duration_ms, valence, energy, tempo)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            valence=VALUES(valence),
                            energy=VALUES(energy),
                            tempo=VALUES(tempo)
                    """
                    execute_query(query, (
                        track['id'],
                        track['title'],
                        track['artist'],
                        track['album'],
                        track['duration_ms'],
                        features['valence'] if features else None,
                        features['energy'] if features else None,
                        features['tempo'] if features else None
                    ))

                    total_added += 1
                    if features:
                        tracks_with_features += 1
                    else:
                        tracks_without_features += 1
                
                offset += len(results['items'])
                # Be polite with Spotify API to avoid throttling
                time.sleep(0.2)
            
            return {
                'success': True,
                'total_processed': total_added,
                'with_features': tracks_with_features,
                'without_features': tracks_without_features
            }
        except Exception as e:
            print(f"[ERROR] Error fetching tracks: {e}")
            return {'success': False, 'error': str(e)}
    
    def play_track(self, track_id, device_id=None):
        """Play a specific track"""
        try:
            if not device_id:
                devices = self.sp.devices()
                if devices['devices']:
                    device_id = devices['devices'][0]['id']
                else:
                    return {'success': False, 'error': 'No active devices found'}
            
            self.sp.start_playback(
                device_id=device_id,
                uris=[f"spotify:track:{track_id}"]
            )
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_current_playback(self):
        """Get current playback state"""
        try:
            playback = self.sp.current_playback()
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
    
    def create_mood_playlist(self, user_id, mood, track_ids):
        """Create a Spotify playlist for a mood"""
        try:
            playlist_name = f"MoodDJ - {mood.capitalize()} Vibes"
            playlist = self.sp.user_playlist_create(
                user_id,
                playlist_name,
                public=False,
                description=f"Auto-generated playlist for {mood} mood by MoodDJ"
            )
            
            # Add tracks in batches of 100 (Spotify limit)
            track_uris = [f"spotify:track:{tid}" for tid in track_ids[:100]]
            
            if track_uris:
                self.sp.playlist_add_items(playlist['id'], track_uris)
            
            return {
                'success': True,
                'playlist_id': playlist['id'],
                'playlist_url': playlist['external_urls']['spotify']
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
