"""
Manual script to sync Spotify library to database
Run this directly to populate your database with songs
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import mysql.connector
from dotenv import load_dotenv
import os
import time
import requests

# Load environment variables
load_dotenv()

# Spotify setup
print("🎵 Initializing Spotify connection...")
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback"),
    scope="user-library-read",
    open_browser=True,
    cache_path=".spotify_cache"
))

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

# SoundNet API setup
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "track-analysis.p.rapidapi.com"

def get_audio_features_from_soundnet(track_id):
    """
    Fetch audio features from SoundNet Track Analysis API

    Args:
        track_id: Spotify track ID

    Returns:
        dict with 'valence', 'energy', 'tempo' or None if failed
    """
    if not RAPIDAPI_KEY or RAPIDAPI_KEY == "your_rapidapi_key_here":
        return None

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    try:
        url = f"https://{RAPIDAPI_HOST}/pktx/spotify/{track_id}"
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()

            # Map SoundNet fields to our database format
            features = {
                'valence': data.get('happiness') / 100.0 if data.get('happiness') is not None else None,
                'energy': data.get('energy') / 100.0 if data.get('energy') is not None else None,
                'tempo': float(data.get('tempo')) if data.get('tempo') is not None else None
            }

            # Validate all fields are present
            if all(v is not None for v in features.values()):
                return features
            else:
                return None
        else:
            return None
    except Exception as e:
        return None

def sync_library(limit=50):
    """Sync Spotify library to database"""
    print(f"\n🔄 Starting sync (limit: {limit} tracks)...")
    
    # Verify authentication
    try:
        user = sp.current_user()
        print(f"✅ Authenticated as: {user['display_name']}")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("\n💡 Delete .spotify_cache and try again")
        return
    
    offset = 0
    total_added = 0
    batch_size = 20  # Process 20 at a time
    
    while offset < limit:
        try:
            # Fetch user's saved tracks
            print(f"\n📥 Fetching tracks {offset} to {offset + batch_size}...")
            results = sp.current_user_saved_tracks(
                limit=min(batch_size, limit - offset),
                offset=offset
            )
            
            if not results['items']:
                print("✅ No more tracks to fetch")
                break
            
            # Process each track
            for item in results['items']:
                try:
                    track = item['track']
                    track_id = track['id']
                    title = track['name']
                    artist = track['artists'][0]['name'] if track['artists'] else 'Unknown'
                    album = track['album']['name']
                    duration_ms = track['duration_ms']

                    # Get audio features from SoundNet API
                    print(f"  🎵 Processing: {title} by {artist}...", end=' ')
                    features = get_audio_features_from_soundnet(track_id)

                    if features:
                        # Insert into database
                        sql = """
                            INSERT INTO songs (spotify_song_id, title, artist, album, duration_ms, valence, energy, tempo)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                                valence=VALUES(valence),
                                energy=VALUES(energy),
                                tempo=VALUES(tempo)
                        """
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
                        total_added += 1
                        print(f"✅ (valence: {features['valence']:.2f})")
                    else:
                        print("⚠️  No audio features available from SoundNet")

                    # Small delay to avoid rate limiting
                    time.sleep(0.5)
                    
                except Exception as track_error:
                    print(f"❌ Error: {track_error}")
                    continue
            
            offset += len(results['items'])
            print(f"\n✅ Progress: {total_added}/{offset} tracks added")
            
            # Delay between batches
            time.sleep(1)
            
        except Exception as e:
            print(f"\n❌ Batch error: {e}")
            if "429" in str(e):
                print("⏳ Rate limited - waiting 30 seconds...")
                time.sleep(30)
            else:
                break
    
    print(f"\n🎉 Sync complete! Total tracks added: {total_added}")
    
    # Show summary
    cursor.execute("SELECT COUNT(*) FROM songs")
    total = cursor.fetchone()[0]
    print(f"📊 Total songs in database: {total}")
    
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