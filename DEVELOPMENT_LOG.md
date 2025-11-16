# MoodDJ Development Log

**Last Updated:** 2025-01-16
**Status:** Production Deployment Active ✅

---

## Recent Changes & Progress

### 4. WebSocket CORS Configuration for Production (In Progress)
**Date:** 2025-01-16
**Goal:** Fix WebSocket connection failures on production deployment

**Issue Identified:**
- WebSocket connections failing in production at `wss://moodhdj.shop/socket.io/`
- Frontend `.env.production` using localhost URLs instead of actual domain
- Backend CORS not configured to allow moodhdj.shop origin

**Changes Made (Ready for Deployment):**
- ✅ Updated `mooddj-frontend/.env.production` to use `https://moodhdj.shop:5000`
- ✅ Added `https://moodhdj.shop` and `http://moodhdj.shop` to backend CORS origins
- ✅ Added moodhdj.shop to SocketIO `cors_allowed_origins` in backend/app.py
- ✅ Committed and pushed changes to main branch

**Files Modified:**
- `mooddj-frontend/.env.production` (lines 5-6)
- `backend/app.py` (lines 53-54, 66-67)

**Next Steps:**
- [ ] Deploy to EC2 via AWS Instance Connect
- [ ] Run `git pull origin main`
- [ ] Rebuild containers: `docker-compose down && docker-compose up -d --build`
- [ ] Verify WebSocket connection in browser console
- [ ] Test full application functionality

**Note:** SSH connection issues on Windows resolved by using AWS EC2 Instance Connect through browser console.

---

### 3. Production Environment Documentation & Workflow Setup
**Date:** 2025-01-16
**Goal:** Document production configuration and establish development workflow

**Key Accomplishments:**
- ✅ Documented production environment configuration in CLAUDE.md
- ✅ Clarified how localhost URLs work in production (monolithic EC2 deployment)
- ✅ Cleaned up unused .env files from repository
- ✅ Created comprehensive development and deployment workflow guide (DEV_WORKFLOW.md)
- ✅ Created testing infrastructure plan (TESTING_PLAN.md)
- ✅ Updated deployment guide with current EC2 Docker Compose approach

**Production Environment Understanding:**
- Frontend and backend both run on same EC2 instance
- React build uses `.env.production` with localhost URLs (`http://127.0.0.1:5000`)
- Works because Docker port mapping makes both services accessible on EC2
- This is a "development-style deployment" that's intentional for MVP stage
- Can migrate to domain-based URLs when scaling requires it

**AWS Secrets Manager Status:**
- Template exists (`backend/.env.production.template`) but NOT implemented
- Current deployment uses `.env` files directly
- Acceptable for MVP; can implement later when scaling

**Development Workflow Established:**
- Local development: `npm start` (frontend) or `python app.py` (backend) for fast iteration
- Docker testing: Optional before deployment to verify container behavior
- Deployment: SSH to EC2 → `git pull` → `docker-compose down && up --build`
- Documented in DEV_WORKFLOW.md with common scenarios and troubleshooting

**Files Created:**
- `TESTING_PLAN.md` - Comprehensive testing infrastructure plan (11-12 hour implementation)
- `DEV_WORKFLOW.md` - Development and deployment workflow guide
- `DEPLOYMENT_GUIDE.md` - Updated to reflect EC2 containerized approach
- `CLAUDE.md` - Updated with production environment configuration section

**Why This Matters:**
- Team now has clear understanding of how production works
- Development workflow is documented and streamlined
- Foundation laid for future testing infrastructure
- Can confidently make changes and deploy

---

### 1. Removed Deprecated Spotify Audio Features API
**Date:** Recent session
**Issue:** Spotify's `audio_features` API endpoint is completely deprecated
**Solution:** Removed all fallback logic and made RapidAPI SoundNet the primary and only source for audio features

**Files Modified:**
- `backend/services/spotify_service.py`
  - Removed `_fetch_audio_features_batch()` method (~100 lines)
  - Removed all fallback logic to Spotify API
  - RapidAPI SoundNet is now the sole audio features provider

**Why:** Spotify completely deprecated the audio_features API, so we need to rely entirely on RapidAPI for valence, energy, tempo, etc.

---

### 2. Implemented Web-Based Spotify OAuth Flow
**Date:** Recent session
**Goal:** Enable anyone to authenticate with their Spotify account for demo/presentation purposes

**Key Requirements Met:**
- ✅ No user accounts or login system needed
- ✅ Single user at a time (MVP)
- ✅ Anyone can authenticate with their Spotify account
- ✅ Works with Spotify's HTTPS requirements (`http://127.0.0.1` allowed)
- ✅ Supports both local development AND production deployment

---

## OAuth Implementation Details

### Backend Changes

