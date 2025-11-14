# 🎵 MoodDJ - Your Mood, Your Music

**MoodDJ** is an intelligent web application that detects your facial expressions in real-time using computer vision and automatically adjusts your Spotify playlist to match your mood.

---

## 🚀 Installation Guide

This guide will walk you through setting up both the **backend** (Flask/Python) and **frontend** (React) components of MoodDJ.

---

## Prerequisites

Before starting, make sure you have:
- **Git** ([Download](https://git-scm.com/downloads))
- **MySQL 8.0+** ([Download](https://dev.mysql.com/downloads/mysql/))
- **Spotify Premium account**
- **RapidAPI account** (free) - for audio features ([Sign up](https://rapidapi.com/))
- **Webcam** (built-in or external)

> **Note**: Python 3.10 and Node.js will be installed during the setup steps below, so you don't need to install them globally on your system.

---

## Part 1: Clone the Repository

### Step 1: Open Terminal/Command Prompt

- **Windows**: Press `Win + R`, type `cmd`, press Enter
- **macOS**: Press `Cmd + Space`, type `Terminal`, press Enter
- **Linux**: Press `Ctrl + Alt + T`

### Step 2: Navigate to Your Workspace

Choose where you want to store the project. For example, Desktop:

```bash
# Windows
cd Desktop

# macOS/Linux
cd ~/Desktop
```

### Step 3: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/MoodDJ.git
```

> Replace `YOUR_USERNAME` with the actual GitHub username

### Step 4: Enter Project Directory

```bash
cd MoodDJ
```

You should now see the project structure with `backend/` and `mooddj-frontend/` folders.

---

## Part 2: Backend Setup (Python/Flask)

The backend handles mood detection, Spotify integration, and database management.

### Step 1: Create Initial Virtual Environment

Make sure you're in the **root project directory** (`.../MoodDJ/`), NOT in the backend folder.

**On Windows:**
```bash
python -m venv venv
```

**On macOS/Linux:**
```bash
python3 -m venv venv
```

This creates a `venv` folder in the root MoodDJ directory.

### Step 2: Activate Virtual Environment

**On Windows:**
```bash
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

✅ **Success Check**: You should see `(venv)` at the start of your terminal:
```
(venv) .../MoodDJ>
```

### Step 3: Install Python 3.10 in Virtual Environment

Now we'll install Python 3.10 specifically within your project's virtual environment, so you don't need to install it globally on your system.

**Check your current Python version:**
```bash
python --version
```

**If you don't have Python 3.10, install it in the venv:**

**On Windows:**
```bash
pip install python==3.10
```

**On macOS/Linux:**
```bash
pip install python==3.10
```

> **Note**: If the above doesn't work, you may need to use a tool like `pyenv` to manage Python versions within your virtual environment.

**Alternative Method Using pyenv (Recommended for version management):**

If you need to install Python 3.10 without affecting your system Python:

**Windows** (using pyenv-win):
```bash
# First, deactivate venv temporarily
deactivate

# Install pyenv-win
pip install pyenv-win --target %USERPROFILE%\.pyenv

# Install Python 3.10
pyenv install 3.10.11

# Set Python 3.10 for this project
pyenv local 3.10.11

# Recreate venv with Python 3.10
python -m venv venv

# Reactivate
venv\Scripts\activate
```

**macOS/Linux** (using pyenv):
```bash
# First, deactivate venv temporarily
deactivate

# Install pyenv (if not already installed)
curl https://pyenv.run | bash

# Install Python 3.10
pyenv install 3.10.11

# Set Python 3.10 for this project
pyenv local 3.10.11

# Recreate venv with Python 3.10
python -m venv venv

# Reactivate
source venv/bin/activate
```

### Step 4: Verify Python Version

```bash
python --version
```

✅ **You should see**: `Python 3.10.x`

If you still don't see Python 3.10, you may need to install it from [python.org](https://www.python.org/downloads/release/python-3100/) and recreate the virtual environment using:
- Windows: `py -3.10 -m venv venv`
- macOS/Linux: `python3.10 -m venv venv`

### Step 5: Navigate to Backend Directory

```bash
cd backend
```

You are now in: `.../MoodDJ/backend/`

### Step 6: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs Flask, Spotipy, OpenCV, MediaPipe, MySQL connector, and other dependencies.

**Installation takes 3-5 minutes.**
```bash
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

✅ **Success Check**: You should see `(venv)` at the start of your terminal:
```
(venv) .../MoodDJ>
```

### Step 3: Navigate to Backend Directory

```bash
cd backend
```

You are now in: `.../MoodDJ/backend/`

### Step 4: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs Flask, Spotipy, OpenCV, MediaPipe, MySQL connector, and other dependencies.

**Installation takes 3-5 minutes.**

---

## Part 3: Database Setup

### Step 1: Start MySQL Server

- **Windows**: Services → MySQL → Start
- **macOS**: `brew services start mysql`
- **Linux**: `sudo systemctl start mysql`

### Step 2: Create Database

Open a **new terminal window** and run:

```bash
mysql -u root -p
```

Enter your MySQL password when prompted.

### Step 3: Run Database Schema

In the MySQL prompt, run:

```sql
source database_schema.sql;
```

Or manually copy-paste the contents of `backend/database_schema.sql` into the MySQL prompt.

This creates:
- Database: `mooddj`
- Tables: `users`, `songs`, `moods`, `mood_sessions`, `user_songs`
- Default mood parameters

### Step 4: Verify Database

```sql
USE mooddj;
SHOW TABLES;
```

You should see 5 tables listed.

```sql
exit;
```

Close this terminal and return to your backend terminal with `(venv)` active.

---

## Part 4: Test Backend Connection

Still in `.../MoodDJ/backend/` with virtual environment active.

### Test 1: Database Connection

```bash
python test_connection.py
```

✅ Expected output:
```
✅ Connected to database: mooddj
✅ Tables found: 5
```

### Test 2: Spotify Authentication

```bash
python test_spotify.py
```

This will:
1. Open a browser for Spotify login
2. Redirect to a localhost URL
3. Test basic API calls

✅ Expected output:
```
✅ Token obtained
✅ User: Your Spotify Name
✅ Audio Features: valence=...
🎉 Spotify authentication is working correctly!
```

---

## Part 5: Sync Your Spotify Library & Audio Features

**Important**: Do this before running the main app to populate the database with songs.

### Step 1: Configure RapidAPI (Audio Features Workaround)

Spotify's audio features API has been deprecated. We use **SoundNet Track Analysis** as an alternative.

1. Go to [RapidAPI.com](https://rapidapi.com/) and create a free account
2. Subscribe to [Track Analysis API](https://rapidapi.com/soundnet-soundnet-default/api/track-analysis)
3. Copy your RapidAPI key
4. Add it to `backend/.env`:
   ```bash
   RAPIDAPI_KEY=your_rapidapi_key_here
   ```

### Step 2: Sync Spotify Library

Still in `.../MoodDJ/backend/` with `(venv)` active:

```bash
python sync_spotify_library.py
```

**What happens:**
1. Asks how many tracks to sync (default: 50)
2. Fetches your saved Spotify songs
3. Attempts to get audio features from Spotify (will likely fail)
4. **Automatically falls back to SoundNet API** for audio features
5. Stores songs with valence, energy, tempo in database

**This takes 2-5 minutes depending on number of tracks.**

### Step 3: Backfill Missing Features (if needed)

If your songs have NULL audio features, run the backfill script:

```bash
python backfill_audio_features.py
# Choose option 1 to test API, then option 2 to backfill
```

This updates all songs with missing audio features using SoundNet API.

✅ Expected output:
```
Total songs processed: 50
Successfully updated: 45-50
```

> **Note**: Some very obscure/regional songs may not be found in SoundNet's database. This is normal.

---

## Part 6: Frontend Setup (React)

### Step 1: Install Node.js and npm

The frontend requires Node.js (JavaScript runtime) and npm (package manager).

**Check if Node.js is already installed:**
```bash
node --version
npm --version
```

If you see version numbers (Node.js 16+ and npm 8+), skip to Step 2.

**If not installed, install Node.js:**

**Method 1: Using Node Version Manager (nvm) - Recommended**

This allows you to install Node.js locally for your project without affecting system-wide installations.

**Windows (nvm-windows):**
```bash
# Download and install nvm-windows from:
# https://github.com/coreybutler/nvm-windows/releases

# After installation, open a NEW terminal and run:
nvm install 18.18.0
nvm use 18.18.0
```

**macOS/Linux (nvm):**
```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash

# Close and reopen terminal, then:
nvm install 18.18.0
nvm use 18.18.0
```

**Method 2: Direct Installation**

Download and install from [nodejs.org](https://nodejs.org/):
- Download Node.js 18.x LTS (Long Term Support)
- Run the installer
- **On Windows**: Make sure to check "Add to PATH" during installation
- Restart your terminal after installation

**Verify installation:**
```bash
node --version
npm --version
```

✅ **You should see**: 
```
v18.x.x
9.x.x (or higher)
```

### Step 2: Open a New Terminal

Keep the backend terminal open. Open a **new terminal window**.

### Step 2: Navigate to Frontend Directory

```bash
cd Desktop/MoodDJ/mooddj-frontend
```

Or from the project root:
```bash
cd mooddj-frontend
```

You are now in: `.../MoodDJ/mooddj-frontend/`

### Step 3: Install Node Dependencies

```bash
npm install
```

This installs React, Material-UI, Socket.IO, Recharts, and other frontend dependencies.

**Installation takes 2-3 minutes.**

✅ You should see a `node_modules` folder created.

---

## Part 7: Running the Application

You need **two terminals open** - one for backend, one for frontend.

### Terminal 1: Start Backend Server

In `.../MoodDJ/backend/` with `(venv)` active:

```bash
python app.py
```

✅ Expected output:
```
[INFO] Database connection pool created successfully
[INFO] Starting MoodDJ Backend Server...
 * Running on http://0.0.0.0:5000
```

**Leave this terminal running.**

### Terminal 2: Start Frontend

In `.../MoodDJ/mooddj-frontend/`:

```bash
npm start
```

✅ Expected output:
```
Compiled successfully!
Local:            http://localhost:3000
```

**Your browser should automatically open to http://localhost:3000**

If it doesn't, manually go to: `http://localhost:3000`

---

## 🎮 Using MoodDJ

1. **Home Page**: Click "Get Started"
2. **Dashboard Opens**: You'll see 4 sections:
   - Camera feed (top left)
   - Current mood display (top right)
   - Music player (middle right)
   - Analytics (bottom)
3. **Click "Start Detection"**: Allows camera access
4. **Your mood is detected** every 2 seconds
5. **Music automatically plays** matching your mood!

---

## 📝 Daily Workflow (After Initial Setup)

### Every Time You Work on the Project:

**Terminal 1 - Backend:**
```bash
# Navigate to project root first
cd Desktop/MoodDJ

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Navigate to backend
cd backend

# Pull latest changes (do this from root before activating venv)
cd ..
git pull origin main
cd backend

# Start backend
python app.py
```

**Terminal 2 - Frontend:**
```bash
# Navigate to frontend
cd Desktop/MoodDJ/mooddj-frontend

# Pull latest changes
git pull origin main

# Start frontend
npm start
```

---

## 📁 Project Structure

```
MoodDJ/                              # Root project directory
│
├── venv/                            # Virtual environment (DO NOT COMMIT)
│
├── backend/                         # Flask Backend
│   ├── app.py                      # Main Flask application
│   ├── requirements.txt            # Python dependencies
│   ├── database_schema.sql         # Database structure
│   ├── .env                        # Environment variables (committed for now)
│   │
│   ├── config/
│   │   └── database.py            # Database connection pool
│   │
│   ├── routes/
│   │   ├── auth_routes.py         # Authentication endpoints
│   │   ├── mood_routes.py         # Mood detection endpoints
│   │   └── music_routes.py        # Music/Spotify endpoints
│   │
│   ├── services/
│   │   ├── mood_detector.py       # Mood detection logic (MediaPipe)
│   │   └── spotify_service.py     # Spotify API wrapper
│   │
│   ├── sync_spotify_library.py    # Script to populate database
│   ├── test_connection.py         # Test database connection
│   └── test_spotify.py            # Test Spotify authentication
│
├── mooddj-frontend/                # React Frontend
│   ├── public/                     # Static files
│   ├── src/
│   │   ├── components/
│   │   │   ├── VideoFeed/         # Camera component
│   │   │   ├── MoodDisplay/       # Shows current mood
│   │   │   ├── MusicPlayer/       # Music playback controls
│   │   │   └── Analytics/         # Mood statistics
│   │   │
│   │   ├── pages/
│   │   │   ├── HomePage.js        # Landing page
│   │   │   └── DashboardPage.js   # Main app page
│   │   │
│   │   ├── services/
│   │   │   ├── api.js             # Axios configuration
│   │   │   ├── moodService.js     # Mood API calls
│   │   │   ├── musicService.js    # Music API calls
│   │   │   └── websocket.js       # WebSocket connection
│   │   │
│   │   ├── store/
│   │   │   └── useStore.js        # Zustand state management
│   │   │
│   │   ├── App.js                 # Main React component
│   │   └── index.js               # Entry point
│   │
│   ├── package.json               # Node dependencies
│   └── .env                       # Frontend environment variables
│
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

---

## ⚠️ Common Issues & Solutions

### "Command not found: python"
- **Windows**: Use `python`
- **macOS/Linux**: Use `python3`

### "No module named 'flask'" (or similar)
- Ensure virtual environment is activated: you should see `(venv)`
- Reinstall: `pip install -r requirements.txt`

### "Failed to open camera" in frontend
- Close other apps using camera (Zoom, Teams, Skype)
- Check browser permissions (allow camera access)
- Try refreshing the page

### "No active Spotify devices found"
- **Open Spotify desktop app** or web player
- **Start playing any song** first
- Then try MoodDJ again

### "Connection refused" to backend
- Make sure backend is running: `python app.py`
- Check backend URL in `mooddj-frontend/.env`: should be `http://127.0.0.1:5000`

### "No songs found for this mood"
- Run the sync script: `python sync_spotify_library.py`
- If songs still have NULL audio features, run: `python backfill_audio_features.py`
- Make sure you have saved songs in your Spotify library and RapidAPI key is configured

### MySQL connection error
- Check if MySQL is running
- Verify credentials in `backend/.env`
- Test connection: `python test_connection.py`

### Frontend won't start / Module errors
- Delete `node_modules` and reinstall:
```bash
rm -rf node_modules
npm install
```

---

## 🔄 Pulling Latest Changes

When your teammates make updates:

```bash
# In project root
cd MoodDJ
git pull origin main

# Reinstall dependencies if needed
cd backend
pip install -r requirements.txt

cd ../mooddj-frontend
npm install
```

---

## 🆘 Getting Help

If you encounter issues:

1. Read the error message carefully
2. Check this README's troubleshooting section
3. Verify virtual environment is active (`(venv)` visible)
4. Ensure you're in the correct directory
5. Check that both backend and frontend are running
6. Contact your team lead
7. Create a GitHub issue with:
   - What you were trying to do
   - The exact error message
   - Your operating system

---

## 🎉 You're All Set!

Once you see the dashboard with your camera feed detecting your mood and Spotify playing music, you're ready to start developing!

**Happy coding! 🚀**