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

## Important: Spotify Account Access

Due to Spotify's API development mode limitations, **new users must be manually added** to the Spotify Developer Dashboard before they can use MoodDJ.

### For Testers/Evaluators

A **test Spotify account** has been set up for evaluation purposes. The credentials and Spotify ID are available in the **User Guide** document provided separately with this project.

### Adding New Users

If you need to add your own Spotify account:
1. The developer must add your Spotify email to the app's user list in the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Contact the developer with your Spotify account email to be whitelisted
3. Once added, you can authenticate and sync your library

> **Note**: This limitation exists because the app is in "Development Mode". In production with an extended quota, this manual step would not be required.

## Quick Start

### Prerequisites

- Python 3.10+ (for local development)
- Node.js 18+ and npm
- MySQL 8.0+ (or use developer's AWS RDS)
- Spotify Premium Account (or use provided test account)
- RapidAPI Account (for audio features)
- Docker & Docker Compose (optional, for containerized deployment)

### Option 1: Local Development

This option runs the backend and frontend directly on your machine without Docker.

#### Backend Setup

1. **Navigate to the backend directory**
   ```bash
   cd backend
   ```

2. **Create a Python virtual environment**

   A virtual environment isolates project dependencies from your system Python installation. This is **strongly recommended** to avoid conflicts.

   ```bash
   # Create the virtual environment
   python -m venv venv
   ```

3. **Activate the virtual environment**

   You must activate the venv every time you open a new terminal to work on this project.

   ```bash
   # Windows (Command Prompt)
   venv\Scripts\activate

   # Windows (PowerShell)
   venv\Scripts\Activate.ps1

   # macOS/Linux
   source venv/bin/activate
   ```

   When activated, you'll see `(venv)` at the beginning of your command prompt.

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up the database**

   Choose one of the following options:

   **Option A: Local MySQL Database**

   Set up your own MySQL instance:
   ```bash
   # Create the database
   mysql -u root -p -e "CREATE DATABASE mooddj;"

   # Import the schema
   mysql -u root -p mooddj < database_schema.sql
   ```

   Configure `backend/.env`:
   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=mooddj
   DB_PORT=3306
   ```

   **Option B: Developer's AWS RDS Database**

   Connect to the hosted database (credentials provided in User Guide):
   ```env
   DB_HOST=<aws-rds-endpoint-from-user-guide>
   DB_USER=<username-from-user-guide>
   DB_PASSWORD=<password-from-user-guide>
   DB_NAME=mooddj
   DB_PORT=3306
   ```

6. **Configure remaining environment variables**

   Complete your `backend/.env` file:
   ```env
   SECRET_KEY=your-secret-key-here

   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:5000/api/auth/callback

   RAPIDAPI_KEY=your_rapidapi_key
   RAPIDAPI_HOST=track-analysis.p.rapidapi.com

   FRONTEND_URL=http://127.0.0.1:3000
   BACKEND_URL=http://127.0.0.1:5000
   ```

7. **Start the backend server**
   ```bash
   python app.py
   ```

   The backend will run at http://127.0.0.1:5000

#### Frontend Setup

1. **Navigate to the frontend directory** (in a new terminal)
   ```bash
   cd mooddj-frontend
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Start the frontend development server**
   ```bash
   npm start
   ```

   The frontend will run at http://127.0.0.1:3000

### Option 2: Docker Deployment

This option uses Docker Compose to run both services in containers.

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

## Usage

1. Open http://127.0.0.1:3000 in your browser
2. Click "Connect with Spotify" to authenticate
3. Sync your Spotify library from the dashboard (click "Sync Library Now")
4. Click "Start Detection" to enable mood detection via webcam
5. Music recommendations will automatically update based on your detected mood
6. Use the play/pause controls to control Spotify playback

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
- `POST /api/music/recommend` - Get recommendations by mood
- `POST /api/music/play` - Play track on Spotify
- `POST /api/music/pause` - Pause playback
- `POST /api/music/resume` - Resume playback
- `POST /api/music/sync` - Sync user's Spotify library
- `GET /api/music/sync/status` - Get sync status
- `POST /api/music/reset` - Reset synced library

## Testing

### Backend Tests
```bash
cd backend
# Activate venv first
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
| `DB_HOST` | MySQL host (localhost or AWS RDS endpoint) |
| `DB_USER` | MySQL username |
| `DB_PASSWORD` | MySQL password |
| `DB_NAME` | Database name (default: mooddj) |
| `SPOTIFY_CLIENT_ID` | Spotify app client ID |
| `SPOTIFY_CLIENT_SECRET` | Spotify app client secret |
| `SPOTIFY_REDIRECT_URI` | OAuth callback URL |
| `RAPIDAPI_KEY` | RapidAPI key for audio features |
| `SECRET_KEY` | Flask session secret |

## Mood Detection

MoodDJ uses a majority voting algorithm to detect three moods based on facial expressions:

- **Happy** - Wide smile detected → High valence, high energy music
- **Angry** - Furrowed brows, squinting eyes → Low valence, high energy music
- **Neutral** - Relaxed expression → Medium valence, medium energy music

The mood is determined by analyzing facial landmarks every 3 seconds using MediaPipe, with a 3-frame majority voting system for stability.

## Contributors

- Washim Akram - Lead Developer

## License

This project is developed for educational purposes as part of a capstone project.