#### `backend/services/spotify_service.py`
Added OAuth methods for web-based authentication:

```python
def get_auth_url(self):
    """Generate Spotify authorization URL for OAuth flow"""

def exchange_code_for_token(self, code: str):
    """Exchange authorization code for access token"""

def create_spotify_client(self, token_info: dict):
    """Create Spotify client from token information"""

def is_token_expired(self, token_info: dict) -> bool:
    """Check if access token is expired"""

def refresh_access_token(self, refresh_token: str):
    """Refresh expired access token"""
```

**Important:** All methods that interact with Spotify now accept `sp_client` parameter for session-based auth.

#### `backend/routes/auth_routes.py`
Added complete OAuth endpoints:

- `GET /api/auth/login` - Initiates OAuth flow, returns authorization URL
- `GET /api/auth/callback` - Handles OAuth callback, exchanges code for token, stores in session
- `POST /api/auth/logout` - Clears session
- `GET /api/auth/status` - Check authentication status (auto-refreshes expired tokens)

#### `backend/routes/music_routes.py`
Added helper function for session-based auth:

```python
def get_spotify_client():
    """Helper to get authenticated Spotify client from session"""
    token_info = session.get('spotify_token_info')
    if not token_info:
        return None, (jsonify({'error': 'Not authenticated'}), 401)
    sp_client = spotify_service.create_spotify_client(token_info)
    return sp_client, None
```

All music endpoints now use this helper to get authenticated client.

#### `backend/app.py`
Configured Flask sessions and CORS:

```python
# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_NAME'] = 'mooddj_session'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize Flask-Session (CRITICAL!)
Session(app)

# CORS with credentials
CORS(app, resources={
    r"/*": {
        "origins": ["http://127.0.0.1:3000", "http://localhost:3000"],
        "supports_credentials": True
    }
})
```

#### `backend/.env`
Updated to use `127.0.0.1` (required by Spotify):

```env
SPOTIFY_REDIRECT_URI=http://127.0.0.1:5000/api/auth/callback
FRONTEND_URL=http://127.0.0.1:3000
BACKEND_URL=http://127.0.0.1:5000
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_SAMESITE=Lax
```

#### `backend/requirements.txt`
Added Flask-Session dependency:

```
Flask-Session==0.8.0
```

**CRITICAL:** Flask-Session is required for filesystem sessions to work properly!

---

### Frontend Changes

#### `mooddj-frontend/src/services/authService.js`
Added OAuth flow methods:

```javascript
initiateSpotifyLogin: async () => {
  const data = await api.get('/api/auth/login');
  if (data.success && data.auth_url) {
    window.location.href = data.auth_url;  // Redirect to Spotify
  }
}

checkAuthStatus: async () => {
  const data = await api.get('/api/auth/status');
  return data;  // Returns {authenticated: bool, user: {...}}
}

logout: async () => {
  const data = await api.post('/api/auth/logout');
  return data;
}
```

#### `mooddj-frontend/src/services/api.js`
Configured axios for credentials:

```javascript
const API_BASE_URL = 'http://127.0.0.1:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true  // CRITICAL: Send cookies with requests
});
```

#### `mooddj-frontend/src/App.js`
Added AuthContext and auth checking:

```javascript
export const AuthContext = createContext(null);

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  useEffect(() => {
    const initializeApp = async () => {
      const authStatus = await authService.checkAuthStatus();
      if (authStatus.authenticated) {
        setIsAuthenticated(true);
        setUser(authStatus.user);
      }
      setAuthLoading(false);
    };
    initializeApp();
  }, []);

  return (
    <AuthContext.Provider value={{isAuthenticated, user, authLoading, setIsAuthenticated, setUser}}>
      {/* Routes */}
    </AuthContext.Provider>
  );
}
```

#### `mooddj-frontend/src/pages/HomePage.js`
Added "Connect with Spotify" button:

```javascript
const handleConnectSpotify = async () => {
  setIsConnecting(true);
  await authService.initiateSpotifyLogin();
};

<Button onClick={handleConnectSpotify} disabled={isConnecting}>
  {isConnecting ? 'Connecting...' : '🎵 Connect with Spotify →'}
</Button>
```

#### `mooddj-frontend/src/pages/DashboardPage.js`
Added auth protection:

```javascript
const { isAuthenticated, user, authLoading } = useContext(AuthContext);

useEffect(() => {
  if (!authLoading && !isAuthenticated) {
    navigate('/');  // Redirect to home if not authenticated
  }
}, [isAuthenticated, authLoading]);
```

#### `mooddj-frontend/.env`
Updated to use `127.0.0.1`:

```env
REACT_APP_API_URL=http://127.0.0.1:5000
REACT_APP_WS_URL=http://127.0.0.1:5000
```

