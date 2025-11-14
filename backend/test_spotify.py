from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests

load_dotenv()

print("🔐 Testing Spotify Authentication and SoundNet API...")

# Create auth manager
auth_manager = SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback"),
    scope="user-library-read",
    open_browser=True,
    cache_path=".spotify_cache"
)

# Force new authentication
token_info = auth_manager.get_access_token(as_dict=False)
print(f"✅ Token obtained: {token_info[:20]}...")

# Create Spotify client
sp = spotipy.Spotify(auth=token_info)

# Test basic API call
try:
    user = sp.current_user()
    print(f"✅ User: {user['display_name']}")
except Exception as e:
    print(f"❌ User fetch failed: {e}")
    exit(1)

# Test track fetching
test_track_id = "3n3Ppam7vgaVa1iaRUc9Lp"  # Mr. Brightside
try:
    track = sp.track(test_track_id)
    print(f"✅ Track: {track['name']}")
except Exception as e:
    print(f"❌ Track fetch failed: {e}")
    exit(1)

# Test SoundNet API for audio features
print("\n🎵 Testing SoundNet API for audio features...")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "track-analysis.p.rapidapi.com"

if not RAPIDAPI_KEY or RAPIDAPI_KEY == "your_rapidapi_key_here":
    print("❌ RAPIDAPI_KEY not configured!")
    print("Please add RAPIDAPI_KEY to your .env file")
    exit(1)

try:
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    url = f"https://{RAPIDAPI_HOST}/pktx/spotify/{test_track_id}"
    response = requests.get(url, headers=headers, timeout=15)

    if response.status_code == 200:
        data = response.json()
        valence = data.get('happiness') / 100.0 if data.get('happiness') is not None else None
        energy = data.get('energy') / 100.0 if data.get('energy') is not None else None
        tempo = float(data.get('tempo')) if data.get('tempo') is not None else None

        if all(v is not None for v in [valence, energy, tempo]):
            print(f"✅ Audio Features from SoundNet:")
            print(f"   valence={valence:.2f}, energy={energy:.2f}, tempo={tempo:.1f}")
            print("\n🎉 All tests passed! You can now sync your library.")
        else:
            print("❌ SoundNet returned incomplete data")
            exit(1)
    else:
        print(f"❌ SoundNet API returned status {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        exit(1)
except Exception as e:
    print(f"❌ SoundNet API failed: {e}")
    exit(1)