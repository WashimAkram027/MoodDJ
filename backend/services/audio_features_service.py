"""
Audio Features Service
Primary source for fetching audio features from RapidAPI SoundNet Track Analysis API

NOTE: Spotify's audio_features API is completely deprecated and no longer used.
This service is the ONLY source for audio features in MoodDJ.

Usage:
    from services.audio_features_service import AudioFeaturesService

    service = AudioFeaturesService()
    features = service.get_audio_features(spotify_track_id)

Returns:
    Audio features dict with valence, energy, tempo (0.0-1.0 scale for valence/energy)
    or None if fetch failed
"""

import os
import time
import requests
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()


class AudioFeaturesService:
    """Service for fetching audio features from RapidAPI SoundNet"""

    def __init__(self):
        """Initialize the audio features service"""
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY")
        self.rapidapi_host = os.getenv("RAPIDAPI_HOST", "track-analysis.p.rapidapi.com")
        self.enabled = bool(self.rapidapi_key and self.rapidapi_key != "your_rapidapi_key_here")

        if not self.enabled:
            print("[WARN] AudioFeaturesService: RAPIDAPI_KEY not configured. Audio features will not be available.")

    def get_audio_features(self, track_id: str, retry_on_rate_limit: bool = True, retry_count: int = 0, max_retries: int = 3) -> Optional[Dict[str, float]]:
        """
        Fetch audio features for a Spotify track from RapidAPI SoundNet

        Args:
            track_id: Spotify track ID (e.g., "7s25THrKz86DM225dOYwnr")
            retry_on_rate_limit: If True, automatically retry with exponential backoff
            retry_count: Current retry attempt (internal use)
            max_retries: Maximum number of retries on rate limit

        Returns:
            dict with 'valence', 'energy', 'tempo' keys, or None if failed
            Example: {'valence': 0.720, 'energy': 0.850, 'tempo': 128.0}
        """
        if not self.enabled:
            return None

        headers = {
            "x-rapidapi-key": self.rapidapi_key,
            "x-rapidapi-host": self.rapidapi_host
        }

        url = f"https://{self.rapidapi_host}/pktx/spotify/{track_id}"

        try:
            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                return self._parse_response(response.json(), track_id)

            elif response.status_code == 404:
                print(f"[WARN] Track {track_id} not found in SoundNet database")
                return None

            elif response.status_code == 429:
                if retry_on_rate_limit and retry_count < max_retries:
                    retry_after = response.headers.get('Retry-After', '3')
                    wait_time = int(retry_after) if retry_after.isdigit() else 3

                    # Exponential backoff: base wait time * 2^retry_count
                    backoff_time = wait_time * (2 ** retry_count)
                    print(f"[WARN] Rate limited (attempt {retry_count + 1}/{max_retries}). Waiting {backoff_time}s...")
                    time.sleep(backoff_time)

                    # Retry with incremented count
                    return self.get_audio_features(track_id, retry_on_rate_limit=True, retry_count=retry_count + 1, max_retries=max_retries)
                else:
                    print(f"[ERROR] Rate limit exceeded after {max_retries} retries")
                    return None

            elif response.status_code == 403:
                print(f"[ERROR] RapidAPI access forbidden (403). Check API key and subscription.")
                return None

            else:
                print(f"[ERROR] SoundNet API returned status {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            print(f"[ERROR] Request timeout for track {track_id}")
            return None

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request failed for track {track_id}: {e}")
            return None

        except Exception as e:
            print(f"[ERROR] Unexpected error for track {track_id}: {e}")
            return None

    def _parse_response(self, data: dict, track_id: str) -> Optional[Dict[str, float]]:
        """
        Parse SoundNet API response and convert to Spotify-compatible format

        Args:
            data: Raw JSON response from SoundNet API
            track_id: Track ID for logging purposes

        Returns:
            Normalized features dict or None if data is incomplete
        """
        try:
            # SoundNet returns: tempo (BPM), energy (0-100), happiness (0-100)
            # We convert to Spotify format: tempo (BPM), energy (0.0-1.0), valence (0.0-1.0)
            features = {
                'tempo': float(data.get('tempo')) if data.get('tempo') is not None else None,
                'energy': data.get('energy') / 100.0 if data.get('energy') is not None else None,
                'valence': data.get('happiness') / 100.0 if data.get('happiness') is not None else None
            }

            # Validate all fields are present
            if all(v is not None for v in features.values()):
                return features
            else:
                print(f"[WARN] Incomplete data from SoundNet for track {track_id}: {features}")
                return None

        except (ValueError, TypeError) as e:
            print(f"[ERROR] Failed to parse SoundNet response for track {track_id}: {e}")
            return None

    def batch_get_audio_features(self, track_ids: list, delay_between_requests: float = 1.0) -> Dict[str, Optional[Dict[str, float]]]:
        """
        Fetch audio features for multiple tracks with rate limiting

        Args:
            track_ids: List of Spotify track IDs
            delay_between_requests: Seconds to wait between API calls (default 1.0)

        Returns:
            Dictionary mapping track_id -> features (or None if failed)
            Example: {'track1': {'valence': 0.7, ...}, 'track2': None, ...}
        """
        if not self.enabled:
            return {track_id: None for track_id in track_ids}

        results = {}
        total = len(track_ids)

        print(f"[INFO] Fetching audio features for {total} tracks...")

        for idx, track_id in enumerate(track_ids, 1):
            print(f"[{idx}/{total}] Fetching features for {track_id}...", end=' ')

            features = self.get_audio_features(track_id)
            results[track_id] = features

            if features:
                print(f"✓ (valence: {features['valence']:.3f}, energy: {features['energy']:.3f}, tempo: {features['tempo']:.1f})")
            else:
                print("✗ Failed")

            # Rate limiting (skip delay on last track)
            if idx < total:
                time.sleep(delay_between_requests)

        success_count = sum(1 for v in results.values() if v is not None)
        print(f"[INFO] Batch complete: {success_count}/{total} successful ({success_count/total*100:.1f}%)")

        return results

    def is_enabled(self) -> bool:
        """Check if the service is properly configured"""
        return self.enabled


# Singleton instance for easy import
audio_features_service = AudioFeaturesService()
