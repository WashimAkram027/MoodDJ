"""
Unified Spotify Library Sync Script
Syncs Spotify tracks AND audio features in ONE pass

This script:
1. Fetches track metadata from Spotify
2. Immediately fetches audio features from RapidAPI SoundNet
3. Stores complete records in database

Usage:
    python sync_spotify_library.py
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import mysql.connector
from dotenv import load_dotenv
import os
import time
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.audio_features_service import AudioFeaturesService

# Load environment variables
load_dotenv()

# Initialize services
print("🎵 Initializing Spotify connection...")
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback"),
    scope="user-library-read",
    open_browser=True,
    cache_path=".spotify_cache"
))

print("🎛️  Initializing Audio Features Service...")
audio_service = AudioFeaturesService()
if not audio_service.is_enabled():
    print("⚠️  WARNING: RapidAPI key not configured!")
    print("   Audio features will NOT be fetched.")
    print("   Add RAPIDAPI_KEY to .env to enable audio features.")
    proceed = input("\nContinue anyway? (y/n): ").strip().lower()
    if proceed != 'y':
        print("❌ Sync aborted")
        sys.exit(1)

# Database setup
print("💾 Connecting to database...")
db = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=int(os.getenv('DB_PORT', 3306)),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME', 'mooddj')
)
cursor = db.cursor()

def sync_library(limit=50):
    """
    Unified sync: Fetch Spotify tracks AND audio features in ONE pass

    Flow:
    1. Get track metadata from Spotify
    2. Immediately fetch audio features from RapidAPI SoundNet
    3. Store complete record with all data
    """
    print(f"\n🔄 Starting unified sync (limit: {limit} tracks)...")
    print("="*70)

    # Verify authentication
    try:
        user = sp.current_user()
        print(f"✅ Authenticated as: {user['display_name']}")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("\n💡 Delete .spotify_cache and try again")
        return

    offset = 0
    total_processed = 0
    tracks_with_features = 0
    tracks_without_features = 0
    batch_size = 20  # Process 20 at a time

    while offset < limit:
        try:
            # Fetch user's saved tracks from Spotify
            print(f"\n📥 Fetching tracks {offset + 1} to {offset + batch_size}...")
            results = sp.current_user_saved_tracks(
                limit=min(batch_size, limit - offset),
                offset=offset
            )

            if not results['items']:
                print("✅ No more tracks to fetch")
                break

            print(f"   Retrieved {len(results['items'])} tracks from Spotify")
            print("-"*70)

            # Process each track: Get metadata + audio features together
            for idx, item in enumerate(results['items'], 1):
                try:
                    track = item['track']
                    track_id = track['id']
                    title = track['name']
                    artist = track['artists'][0]['name'] if track['artists'] else 'Unknown'
                    album = track['album']['name']
                    duration_ms = track['duration_ms']

                    print(f"\n[{offset + idx}] 🎵 {title} by {artist}")
                    print(f"    Track ID: {track_id}")
                    print(f"    Fetching audio features from RapidAPI...", end=' ')

                    # Fetch audio features from RapidAPI SoundNet (NOT Spotify)
                    features = audio_service.get_audio_features(track_id)

                    # Prepare database insert
                    sql = """
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

                    if features:
                        # Store with complete audio features
                        cursor.execute(sql, (
                            track_id,
                            title,
                            artist,
                            album,
                            duration_ms,
                            features['valence'],
                            features['energy'],
                            features['tempo']
                        ))
                        db.commit()
                        tracks_with_features += 1
                        print(f"✅")
                        print(f"    valence: {features['valence']:.3f}, energy: {features['energy']:.3f}, tempo: {features['tempo']:.1f}")
                    else:
                        # Store track metadata only (features will be NULL)
                        cursor.execute(sql, (
                            track_id,
                            title,
                            artist,
                            album,
                            duration_ms,
                            None,  # valence
                            None,  # energy
                            None   # tempo
                        ))
                        db.commit()
                        tracks_without_features += 1
                        print(f"⚠️  No audio features available")

                    total_processed += 1

                    # Rate limiting delay (1 second between RapidAPI calls)
                    if idx < len(results['items']):
                        time.sleep(1.0)

                except Exception as track_error:
                    print(f"    ❌ Error: {track_error}")
                    continue

            offset += len(results['items'])
            print("\n" + "-"*70)
            print(f"📊 Progress: {total_processed} tracks processed")
            print(f"   ✅ With features: {tracks_with_features}")
            print(f"   ⚠️  Without features: {tracks_without_features}")
            print(f"   Success rate: {(tracks_with_features/total_processed*100):.1f}%")

            # Delay between batches
            time.sleep(2)

        except Exception as e:
            print(f"\n❌ Batch error: {e}")
            if "429" in str(e):
                print("⏳ Rate limited - waiting 30 seconds...")
                time.sleep(30)
            else:
                break

    # Final summary
    print("\n" + "="*70)
    print("🎉 SYNC COMPLETE!")
    print("="*70)
    print(f"Total tracks processed: {total_processed}")
    print(f"  ✅ With audio features: {tracks_with_features}")
    print(f"  ⚠️  Without features: {tracks_without_features}")
    print(f"  Success rate: {(tracks_with_features/total_processed*100):.1f}%" if total_processed > 0 else "  Success rate: N/A")

    # Database statistics
    cursor.execute("SELECT COUNT(*) FROM songs")
    total = cursor.fetchone()[0]
    print(f"\n📊 Total songs in database: {total}")

    cursor.execute("""
        SELECT COUNT(*) FROM songs
        WHERE valence IS NOT NULL AND energy IS NOT NULL AND tempo IS NOT NULL
    """)
    complete = cursor.fetchone()[0]
    print(f"   Complete records (with features): {complete}")
    print(f"   Incomplete records (missing features): {total - complete}")

    # Show mood distribution
    cursor.execute("""
        SELECT mood_name, COUNT(*) as count
        FROM moods m
        LEFT JOIN songs s ON
            s.valence BETWEEN m.target_valence_min AND m.target_valence_max
            AND s.energy BETWEEN m.target_energy_min AND m.target_energy_max
        GROUP BY m.mood_name
    """)
    print("\n📊 Songs per mood:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} songs")

if __name__ == "__main__":
    try:
        # Ask user for limit
        limit_input = input("\nHow many tracks to sync? (default 50): ").strip()
        limit = int(limit_input) if limit_input else 50
        
        sync_library(limit)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Sync interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        cursor.close()
        db.close()
        print("\n👋 Goodbye!")