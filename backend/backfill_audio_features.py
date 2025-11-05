"""
Backfill audio features for songs with NULL valence/energy/tempo
Uses SoundNet Track Analysis API via RapidAPI as workaround for deprecated Spotify endpoint

Usage:
    python backfill_audio_features.py

Requirements:
    - RAPIDAPI_KEY in .env file
    - mysql.connector (already installed)
    - requests library
"""

import mysql.connector
import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# RapidAPI Configuration
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "track-analysis.p.rapidapi.com"

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME', 'mooddj')
}


def get_audio_features_from_soundnet(track_id, verbose=False):
    """
    Fetch audio features from SoundNet Track Analysis API using Spotify Track ID

    Uses the /pktx/spotify/{trackID} endpoint for accurate results

    Args:
        track_id (str): Spotify track ID (e.g., "7s25THrKz86DM225dOYwnr")
        verbose (bool): Enable detailed logging

    Returns:
        dict: Audio features (tempo, energy, valence) or None if failed
    """
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    url = f"https://{RAPIDAPI_HOST}/pktx/spotify/{track_id}"

    if verbose:
        print(f"\n[DEBUG] API Request Details:")
        print(f"  URL: {url}")
        print(f"  Headers:")
        print(f"    x-rapidapi-key: {RAPIDAPI_KEY[:10]}...{RAPIDAPI_KEY[-5:]}")
        print(f"    x-rapidapi-host: {RAPIDAPI_HOST}")
        print(f"  Timeout: 15 seconds")
        print(f"  Making request...")

    try:
        # Use the Spotify Track ID endpoint with longer timeout
        response = requests.get(url, headers=headers, timeout=15)

        if verbose:
            print(f"\n[DEBUG] API Response:")
            print(f"  Status Code: {response.status_code}")
            print(f"  Headers: {dict(response.headers)}")
            print(f"  Response Time: {response.elapsed.total_seconds():.2f}s")

        if response.status_code == 200:
            data = response.json()

            if verbose:
                print(f"\n[DEBUG] Raw Response Data:")
                import json
                print(json.dumps(data, indent=2))

            # Extract relevant fields
            # SoundNet returns: tempo, energy (0-100), happiness (0-100), danceability, etc.
            features = {
                'tempo': float(data.get('tempo')) if data.get('tempo') is not None else None,
                'energy': data.get('energy') / 100.0 if data.get('energy') is not None else None,     # Convert 0-100 to 0.0-1.0
                'valence': data.get('happiness') / 100.0 if data.get('happiness') is not None else None  # Convert 0-100 to 0.0-1.0
            }

            if verbose:
                print(f"\n[DEBUG] Extracted Features:")
                print(f"  tempo: {features['tempo']}")
                print(f"  energy: {features['energy']} (from {data.get('energy')})")
                print(f"  valence: {features['valence']} (from happiness: {data.get('happiness')})")

            # Validate that we got actual values
            if all(v is not None for v in features.values()):
                return features
            else:
                print(f"    [WARN] API returned incomplete data: {features}")
                return None

        elif response.status_code == 404:
            print(f"    [WARN] Track not found in SoundNet database (404)")
            if verbose:
                print(f"    Response body: {response.text}")
            return None

        elif response.status_code == 429:
            print(f"    [WARN] Rate limited by API (429)")
            retry_after = response.headers.get('Retry-After', 'unknown')
            print(f"    Retry-After: {retry_after}")
            if verbose:
                print(f"    Response body: {response.text}")
            return None

        elif response.status_code == 403:
            print(f"    [ERROR] Forbidden (403) - Check API key permissions")
            if verbose:
                print(f"    Response body: {response.text}")
            return None

        else:
            print(f"    [ERROR] API returned status {response.status_code}")
            print(f"    Response: {response.text[:200]}")
            return None

    except requests.exceptions.Timeout:
        print(f"    [ERROR] Request timeout (15 seconds)")
        return None

    except requests.exceptions.ConnectionError as e:
        print(f"    [ERROR] Connection error: {e}")
        return None

    except requests.exceptions.RequestException as e:
        print(f"    [ERROR] Request failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return None

    except Exception as e:
        print(f"    [ERROR] Unexpected error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return None


def backfill_audio_features(batch_size=10, delay_between_requests=1.0):
    """
    Backfill audio features for all songs with NULL valence/energy/tempo

    Args:
        batch_size (int): Number of songs to process before committing
        delay_between_requests (float): Seconds to wait between API calls (rate limiting)
    """

    # Validate RapidAPI key
    if not RAPIDAPI_KEY or RAPIDAPI_KEY == "your_rapidapi_key_here":
        print("\n[ERROR] RAPIDAPI_KEY not configured!")
        print("Please add RAPIDAPI_KEY to your .env file")
        print("Get your key from: https://rapidapi.com/")
        return

    print("\n" + "="*60)
    print("BACKFILL AUDIO FEATURES - SoundNet API")
    print("="*60)

    # Connect to database
    print("\n[1/4] Connecting to database...")
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor(dictionary=True)  # Return rows as dictionaries
        print(f"      Connected to: {DB_CONFIG['database']}@{DB_CONFIG['host']}")
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return

    # Fetch songs with NULL audio features
    print("\n[2/4] Fetching songs with missing audio features...")
    query = """
        SELECT spotify_song_id, title, artist, valence, energy, tempo
        FROM songs
        WHERE valence IS NULL OR energy IS NULL OR tempo IS NULL
        ORDER BY created_at DESC
    """

    try:
        cursor.execute(query)
        songs = cursor.fetchall()
        total_songs = len(songs)
        print(f"      Found {total_songs} songs with missing data")

        if total_songs == 0:
            print("\n[SUCCESS] All songs already have audio features!")
            cursor.close()
            db.close()
            return

    except Exception as e:
        print(f"[ERROR] Failed to fetch songs: {e}")
        cursor.close()
        db.close()
        return

    # Process each song
    print(f"\n[3/4] Processing {total_songs} songs...")
    print(f"      Rate limit: {delay_between_requests}s between requests")
    print("-"*60)

    updated_count = 0
    failed_count = 0
    skipped_count = 0

    for idx, song in enumerate(songs, 1):
        track_id = song['spotify_song_id']
        title = song['title']
        artist = song['artist']

        print(f"\n[{idx}/{total_songs}] {title} by {artist}")
        print(f"      Spotify ID: {track_id}")

        # Call SoundNet API with Spotify Track ID
        # Enable verbose logging for first 3 songs
        verbose = (idx <= 3)
        if verbose:
            print(f"      [Verbose logging enabled for first 3 songs]")
        else:
            print(f"      Fetching from SoundNet API...", end=" ")

        features = get_audio_features_from_soundnet(track_id, verbose=verbose)

        if features:
            print(f"OK")
            print(f"      tempo: {features['tempo']:.2f}, energy: {features['energy']:.3f}, valence: {features['valence']:.3f}")

            # Update database
            update_query = """
                UPDATE songs
                SET tempo = %s, energy = %s, valence = %s
                WHERE spotify_song_id = %s
            """

            try:
                cursor.execute(update_query, (
                    features['tempo'],
                    features['energy'],
                    features['valence'],
                    track_id
                ))

                # Commit after each batch
                if (idx % batch_size == 0) or (idx == total_songs):
                    db.commit()
                    print(f"      [COMMIT] Saved batch to database")

                updated_count += 1

            except Exception as e:
                print(f"      [ERROR] Database update failed: {e}")
                failed_count += 1

        else:
            print(f"FAILED")
            failed_count += 1

        # Rate limiting delay (skip on last song)
        if idx < total_songs:
            time.sleep(delay_between_requests)

    # Final summary
    print("\n" + "="*60)
    print("[4/4] BACKFILL COMPLETE")
    print("="*60)
    print(f"  Total songs processed: {total_songs}")
    print(f"  Successfully updated: {updated_count}")
    print(f"  Failed: {failed_count}")
    print(f"  Success rate: {(updated_count/total_songs*100):.1f}%")

    # Show remaining NULL songs
    cursor.execute("""
        SELECT COUNT(*) as null_count
        FROM songs
        WHERE valence IS NULL OR energy IS NULL OR tempo IS NULL
    """)
    remaining = cursor.fetchone()['null_count']
    print(f"\n  Songs still missing data: {remaining}")

    if remaining == 0:
        print("\n[SUCCESS] All songs now have audio features!")
    else:
        print(f"\n[NOTE] {remaining} songs could not be found in SoundNet database")
        print("       You may need to manually add these or skip them")

    # Close database connection
    cursor.close()
    db.close()
    print("\n[DONE] Database connection closed")


def test_api_connection():
    """Test SoundNet API connection with the example track from their docs"""
    print("\n" + "="*70)
    print("TESTING SOUNDNET API CONNECTION")
    print("="*70)

    if not RAPIDAPI_KEY or RAPIDAPI_KEY == "your_rapidapi_key_here":
        print("\n[ERROR] RAPIDAPI_KEY not configured!")
        print("Please add RAPIDAPI_KEY to your .env file")
        return False

    # Test with "Respect" by Aretha Franklin
    # This is the official example from SoundNet's API documentation
    test_track_id = "7s25THrKz86DM225dOYwnr"
    test_title = "Respect"
    test_artist = "Aretha Franklin"

    print(f"\nTest Track: {test_title} by {test_artist}")
    print(f"Spotify ID: {test_track_id}")
    print(f"(This is the official example from SoundNet docs)")
    print("\nCalling API with VERBOSE logging enabled...")
    print("-"*70)

    features = get_audio_features_from_soundnet(test_track_id, verbose=True)

    print("\n" + "="*70)
    if features:
        print("[SUCCESS] API TEST PASSED!")
        print("="*70)
        print(f"\nFinal Features:")
        print(f"  Tempo: {features['tempo']} BPM")
        print(f"  Energy: {features['energy']:.3f} (0.0-1.0)")
        print(f"  Valence: {features['valence']:.3f} (0.0-1.0)")
        print("\n[OK] API is working correctly!")
        print("     You can proceed with backfilling your songs.")
        return True
    else:
        print("[FAILED] API TEST FAILED!")
        print("="*70)
        print("\nPossible issues:")
        print("  1. RAPIDAPI_KEY is incorrect or invalid")
        print("  2. Not subscribed to 'Track Analysis' API on RapidAPI")
        print("  3. API quota exhausted (check your RapidAPI dashboard)")
        print("  4. Network/connectivity issues")
        print(f"\nYour API Key: {RAPIDAPI_KEY[:15]}...")
        print(f"API Host: {RAPIDAPI_HOST}")
        print("\nPlease check your RapidAPI dashboard at:")
        print("https://rapidapi.com/developer/dashboard")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("MOODDJ - AUDIO FEATURES BACKFILL TOOL")
    print("Uses SoundNet Track Analysis API (RapidAPI)")
    print("="*60)

    # Ask user what to do
    print("\nOptions:")
    print("  1. Test API connection")
    print("  2. Backfill all songs with missing audio features")
    print("  3. Exit")

    choice = input("\nEnter your choice (1/2/3): ").strip()

    if choice == "1":
        test_api_connection()

    elif choice == "2":
        # Test API first
        print("\n[STEP 1] Testing API connection...")
        if test_api_connection():
            print("\n[STEP 2] Starting backfill process...")
            input("\nPress ENTER to continue or CTRL+C to cancel...")

            # Ask for delay
            delay_input = input("\nDelay between requests in seconds (default 1.0): ").strip()
            delay = float(delay_input) if delay_input else 1.0

            backfill_audio_features(batch_size=10, delay_between_requests=delay)
        else:
            print("\n[ABORTED] Fix API connection first")

    elif choice == "3":
        print("\nGoodbye!")

    else:
        print("\nInvalid choice!")