---

## Critical Issues Resolved

### Issue 1: API Response Double-Unwrapping
**Error:** `TypeError: Cannot read properties of undefined (reading 'success')`

**Cause:** Frontend was accessing `response.data.success` but `api.js` interceptor already returns `response.data`

**Fix:** Changed authService methods to use `data.success` instead of `response.data.success`

---

### Issue 2: Missing Database Column
**Error:** `Unknown column 'last_login' in 'field list'`

**Fix:** Removed `last_login = CURRENT_TIMESTAMP` from database update query in `auth_routes.py`

---

### Issue 3: Cookie Domain Mismatch
**Error:** User authenticated successfully but redirected back to home screen with "User not authenticated"

**Cause:** Session cookies set on `127.0.0.1:5000` weren't being sent with requests from `localhost:3000`

**Fix:**
1. Changed all URLs to use `127.0.0.1` instead of `localhost`
2. Updated `.env` files in both backend and frontend
3. Removed `SESSION_COOKIE_DOMAIN` setting to let Flask use requesting domain

**IMPORTANT:** Users MUST access the app at `http://127.0.0.1:3000` (NOT `localhost:3000`)

---

### Issue 4: Session Not Persisting
**Error:** OAuth callback worked but session data wasn't persisting

**Cause:** `SESSION_TYPE = 'filesystem'` configured but Flask-Session extension not installed or initialized

**Fix:**
1. Added `Flask-Session==0.8.0` to `requirements.txt`
2. Imported `from flask_session import Session` in `app.py`
3. Called `Session(app)` after app configuration

**Result:** ✅ OAuth authentication now works perfectly!

---

## OAuth Flow Summary

1. **User clicks "Connect with Spotify"** → Frontend calls `GET /api/auth/login`
2. **Backend returns auth URL** → Frontend redirects to Spotify authorization page
3. **User authorizes on Spotify** → Spotify redirects to `http://127.0.0.1:5000/api/auth/callback?code=...`
4. **Backend exchanges code for token** → Stores in server-side session (7-day lifetime)
5. **Backend gets user profile** → Stores user info in session
6. **Backend redirects to dashboard** → `http://127.0.0.1:3000/dashboard`
7. **Frontend checks auth status** → `GET /api/auth/status` (cookies sent automatically)
8. **Backend verifies session** → Returns `{authenticated: true, user: {...}}`
9. **Dashboard loads** → User is authenticated and can use the app

---

## Important Configuration Notes

### Spotify Requirements
- HTTPS required UNLESS using loopback address
- `http://127.0.0.1:PORT` is allowed (what we use for development)
- `localhost` is NOT allowed as redirect URI
- Must register redirect URI in Spotify Developer Dashboard

### Session Configuration
- **Type:** Filesystem (server-side)
- **Lifetime:** 7 days
- **Cookie Name:** `mooddj_session`
- **Security:** httpOnly, sameSite=Lax
- **HTTPS:** Only in production (SESSION_COOKIE_SECURE=True)

### CORS Configuration
- **Credentials:** Enabled (`supports_credentials: True`)
- **Origins:** Both `localhost:3000` and `127.0.0.1:3000` allowed
- **Methods:** GET, POST, PUT, DELETE
- **Headers:** Content-Type, Authorization

---

## Development Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

**Backend runs on:** `http://0.0.0.0:5000` (accessible via `127.0.0.1:5000`)

### Frontend
```bash
cd mooddj-frontend
npm install
npm start
```

**Frontend runs on:** `http://127.0.0.1:3000`

### Testing OAuth
1. Navigate to `http://127.0.0.1:3000` (NOT localhost!)
2. Click "Connect with Spotify"
3. Authorize on Spotify
4. You should land on dashboard and stay authenticated

---

## Production Deployment Considerations

### For AWS/GCP/Azure Deployment:

1. **Update Environment Variables:**
   ```env
   SPOTIFY_REDIRECT_URI=https://yourdomain.com/api/auth/callback
   FRONTEND_URL=https://yourdomain.com
   BACKEND_URL=https://yourdomain.com
   SESSION_COOKIE_SECURE=True
   SESSION_COOKIE_SAMESITE=Lax
   ```

2. **Update Spotify Developer Dashboard:**
   - Add production redirect URI: `https://yourdomain.com/api/auth/callback`

3. **Enable HTTPS:**
   - Use Let's Encrypt or cloud provider's SSL/TLS
   - Flask will automatically use HTTPS cookies when `SESSION_COOKIE_SECURE=True`

4. **Session Storage:**
   - Consider Redis/Memcached instead of filesystem for scalability
   - Update `SESSION_TYPE` in `app.py`

