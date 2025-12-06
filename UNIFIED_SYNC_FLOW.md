# 🎵 MoodDJ - Unified Sync Flow Documentation

## Overview

The MoodDJ sync process has been **unified** to populate Spotify track metadata AND audio features in a **single pass**. No more two-step process!

## ⚠️ Important: Audio Features Source

**Spotify's `audio_features()` API is COMPLETELY DEPRECATED and has been removed from the codebase.**

- ❌ **NOT USED:** Spotify audio_features API
- ✅ **ONLY SOURCE:** RapidAPI SoundNet Track Analysis API
- ✅ **NO FALLBACK:** RapidAPI is the primary (and only) source

All audio features (valence, energy, tempo) are now fetched exclusively from RapidAPI SoundNet.

---

## 🔄 New Unified Flow

### **Before (Old Two-Step Process)**
```
1. Run sync_spotify_library.py
   → Fetch tracks from Spotify
   → Try Spotify audio_features API (COMPLETELY DEPRECATED ❌)
   → Store tracks with NULL audio features

2. Run backfill_audio_features.py
   → Query database for NULL features
   → Call RapidAPI SoundNet for each
   → UPDATE database with features
```

**Problems:**
- ❌ Two separate scripts needed
- ❌ Spotify audio_features API is completely deprecated and removed
- ❌ Database initially populated with incomplete records
- ❌ Manual intervention required

---

### **After (New Unified Process)**
```
Backend starts → Auto-check database
  ↓
If database empty:
  → Fetch tracks from Spotify (metadata only)
  → For EACH track immediately:
     - Call RapidAPI SoundNet for audio features
     - Store COMPLETE record in database
  ↓
Result: Fully populated database in ONE pass ✅
```

**Benefits:**
- ✅ Single unified sync process
- ✅ Audio features fetched during sync, not after
- ✅ No NULL values for new tracks
- ✅ Automatic on backend startup
- ✅ Reusable service architecture

---

## 📁 Architecture Changes

### **New Files Created**

#### 1. `backend/services/audio_features_service.py`
**Purpose:** PRIMARY and ONLY source for audio features (RapidAPI SoundNet)

**Key Methods:**
- `get_audio_features(track_id)` - Fetch features for single track
- `batch_get_audio_features(track_ids)` - Fetch for multiple tracks with rate limiting
- `is_enabled()` - Check if RapidAPI key is configured

**Features:**
- Automatic retry on rate limit (429)
- Error handling for 403, 404 responses
- Converts SoundNet format (0-100) to Spotify format (0.0-1.0)
- Singleton pattern for easy import

**Note:** Spotify's audio_features API is completely deprecated and NOT used anywhere in the codebase.

**Usage:**
```python
from services.audio_features_service import audio_features_service

features = audio_features_service.get_audio_features("7s25THrKz86DM225dOYwnr")
# Returns: {'valence': 0.720, 'energy': 0.850, 'tempo': 128.0}
```

---

### **Modified Files**

#### 2. `backend/sync_spotify_library.py`
**Changes:**
- Now imports and uses `AudioFeaturesService`
- For each Spotify track, immediately calls RapidAPI for audio features
- Stores complete records in database (no NULL values)
- Better progress tracking and error reporting

**New Flow:**
```python
for track in spotify_tracks:
    # 1. Get metadata from Spotify
    track_id = track['id']
    title = track['name']
    artist = track['artists'][0]['name']

    # 2. IMMEDIATELY fetch audio features from RapidAPI
    features = audio_service.get_audio_features(track_id)

    # 3. Store COMPLETE record
    INSERT INTO songs (track_id, title, artist, valence, energy, tempo)
    VALUES (%s, %s, %s, %s, %s, %s)
```

**Usage:**
```bash
python sync_spotify_library.py
# Prompts for number of tracks to sync
# Syncs metadata + audio features in one pass
```

---

#### 3. `backend/services/spotify_service.py`
**Changes:**
- ❌ **REMOVED** all Spotify `audio_features()` API calls (deprecated)
- ❌ **REMOVED** `_fetch_audio_features_batch()` method (100+ lines)
- ✅ **USES ONLY** `AudioFeaturesService` for audio features
- ✅ Direct integration with RapidAPI (no fallback logic needed)
- Cleaner, simpler code

