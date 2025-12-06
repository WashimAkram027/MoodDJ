# MoodDJ - AI-Powered Mood-Based Music Recommendation

MoodDJ is an intelligent web application that uses computer vision to detect your facial expressions in real-time and automatically recommends music from your Spotify library matching your current mood.

## Features

- **Real-time Mood Detection**: Uses MediaPipe for facial landmark detection and mood classification
- **Spotify Integration**: OAuth authentication and playback control
- **Personalized Recommendations**: Recommends songs based on audio features (valence, energy, tempo)
- **Multi-user Support**: Each user's Spotify library is synced independently
- **WebSocket Updates**: Real-time mood updates across connected clients

## Tech Stack

### Backend
- Flask (Python 3.10+)
- MediaPipe + OpenCV
- MySQL Database
- Flask-SocketIO
- Spotipy (Spotify API)

### Frontend
- React 19
- Material-UI
- Zustand (State Management)
- Socket.IO Client
- React Webcam

### Infrastructure
- Docker + Docker Compose
- AWS EC2 (Production)
- AWS RDS MySQL

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Spotify Premium Account
- RapidAPI Account (for audio features)
- MySQL 8.0+ (for local development without Docker)

### Option 1: Docker Deployment (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/WashimAkram027/MoodDJ.git
   cd MoodDJ
   ```

2. **Configure environment variables**

   Backend (`backend/.env`):
   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=mooddj
   DB_PORT=3306

   SECRET_KEY=your-secret-key

   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:5000/api/auth/callback

   RAPIDAPI_KEY=your_rapidapi_key
   RAPIDAPI_HOST=track-analysis.p.rapidapi.com

   FRONTEND_URL=http://127.0.0.1:3000
   BACKEND_URL=http://127.0.0.1:5000
   ```

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://127.0.0.1:3000
   - Backend API: http://127.0.0.1:5000

### Option 2: Local Development

#### Backend Setup

1. **Create virtual environment**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Set up database**
   ```bash
   mysql -u root -p < database_schema.sql
   ```

4. **Start backend**
   ```bash
   python app.py
   ```

#### Frontend Setup

1. **Install dependencies**
   ```bash
   cd mooddj-frontend
   npm install
   ```

2. **Start frontend**
   ```bash
   npm start
   ```

## Usage

1. Open http://127.0.0.1:3000 in your browser
2. Click "Connect with Spotify" to authenticate
3. Sync your Spotify library from the dashboard
4. Click "Start Detection" to enable mood detection
5. Music recommendations will update based on your detected mood

## Project Structure

```
MoodDJ/
├── backend/
│   ├── app.py                    # Flask application entry point
│   ├── config/
│   │   └── database.py           # Database connection pool
│   ├── routes/
│   │   ├── auth_routes.py        # OAuth & authentication
│   │   ├── mood_routes.py        # Mood detection endpoints
│   │   └── music_routes.py       # Music & playback endpoints
│   ├── services/
│   │   ├── audio_features_service.py  # RapidAPI integration
│   │   ├── mood_detector.py      # MediaPipe mood detection
│   │   └── spotify_service.py    # Spotify API wrapper
│   ├── tests/                    # Unit tests (46 tests)
│   ├── database_schema.sql       # MySQL schema
│   ├── Dockerfile
│   └── requirements.txt
│
├── mooddj-frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── VideoFeed/        # Webcam & detection
│   │   │   ├── MoodDisplay/      # Mood visualization
│   │   │   └── MusicPlayer/      # Playback controls
│   │   ├── pages/
│   │   │   ├── HomePage.js       # Landing page
│   │   │   └── DashboardPage.js  # Main application
│   │   ├── services/             # API & WebSocket services
│   │   └── store/                # Zustand state management
│   ├── __tests__/                # Frontend tests (15 tests)
│   ├── Dockerfile
│   └── package.json
│
├── docs/                         # Assignment documentation
├── docker-compose.yml
└── README.md
```

## API Endpoints

### Authentication
- `GET /api/auth/login` - Initiate Spotify OAuth
- `GET /api/auth/callback` - OAuth callback
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/status` - Check auth status

### Mood Detection
- `POST /api/mood/detect` - Detect mood from image
- `POST /api/mood/log` - Log mood to database
- `GET /api/mood/history` - Get mood history

### Music
- `GET /api/music/recommendations` - Get recommendations by mood
- `POST /api/music/play` - Play track on Spotify
- `POST /api/music/sync` - Sync user's Spotify library
- `GET /api/music/sync/status` - Get sync status

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd mooddj-frontend
npm test
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DB_HOST` | MySQL host |
| `DB_USER` | MySQL username |
| `DB_PASSWORD` | MySQL password |
| `DB_NAME` | Database name (default: mooddj) |
| `SPOTIFY_CLIENT_ID` | Spotify app client ID |
| `SPOTIFY_CLIENT_SECRET` | Spotify app client secret |
| `SPOTIFY_REDIRECT_URI` | OAuth callback URL |
| `RAPIDAPI_KEY` | RapidAPI key for audio features |
| `SECRET_KEY` | Flask session secret |

## Mood Detection

MoodDJ detects four moods based on facial expressions:
- **Happy** - High valence, high energy music
- **Sad** - Low valence, low energy music
- **Angry** - Low valence, high energy music
- **Neutral** - Medium valence, medium energy music

## Contributors

- Washim Akram - Lead Developer

## License

This project is developed for educational purposes as part of a capstone project.