5. **Security:**
   - Change `SECRET_KEY` to a strong random value
   - Enable all security headers
   - Consider rate limiting on auth endpoints

---

## Current System Architecture

### Mood Detection → Music Playback Flow

1. **User starts detection** (VideoFeed component)
2. **Webcam captures frame** every 2 seconds
3. **MediaPipe detects facial landmarks**
4. **Mood classifier predicts emotion** (happy, sad, angry, neutral)
5. **Frontend sends mood to backend** via WebSocket or API
6. **Backend queries database** for songs matching mood (using audio features)
7. **Audio features from RapidAPI** (valence, energy, tempo) - NOT Spotify API
8. **Backend returns recommendations**
9. **Frontend plays music** via Spotify Web Playback SDK or direct API calls

### Audio Features Source
- **Primary/Only:** RapidAPI SoundNet Track Analysis
- **API Key:** Stored in `.env` as `RAPIDAPI_KEY`
- **Why:** Spotify's audio_features API is completely deprecated

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    spotify_id VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255),
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Songs Table
```sql
CREATE TABLE songs (
    song_id INT AUTO_INCREMENT PRIMARY KEY,
    spotify_track_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    artist VARCHAR(255),
    valence FLOAT,
    energy FLOAT,
    tempo FLOAT,
    -- Other audio features
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Next Steps / Potential Improvements

### High Priority
- [ ] Test OAuth flow end-to-end with actual music playback
- [ ] Verify mood detection → music recommendation pipeline works
- [ ] Test token refresh when access token expires (1 hour)
- [ ] Add logout button on dashboard

### Medium Priority
- [ ] Add error handling for RapidAPI failures
- [ ] Implement caching for audio features to reduce API calls
- [ ] Add loading states during OAuth flow
- [ ] Display user profile picture on dashboard

### Low Priority / Future
- [ ] Add analytics tracking for mood patterns
- [ ] Implement playlist creation based on mood history
- [ ] Add social features (share mood/music)
- [ ] Deploy to production (AWS/GCP/Azure)

---

## Known Issues / Limitations

1. **Single User Only:** Current implementation is MVP - only one user can be authenticated at a time (session-based)
2. **Browser Cookies Required:** Users must allow cookies for authentication to work
3. **Must Use 127.0.0.1:** Using `localhost` will break cookie handling
4. **RapidAPI Rate Limits:** Check RapidAPI plan limits for SoundNet API
5. **No Refresh Token Rotation:** Security best practice but not implemented yet

---

## Key Files Reference

### Backend Core
- `backend/app.py` - Main Flask app, session config, CORS
- `backend/services/spotify_service.py` - All Spotify interactions, OAuth methods
- `backend/routes/auth_routes.py` - OAuth endpoints
- `backend/routes/music_routes.py` - Music playback endpoints
- `backend/routes/mood_routes.py` - Mood detection endpoints
- `backend/.env` - Environment variables (DO NOT COMMIT!)

### Frontend Core
- `mooddj-frontend/src/App.js` - Auth context, route protection
- `mooddj-frontend/src/services/authService.js` - Auth API calls
- `mooddj-frontend/src/services/api.js` - Axios config with credentials
- `mooddj-frontend/src/pages/HomePage.js` - Landing page with OAuth button
- `mooddj-frontend/src/pages/DashboardPage.js` - Main app interface
- `mooddj-frontend/.env` - Frontend environment variables

---

## Git Status
```
Current branch: main
Modified: backend/.spotify_cache (ignored - contains cached tokens)
```

---

## Contact & Resources

- **Spotify OAuth Docs:** https://developer.spotify.com/documentation/web-api/tutorials/code-flow
- **Flask-Session Docs:** https://flask-session.readthedocs.io/
- **RapidAPI SoundNet:** https://rapidapi.com/track-analysis
- **MediaPipe Face Mesh:** https://google.github.io/mediapipe/solutions/face_mesh

---

## Tips for Tomorrow

1. **If OAuth stops working:**
   - Check if backend is running on `127.0.0.1:5000`
   - Check if frontend is accessed via `127.0.0.1:3000`
   - Clear browser cookies and try again
   - Check if `Flask-Session` is installed: `pip list | grep Flask-Session`

2. **If session doesn't persist:**
   - Verify `Session(app)` is called in `app.py`
   - Check if `flask_session/` directory exists in backend folder
   - Restart backend server

3. **If CORS errors:**
   - Verify `withCredentials: true` in `api.js`
   - Check CORS origins include both localhost and 127.0.0.1
   - Check `supports_credentials: True` in CORS config

4. **Testing OAuth:**
   - Always test in incognito/private window first
   - Check browser console for errors
   - Check backend logs for detailed flow

---

**Status:** OAuth authentication is fully functional! Ready to continue with music playback and mood detection integration.