**Before (Complex fallback logic with deprecated API):**
```python
# Try Spotify first (deprecated)
audio_features = self._fetch_audio_features_batch(track_ids)

# Fallback to SoundNet if Spotify fails
for track, features in zip(track_data, audio_features):
    if not features:
        features = self._fetch_audio_features_from_soundnet(track['id'])
```

**After (Direct RapidAPI integration):**
```python
# Direct RapidAPI call (primary and only source)
features = self.audio_features_service.get_audio_features(track_id)
```

---

#### 4. `backend/app.py`
**Changes:**
- Added `check_and_sync_library()` startup hook
- Automatically checks if database is empty on startup
- Triggers sync if needed

**Startup Flow:**
```python
if __name__ == '__main__':
    logger.info('Starting MoodDJ Backend Server...')

    # 1. Check database
    check_and_sync_library()

    # 2. Start server
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

**Output:**
```
Starting MoodDJ Backend Server...
----------------------------------------------------------------------
Database check: Found 0 songs in database
======================================================================
🔄 DATABASE IS EMPTY - Starting auto-sync...
======================================================================
[Sync process runs automatically]
======================================================================
✅ AUTO-SYNC COMPLETE!
   Total tracks: 50
   With features: 48
   Without features: 2
======================================================================
----------------------------------------------------------------------
🚀 Server ready! Running on http://0.0.0.0:5000
```

---

## 🚀 Usage Guide

### **Scenario 1: Fresh Database (Empty)**

1. **Start the backend:**
   ```bash
   cd backend
   python app.py
   ```

2. **Backend automatically:**
   - Detects empty database
   - Syncs 50 tracks from Spotify
   - Fetches audio features for each from RapidAPI
   - Stores complete records

3. **Result:** Database fully populated on startup ✅

---

### **Scenario 2: Manual Sync (Any Time)**

**Option A: Via Standalone Script**
```bash
cd backend
python sync_spotify_library.py

# Prompts:
# How many tracks to sync? (default 50): 100
# [Syncs 100 tracks with audio features]
```

**Option B: Via API Endpoint**
```bash
curl -X POST http://localhost:5000/api/music/sync \
  -H "Content-Type: application/json" \
  -d '{"limit": 100}'
```

**Response:**
```json
{
  "success": true,
  "total_processed": 100,
  "with_features": 97,
  "without_features": 3
}
```

---

### **Scenario 3: Backfill Existing NULL Records**

If you have old records with NULL audio features:

```bash
cd backend
python backfill_audio_features.py

# Options:
#   1. Test API connection
#   2. Backfill all songs with missing audio features
#   3. Exit
```

**Note:** This script is now mainly for **fixing old data**. New syncs won't create NULL records.

---

## ⚙️ Configuration

### **Required Environment Variables**

Add to `.env`:
```env
# RapidAPI Configuration (REQUIRED for audio features)
RAPIDAPI_KEY=your_rapidapi_key_here
RAPIDAPI_HOST=track-analysis.p.rapidapi.com

# Spotify Configuration
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_db_password
DB_NAME=mooddj
```

### **Get RapidAPI Key**

1. Sign up at [RapidAPI](https://rapidapi.com/)
2. Subscribe to [Track Analysis API](https://rapidapi.com/apiroom-apiroom-default/api/track-analysis/)
3. Copy your API key
4. Add to `.env` as `RAPIDAPI_KEY`

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND STARTS                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Check Database  │
                │ for songs count │
                └────────┬────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
            ▼                         ▼
     Count = 0                   Count > 0
  (Empty Database)          (Already populated)
            │                         │
            │                         ▼
            │                   Skip auto-sync
            │                   Log: "Database OK"
            │
            ▼
    ┌──────────────────┐
    │  AUTO-SYNC START │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────────────────────────────┐
    │ SpotifyService.fetch_and_store_user_tracks()
    └────────┬─────────────────────────────────┘
             │
             ▼
    ┌──────────────────────────────────────────┐
    │ For each track in Spotify library:       │
    │                                           │
    │ 1. Get metadata from Spotify API         │
    │    - track_id, title, artist, album      │
    │                                           │
    │ 2. Fetch audio features from RapidAPI    │
    │    AudioFeaturesService.get_audio_features()
    │    - valence, energy, tempo              │
    │                                           │
    │ 3. Store COMPLETE record in database     │
    │    INSERT INTO songs (...)               │
    │                                           │
    │ 4. Wait 1 second (rate limiting)         │
    └────────┬─────────────────────────────────┘
             │
             ▼
    ┌──────────────────┐
    │  SYNC COMPLETE   │
    │  Database ready! │
    └──────────────────┘
```

