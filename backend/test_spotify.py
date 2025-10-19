from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

print("🔐 Testing Spotify Authentication...")

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

# Test audio features with a known track
test_track_id = "3n3Ppam7vgaVa1iaRUc9Lp"  # Mr. Brightside
try:
    track = sp.track(test_track_id)
    print(f"✅ Track: {track['name']}")
    
    features = sp.audio_features([test_track_id])
    if features and features[0]:
        print(f"✅ Audio Features: valence={features[0]['valence']:.2f}, energy={features[0]['energy']:.2f}")
        print("\n🎉 Spotify authentication is working correctly!")
    else:
        print("❌ Audio features returned None")
        exit(1)
except Exception as e:
    print(f"❌ Audio features failed: {e}")
    print("\n💡 This might be a Spotify API permissions issue.")
    exit(1)

print("\n✅ All tests passed! You can now sync your library.")