---

## 🔧 API Endpoints

### **Sync Library**
```http
POST /api/music/sync
Content-Type: application/json

{
  "limit": 50  // Optional, default 50
}
```

**Response:**
```json
{
  "success": true,
  "total_processed": 50,
  "with_features": 48,
  "without_features": 2
}
```

### **Get Recommendations**
```http
POST /api/music/recommend
Content-Type: application/json

{
  "mood": "happy",
  "limit": 30
}
```

**Response:**
```json
{
  "success": true,
  "mood": "happy",
  "songs": [
    {
      "id": 1,
      "spotify_song_id": "7s25THrKz86DM225dOYwnr",
      "title": "Respect",
      "artist": "Aretha Franklin",
      "valence": 0.720,
      "energy": 0.850,
      "tempo": 128.0
    }
  ],
  "count": 30
}
```

---

## 🎯 Summary of Improvements

| Feature | Before | After |
|---------|--------|-------|
| **Sync Process** | Two-step (sync + backfill) | One-step (unified) |
| **Audio Features Source** | Spotify (deprecated, removed) | **RapidAPI SoundNet ONLY** |
| **Fallback Logic** | Complex (Spotify → RapidAPI) | **No fallback needed** |
| **Code Duplication** | Yes (3 places) | No (1 service) |
| **Auto-sync on Startup** | ❌ No | ✅ Yes |
| **NULL Audio Features** | Common | Rare (only if API fails) |
| **Manual Intervention** | Required | Optional |
| **API Endpoint** | ✅ Yes (`/api/music/sync`) | ✅ Yes (improved) |

---

## 📝 Migration Notes

If you have an **existing database** with NULL audio features:

1. **Option 1:** Run backfill script
   ```bash
   python backfill_audio_features.py
   ```

2. **Option 2:** Clear database and let auto-sync repopulate
   ```sql
   TRUNCATE TABLE songs;
   ```
   Then restart backend - it will auto-sync with complete data.

---

## 🐛 Troubleshooting

### **Problem: No audio features fetched**
**Cause:** RapidAPI key not configured

**Solution:**
1. Check `.env` has `RAPIDAPI_KEY`
2. Verify key is valid at [RapidAPI Dashboard](https://rapidapi.com/developer/dashboard)
3. Ensure subscribed to Track Analysis API

---

### **Problem: Rate limit errors (429)**
**Cause:** Too many requests to RapidAPI

**Solution:**
- Wait for rate limit to reset (usually 1 minute)
- Reduce batch size in sync script
- Upgrade RapidAPI plan for higher limits

---

### **Problem: Auto-sync not running**
**Cause:** Database already has songs

**Solution:**
- Auto-sync only runs if database is **empty**
- To force sync: Call `/api/music/sync` endpoint
- Or use standalone script: `python sync_spotify_library.py`

---

## 🎉 Credits

**Unified Sync Architecture** - Optimized for MoodDJ v2.0
- Single source of truth for audio features
- DRY principle (Don't Repeat Yourself)
- Production-ready error handling
- Automatic startup sync

---

## 📞 Support

If you encounter issues:
1. Check logs: `backend/app.log`
2. Verify environment variables in `.env`
3. Test RapidAPI connection: `python backfill_audio_features.py` → Option 1
4. Check database: `SELECT COUNT(*) FROM songs WHERE valence IS NULL;`

---

**Last Updated:** 2025-01-10
**Version:** 2.0 (Unified Sync)
