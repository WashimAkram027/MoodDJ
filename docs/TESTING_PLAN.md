# MoodDJ Deployment Testing Plan
**Comprehensive Testing Infrastructure for EC2 Deployment**

**Created:** 2025-01-16
**Status:** Implementation Plan
**Purpose:** Ensure all features work on live EC2 deployment before and after code changes

---

## Table of Contents
1. [Overview](#overview)
2. [Testing Strategy](#testing-strategy)
3. [Files to Create](#files-to-create)
4. [Implementation Steps](#implementation-steps)
5. [Testing Workflows](#testing-workflows)
6. [Test Coverage Matrix](#test-coverage-matrix)
7. [Environment Configuration](#environment-configuration)
8. [Usage Instructions](#usage-instructions)

---

## Overview

### Problem Statement
Currently, code works locally but may have issues when deployed to EC2 due to:
- Environment variable differences (localhost vs domain)
- OAuth redirect URI mismatches
- WebSocket connection issues
- Session storage differences (filesystem vs Redis)
- HTTPS/HTTP mixed content issues
- External API rate limiting

### Solution
Create automated testing scripts and comprehensive documentation to:
- Test all API endpoints against live deployment
- Validate WebSocket connections
- Verify OAuth flows end-to-end
- Check database connectivity
- Test external API integrations
- Generate detailed reports
- Provide step-by-step testing guide

### Benefits
- ✅ Catch deployment issues before users see them
- ✅ Verify every feature works on live environment
- ✅ Automated testing reduces manual effort
- ✅ Consistent testing process across team
- ✅ Detailed reports for debugging
- ✅ Pre-deployment validation checklist

---

## Testing Strategy

### Testing Levels

1. **Unit Tests** (Future - Not in this plan)
   - Individual function testing
   - Isolated component testing

2. **API Integration Tests** ✅ (Implemented in this plan)
   - Test all REST endpoints
   - Validate request/response formats
   - Check authentication flow
   - Test error handling

3. **WebSocket Tests** ✅ (Implemented in this plan)
   - Connection establishment
   - Event emission/reception
   - Reconnection logic
   - Concurrent connections

4. **Database Tests** ✅ (Implemented in this plan)
   - RDS connectivity
   - Schema validation
   - Query performance
   - Data integrity

5. **End-to-End Tests** ✅ (Implemented in this plan)
   - Complete user workflows
   - OAuth flow
   - Library sync
   - Mood detection → Recommendation → Playback

6. **External API Tests** ✅ (Implemented in this plan)
   - Spotify API connectivity
   - RapidAPI connectivity
   - Rate limit handling
   - Credential validation

### Testing Environments

- **Local:** `http://127.0.0.1:5000` (for development)
- **Deployed:** Configurable via `config.yaml`
  - EC2 Public IP: `http://<EC2_IP>:5000`
  - Custom Domain: `http://<DOMAIN>:5000`
  - HTTPS (future): `https://<DOMAIN>`

### Test Execution Methods

1. **Automated Scripts** (Primary method)
   - Python scripts for API/database tests
   - Shell script for running full suite
   - Generates HTML reports

2. **Manual Testing Guide** (Backup/verification)
   - Step-by-step procedures
   - Browser-based testing
   - Visual verification

3. **CI/CD Integration** (Optional future enhancement)
   - GitHub Actions workflow
   - Automated on every push
   - Deployment gates

---

## Files to Create

### Directory Structure

```
MoodDJ/
├── tests/
│   └── deployment/
│       ├── test_api_endpoints.py       # API endpoint tests
│       ├── test_websocket.py           # WebSocket tests
│       ├── test_database.py            # Database tests
│       ├── test_integration.py         # E2E workflow tests
│       ├── test_external_apis.py       # External API tests
│       ├── config.yaml                 # Test configuration
│       ├── requirements.txt            # Test dependencies
│       ├── run_all_tests.sh            # Master test runner
│       ├── reports/                    # Test reports (gitignored)
│       └── logs/                       # Test logs (gitignored)
│
├── TESTING_GUIDE.md                    # Comprehensive testing documentation
├── PRE_DEPLOYMENT_CHECKLIST.md         # Quick pre-deployment checklist
└── TESTING_PLAN.md                     # This file
```

---

## File Specifications

### 1. TESTING_GUIDE.md

**Purpose:** Comprehensive testing documentation
**Length:** ~500 lines
**Sections:**
- Complete API endpoint reference with test procedures
- Frontend feature testing workflows
- Environment-specific configurations
- Step-by-step testing checklist
- Common issues and debugging
- Pre-deployment verification
- Manual testing procedures
- Automated testing instructions
- Report interpretation guide

**Key Content:**
- All 20+ endpoints documented
- Manual test procedures for each feature
- Expected responses for each test
- Troubleshooting for common failures
- Screenshots/examples (future enhancement)

---

### 2. test_api_endpoints.py

**Purpose:** Automated API endpoint testing
**Technology:** Python + requests library
**Lines:** ~400 lines

**Features:**
- Tests all 20+ API endpoints
- Configurable base URL (from config.yaml)
- Session management for authenticated endpoints
- Detailed logging
- JSON report generation
- Color-coded console output
- Error screenshots/logs

**Test Coverage:**

#### Authentication Endpoints (6 tests)
```python
def test_health_check():
    """GET /api/health - Should return 200 with status"""

def test_login_initiate():
    """GET /api/auth/login - Should return auth_url"""

def test_auth_status_no_session():
    """GET /api/auth/status - Should return authenticated=false"""

def test_auth_status_with_session():
    """GET /api/auth/status - Should return authenticated=true"""

def test_logout():
    """POST /api/auth/logout - Should clear session"""

def test_get_profile():
    """GET /api/auth/profile - Should return user data"""
```

#### Music Endpoints (6 tests)
```python
def test_recommend_happy():
    """POST /api/music/recommend - mood=happy"""

def test_recommend_sad():
    """POST /api/music/recommend - mood=sad"""

def test_sync_status():
    """GET /api/music/sync/status - Check sync state"""

def test_sync_library():
    """POST /api/music/sync - Sync with limit=10"""

def test_current_playback():
    """GET /api/music/current - Get playback state"""

def test_play_track():
    """POST /api/music/play - Play specific track"""
```

#### Mood Endpoints (5 tests)
```python
def test_detect_mood_valid_image():
    """POST /api/mood/detect - Valid base64 image"""

def test_detect_mood_invalid_image():
    """POST /api/mood/detect - Invalid image data"""

def test_log_mood():
    """POST /api/mood/log - Log mood session"""

def test_get_mood_history():
    """GET /api/mood/history - Get user mood history"""

def test_get_mood_stats():
    """GET /api/mood/stats - Get mood statistics"""
```

**Report Format:**
```json
{
  "timestamp": "2025-01-16T10:30:00Z",
  "environment": "https://mooddj.com",
  "total_tests": 17,
  "passed": 15,
  "failed": 2,
  "skipped": 0,
  "duration_seconds": 45.3,
  "results": [
    {
      "test_name": "test_health_check",
      "status": "PASSED",
      "duration_ms": 234,
      "response_code": 200,
      "response_data": {"status": "healthy"}
    },
    {
      "test_name": "test_recommend_happy",
      "status": "FAILED",
      "duration_ms": 1234,
      "error": "No songs found for mood: happy",
      "traceback": "..."
    }
  ]
}
```

---

### 3. test_websocket.py

**Purpose:** Test WebSocket/Socket.IO connections
**Technology:** Python + python-socketio
**Lines:** ~200 lines

**Features:**
- Connect to deployed WebSocket server
- Test all Socket.IO events
- Validate bidirectional communication
- Test reconnection logic
- Test concurrent connections
- Measure latency

**Test Coverage:**

```python
def test_connection():
    """Test basic WebSocket connection"""

def test_mood_update_event():
    """Test sending mood_update event"""

def test_mood_changed_event():
    """Test receiving mood_changed broadcast"""

def test_start_detection():
    """Test start_detection event"""

def test_stop_detection():
    """Test stop_detection event"""

def test_reconnection():
    """Test automatic reconnection after disconnect"""

def test_concurrent_connections():
    """Test multiple simultaneous connections"""

def test_event_latency():
    """Measure round-trip latency for events"""
```

**Example Test:**
```python
import socketio
import time

def test_mood_update():
    sio = socketio.Client()

    # Connect
    sio.connect('http://your-domain.com:5000')
    assert sio.connected, "Failed to connect to WebSocket"

    # Define event handler
    received_mood = []

    @sio.on('mood_changed')
    def on_mood_changed(data):
        received_mood.append(data)

    # Send mood update
    sio.emit('mood_update', {'mood': 'happy', 'confidence': 0.87})

    # Wait for response
    time.sleep(2)

    # Verify
    assert len(received_mood) > 0, "No mood_changed event received"
    assert received_mood[0]['mood'] == 'happy'

    sio.disconnect()
```

---

### 4. test_database.py

**Purpose:** Test RDS MySQL database connectivity and integrity
**Technology:** Python + mysql-connector-python
**Lines:** ~250 lines

**Features:**
- Connect to RDS from external location
- Validate schema structure
- Test critical queries
- Check indexes exist
- Verify foreign key constraints
- Test connection pooling
- Measure query performance

**Test Coverage:**

```python
def test_connection():
    """Test basic database connection"""

def test_tables_exist():
    """Verify all 5 tables exist"""

def test_users_schema():
    """Validate users table schema"""

def test_songs_schema():
    """Validate songs table schema"""

def test_indexes_exist():
    """Check required indexes on songs table"""

def test_song_recommendation_query():
    """Test mood-based song query performance"""

def test_user_library_query():
    """Test user-specific song retrieval"""

def test_mood_logging():
    """Test inserting mood session"""

def test_foreign_key_constraints():
    """Verify FK constraints work"""
```

**Example Test:**
```python
import mysql.connector

def test_song_recommendation_query():
    """Test mood-based recommendation query"""

    conn = mysql.connector.connect(
        host=config['database']['host'],
        user=config['database']['user'],
        password=config['database']['password'],
        database=config['database']['name']
    )

    cursor = conn.cursor(dictionary=True)

    # Test happy mood query
    query = """
        SELECT s.song_id, s.title, s.artist, s.valence, s.energy
        FROM songs s
        INNER JOIN moods m ON s.valence BETWEEN m.target_valence_min AND m.target_valence_max
        WHERE m.mood_name = 'happy'
        LIMIT 10
    """

    start_time = time.time()
    cursor.execute(query)
    results = cursor.fetchall()
    duration = time.time() - start_time

    # Assertions
    assert len(results) > 0, "No songs found for happy mood"
    assert duration < 1.0, f"Query too slow: {duration}s"
    assert all('valence' in r for r in results), "Missing valence data"

    cursor.close()
    conn.close()
```

---

### 5. test_integration.py

**Purpose:** End-to-end workflow testing
**Technology:** Python + Selenium WebDriver
**Lines:** ~350 lines

**Features:**
- Browser automation with Selenium
- Test complete user workflows
- Screenshot on failures
- Multi-browser support (Chrome, Firefox)
- Headless mode for CI/CD
- Video recording (optional)

**Test Coverage:**

```python
def test_oauth_flow():
    """
    Complete OAuth flow:
    1. Visit home page
    2. Click "Connect with Spotify"
    3. Login to Spotify (if needed)
    4. Authorize application
    5. Redirected to dashboard
    6. Verify authenticated
    """

def test_library_sync_workflow():
    """
    Library sync workflow:
    1. Login to dashboard
    2. Check sync status (should show "Needs Sync")
    3. Click "Sync Library" button
    4. Wait for sync to complete
    5. Verify songs in database
    6. Check sync status (should show "Synced")
    """

def test_mood_detection_workflow():
    """
    Mood detection workflow:
    1. Login to dashboard
    2. Grant camera permission
    3. Start mood detection
    4. Wait for mood to be detected
    5. Verify mood displayed in UI
    6. Verify recommendations shown
    """

def test_music_playback_workflow():
    """
    Music playback workflow:
    1. Login to dashboard
    2. Detect mood (or select manually)
    3. View recommendations
    4. Click play on a song
    5. Verify Spotify player starts
    6. Verify song playing
    """
```

**Example Test:**
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_oauth_flow():
    """Test complete OAuth flow"""

    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)

    try:
        # Step 1: Visit home page
        driver.get(config['deployment']['frontend_url'])

        # Step 2: Click "Connect with Spotify"
        connect_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Connect with Spotify')]"))
        )
        connect_btn.click()

        # Step 3: Should redirect to Spotify login
        wait.until(EC.url_contains("accounts.spotify.com"))
        assert "spotify.com" in driver.current_url

        # Note: Actual login would require test Spotify account
        # For now, verify redirect happened

        print("✓ OAuth flow initiated successfully")

    except Exception as e:
        driver.save_screenshot("tests/deployment/reports/oauth_flow_error.png")
        raise e
    finally:
        driver.quit()
```

---

### 6. test_external_apis.py

**Purpose:** Test external API integrations
**Technology:** Python + requests
**Lines:** ~150 lines

**Features:**
- Test Spotify API connectivity
- Test RapidAPI connectivity
- Validate API credentials
- Test rate limit handling
- Check error responses

**Test Coverage:**

```python
def test_spotify_api_connection():
    """Test basic Spotify API connectivity"""

def test_spotify_get_user_profile():
    """Test fetching Spotify user profile"""

def test_spotify_get_user_tracks():
    """Test fetching user's saved tracks"""

def test_rapidapi_connection():
    """Test basic RapidAPI connectivity"""

def test_rapidapi_get_audio_features():
    """Test getting audio features for a track"""

def test_rapidapi_rate_limiting():
    """Test rate limit handling (exponential backoff)"""

def test_spotify_token_refresh():
    """Test Spotify token refresh mechanism"""
```

**Example Test:**
```python
import requests
import os

def test_rapidapi_get_audio_features():
    """Test RapidAPI SoundNet API"""

    track_id = "3n3Ppam7vgaVa1iaRUc9Lp"  # Mr. Blue Sky

    url = f"https://track-analysis.p.rapidapi.com/pktx/spotify/{track_id}"
    headers = {
        "x-rapidapi-key": config['external_apis']['rapidapi_key'],
        "x-rapidapi-host": "track-analysis.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)

    # Assertions
    assert response.status_code == 200, f"Failed to get audio features: {response.status_code}"

    data = response.json()
    assert 'valence' in data, "Missing valence in response"
    assert 'energy' in data, "Missing energy in response"
    assert 'tempo' in data, "Missing tempo in response"

    assert 0 <= data['valence'] <= 1, "Invalid valence value"
    assert 0 <= data['energy'] <= 1, "Invalid energy value"
    assert data['tempo'] > 0, "Invalid tempo value"

    print(f"✓ RapidAPI test passed - Valence: {data['valence']}, Energy: {data['energy']}")
```

---

### 7. config.yaml

**Purpose:** Centralized test configuration
**Format:** YAML
**Lines:** ~50 lines

**Structure:**
```yaml
# Deployment configuration
deployment:
  environment: "production"  # or "staging", "local"
  domain: "your-ec2-domain.com"
  backend_url: "http://your-ec2-domain.com:5000"
  frontend_url: "http://your-ec2-domain.com"
  use_https: false  # Set to true when HTTPS is configured

# Test user credentials (for automated testing)
test_user:
  spotify_email: "test@example.com"
  spotify_password: "test_password"  # Store securely, not in repo
  # Or use pre-authenticated session token
  session_token: "..."

# Database configuration
database:
  host: "mooddj-database.c9wc8gkmgine.ca-central-1.rds.amazonaws.com"
  user: "admin"
  password: "Tensorflow_python786"  # Use env var in production
  name: "mooddj"
  port: 3306

# External API credentials
external_apis:
  spotify:
    client_id: "987339e67f5a49bf8225ca6c944f41ca"
    client_secret: "913856a259f84195b6d769288f481f4a"
  rapidapi:
    key: "a07bdb5faemsh4e902b0093f5565p1f95b8jsndba5b9cbb3c8"
    host: "track-analysis.p.rapidapi.com"

# Test configuration
test_settings:
  timeout_seconds: 30
  retry_attempts: 3
  generate_html_report: true
  save_screenshots: true
  verbose_logging: true

# WebSocket configuration
websocket:
  connect_timeout: 10
  event_timeout: 5
  reconnection_attempts: 3

# Test data
test_data:
  sample_track_id: "3n3Ppam7vgaVa1iaRUc9Lp"  # Mr. Blue Sky
  sample_moods: ["happy", "sad", "angry", "neutral"]
  library_sync_limit: 10  # Number of tracks to sync in test
```

**Security Note:**
- Add `.gitignore` entry for `config.yaml`
- Create `config.example.yaml` with placeholder values
- Use environment variables for sensitive data

---

### 8. requirements.txt

**Purpose:** Python dependencies for test scripts
**Lines:** ~15 lines

```txt
# Testing framework
pytest==7.4.3
pytest-html==4.1.1

# HTTP requests
requests==2.31.0

# WebSocket testing
python-socketio==5.10.0

# Database testing
mysql-connector-python==8.2.0

# Browser automation
selenium==4.15.2

# Configuration
PyYAML==6.0.1

# Utilities
colorama==0.4.6  # Colored console output
python-dotenv==1.0.0
```

---

### 9. run_all_tests.sh

**Purpose:** Master test runner script
**Technology:** Bash
**Lines:** ~150 lines

**Features:**
- Runs all test scripts in sequence
- Generates HTML report
- Logs results with timestamps
- Sends email/Slack notifications (optional)
- Exit codes for CI/CD integration
- Parallel test execution (optional)

**Structure:**
```bash
#!/bin/bash

# run_all_tests.sh - Master test runner for MoodDJ deployment

set -e  # Exit on error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_DIR="$SCRIPT_DIR/reports"
LOG_DIR="$SCRIPT_DIR/logs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/test_run_$TIMESTAMP.log"
REPORT_FILE="$REPORT_DIR/test_report_$TIMESTAMP.html"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

# Main execution
main() {
    log_info "Starting MoodDJ deployment tests at $(date)"
    log_info "Log file: $LOG_FILE"

    # Check prerequisites
    log_info "Checking prerequisites..."
    python3 --version || { log_error "Python3 not found"; exit 1; }

    # Install dependencies
    log_info "Installing test dependencies..."
    pip3 install -r requirements.txt > /dev/null 2>&1 || log_warning "Failed to install some dependencies"

    # Initialize results
    TOTAL_TESTS=0
    PASSED_TESTS=0
    FAILED_TESTS=0

    # Test 1: API Endpoints
    log_info "Running API endpoint tests..."
    if python3 test_api_endpoints.py; then
        log_info "✓ API endpoint tests passed"
        ((PASSED_TESTS++))
    else
        log_error "✗ API endpoint tests failed"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))

    # Test 2: WebSocket
    log_info "Running WebSocket tests..."
    if python3 test_websocket.py; then
        log_info "✓ WebSocket tests passed"
        ((PASSED_TESTS++))
    else
        log_error "✗ WebSocket tests failed"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))

    # Test 3: Database
    log_info "Running database tests..."
    if python3 test_database.py; then
        log_info "✓ Database tests passed"
        ((PASSED_TESTS++))
    else
        log_error "✗ Database tests failed"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))

    # Test 4: External APIs
    log_info "Running external API tests..."
    if python3 test_external_apis.py; then
        log_info "✓ External API tests passed"
        ((PASSED_TESTS++))
    else
        log_error "✗ External API tests failed"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))

    # Test 5: Integration (optional, takes longer)
    if [ "$SKIP_INTEGRATION" != "true" ]; then
        log_info "Running integration tests..."
        if python3 test_integration.py; then
            log_info "✓ Integration tests passed"
            ((PASSED_TESTS++))
        else
            log_error "✗ Integration tests failed"
            ((FAILED_TESTS++))
        fi
        ((TOTAL_TESTS++))
    fi

    # Generate summary
    log_info "========================================="
    log_info "Test Summary"
    log_info "========================================="
    log_info "Total Tests: $TOTAL_TESTS"
    log_info "Passed: $PASSED_TESTS"
    log_info "Failed: $FAILED_TESTS"
    log_info "========================================="

    # Generate HTML report
    log_info "Generating HTML report: $REPORT_FILE"
    generate_html_report

    # Send notifications (optional)
    if [ "$SEND_NOTIFICATIONS" == "true" ]; then
        send_notification
    fi

    # Exit with appropriate code
    if [ $FAILED_TESTS -gt 0 ]; then
        log_error "Tests failed!"
        exit 1
    else
        log_info "All tests passed!"
        exit 0
    fi
}

generate_html_report() {
    # Generate simple HTML report
    cat > "$REPORT_FILE" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>MoodDJ Test Report - $TIMESTAMP</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .passed { color: green; }
        .failed { color: red; }
        .summary { background: #f0f0f0; padding: 15px; margin: 20px 0; }
    </style>
</head>
<body>
    <h1>MoodDJ Deployment Test Report</h1>
    <p>Generated: $(date)</p>
    <div class="summary">
        <h2>Summary</h2>
        <p>Total Tests: $TOTAL_TESTS</p>
        <p class="passed">Passed: $PASSED_TESTS</p>
        <p class="failed">Failed: $FAILED_TESTS</p>
    </div>
    <!-- Detailed results would be added here -->
</body>
</html>
EOF
}

send_notification() {
    # Placeholder for email/Slack notification
    log_info "Sending notification (not implemented)"
}

# Run main
main "$@"
```

**Usage:**
```bash
# Run all tests
./run_all_tests.sh

# Skip integration tests (faster)
SKIP_INTEGRATION=true ./run_all_tests.sh

# With notifications
SEND_NOTIFICATIONS=true ./run_all_tests.sh
```

---

### 10. TESTING_GUIDE.md

**Purpose:** Comprehensive testing documentation
**Length:** ~800 lines
**Audience:** Developers and testers

**Table of Contents:**
1. Introduction
2. Quick Start
3. Manual Testing Procedures
4. Automated Testing
5. API Endpoint Reference
6. Feature Testing Workflows
7. Environment Setup
8. Troubleshooting
9. Report Interpretation
10. Pre-Deployment Checklist

**Key Sections:**

#### Manual Testing Procedures
- Step-by-step instructions for each feature
- Expected results
- Screenshots (future)
- Common issues

#### Automated Testing
- How to run each test script
- How to configure for your deployment
- How to interpret results
- How to add new tests

#### API Endpoint Reference
- Complete list of all endpoints
- Request/response examples
- Authentication requirements
- Error codes and handling

---

### 11. PRE_DEPLOYMENT_CHECKLIST.md

**Purpose:** Quick checklist before deployment
**Length:** ~100 lines
**Format:** Interactive checklist

**Structure:**
```markdown
# Pre-Deployment Checklist

Run through this checklist before every deployment to EC2.

## Environment Verification

- [ ] Backend `.env` file updated with production values
  - [ ] `SPOTIFY_REDIRECT_URI` points to deployment domain
  - [ ] `FRONTEND_URL` points to deployment domain
  - [ ] `DB_HOST` is RDS endpoint (not localhost)
  - [ ] `SESSION_TYPE` is `redis` (not filesystem)
  - [ ] `SECRET_KEY` is unique and strong

- [ ] Frontend `.env` file updated with production values
  - [ ] `REACT_APP_API_URL` points to deployment domain
  - [ ] `REACT_APP_WS_URL` points to deployment domain

- [ ] Spotify Developer Dashboard updated
  - [ ] Redirect URI matches deployment domain

## Quick Smoke Tests

- [ ] Backend health check: `curl http://<DOMAIN>:5000/api/health`
- [ ] Frontend loads: Visit `http://<DOMAIN>` in browser
- [ ] Database connection: `python3 tests/deployment/test_database.py`

## Run Automated Tests

- [ ] `cd tests/deployment`
- [ ] `./run_all_tests.sh`
- [ ] Review report: `open reports/test_report_*.html`
- [ ] All tests passed (or failures documented)

## Deployment

- [ ] SSH into EC2: `ssh -i mooddj-key.pem ubuntu@<EC2_IP>`
- [ ] Pull latest code: `cd ~/MoodDJ && git pull`
- [ ] Rebuild containers: `docker-compose down && docker-compose up -d --build`
- [ ] Check logs: `docker-compose logs -f`
- [ ] Verify services running: `docker-compose ps`

## Post-Deployment Verification

- [ ] Frontend accessible from browser
- [ ] Backend health check responds
- [ ] OAuth login works
- [ ] Camera detection works
- [ ] Music recommendations work
- [ ] Playback works

## If Issues Found

- [ ] Check logs: `docker-compose logs backend`
- [ ] Check environment variables: `docker-compose exec backend env | grep SPOTIFY`
- [ ] Rollback if needed: `git checkout <previous-commit> && docker-compose up -d --build`
- [ ] Document issue in GitHub Issues
```

---

## Implementation Steps

### Phase 1: Setup (30 minutes)
1. Create directory structure
   ```bash
   mkdir -p tests/deployment/{reports,logs}
   cd tests/deployment
   ```

2. Create `requirements.txt`
3. Create `config.example.yaml` (template)
4. Copy to `config.yaml` and fill in values
5. Install dependencies: `pip3 install -r requirements.txt`

### Phase 2: Basic Tests (2 hours)
1. Write `test_api_endpoints.py`
   - Start with health check
   - Add authentication tests
   - Add music endpoint tests
   - Add mood endpoint tests

2. Test locally first:
   ```bash
   # Update config.yaml to point to local
   python3 test_api_endpoints.py
   ```

3. Test against deployment:
   ```bash
   # Update config.yaml to point to EC2
   python3 test_api_endpoints.py
   ```

### Phase 3: Advanced Tests (3 hours)
1. Write `test_websocket.py`
2. Write `test_database.py`
3. Write `test_external_apis.py`
4. Test each script individually

### Phase 4: Integration Tests (2 hours)
1. Install Selenium WebDriver
2. Write `test_integration.py`
3. Start with OAuth flow
4. Add other workflows

### Phase 5: Master Runner (1 hour)
1. Write `run_all_tests.sh`
2. Test running all scripts
3. Verify report generation
4. Test error handling

### Phase 6: Documentation (2 hours)
1. Write `TESTING_GUIDE.md`
2. Write `PRE_DEPLOYMENT_CHECKLIST.md`
3. Update main `README.md` with testing section
4. Create examples and screenshots

### Phase 7: Refinement (1 hour)
1. Add error handling
2. Improve logging
3. Add more assertions
4. Optimize test execution time

**Total Estimated Time:** 11-12 hours

---

## Testing Workflows

### Daily Development Workflow
```bash
# 1. Make code changes locally
# 2. Test locally
docker-compose up --build

# 3. Run quick smoke tests
cd tests/deployment
python3 test_api_endpoints.py  # ~2 minutes

# 4. If passing, commit and push
git add .
git commit -m "Add feature X"
git push
```

### Before Deployment Workflow
```bash
# 1. Update config.yaml with deployment URLs
# 2. Run full test suite
cd tests/deployment
./run_all_tests.sh  # ~5-10 minutes

# 3. Review report
open reports/test_report_*.html

# 4. If all passed, deploy
ssh -i mooddj-key.pem ubuntu@<EC2_IP>
cd ~/MoodDJ
git pull
docker-compose down && docker-compose up -d --build

# 5. Run tests against live deployment
cd tests/deployment
./run_all_tests.sh

# 6. If passed, deployment successful
```

### Weekly Regression Testing
```bash
# Run full test suite including integration tests
cd tests/deployment
SKIP_INTEGRATION=false ./run_all_tests.sh

# Review results
# Document any failures
# Create GitHub issues for bugs
```

---

## Test Coverage Matrix

### API Endpoints Coverage

| Endpoint | Method | Manual Test | Automated Test | Integration Test |
|----------|--------|-------------|----------------|------------------|
| `/api/health` | GET | ✅ | ✅ | ✅ |
| `/api/auth/login` | GET | ✅ | ✅ | ✅ |
| `/api/auth/callback` | GET | ✅ | ⚠️ | ✅ |
| `/api/auth/status` | GET | ✅ | ✅ | ✅ |
| `/api/auth/logout` | POST | ✅ | ✅ | ✅ |
| `/api/music/recommend` | POST | ✅ | ✅ | ✅ |
| `/api/music/play` | POST | ✅ | ✅ | ✅ |
| `/api/music/sync` | POST | ✅ | ✅ | ✅ |
| `/api/music/sync/status` | GET | ✅ | ✅ | ✅ |
| `/api/mood/detect` | POST | ✅ | ✅ | ✅ |
| `/api/mood/log` | POST | ✅ | ✅ | - |
| `/api/mood/history` | GET | ✅ | ✅ | - |

✅ = Covered, ⚠️ = Partial, - = Not needed

### Feature Coverage

| Feature | Manual Test | Automated Test | Browser Test |
|---------|-------------|----------------|--------------|
| OAuth Login | ✅ | ⚠️ | ✅ |
| Camera Access | ✅ | - | ✅ |
| Mood Detection | ✅ | ✅ | ✅ |
| Music Recommendations | ✅ | ✅ | ✅ |
| Music Playback | ✅ | ⚠️ | ✅ |
| Library Sync | ✅ | ✅ | ✅ |
| Session Persistence | ✅ | ✅ | ✅ |
| WebSocket Communication | ✅ | ✅ | ✅ |

---

## Environment Configuration

### Local Testing Configuration
```yaml
deployment:
  environment: "local"
  domain: "127.0.0.1"
  backend_url: "http://127.0.0.1:5000"
  frontend_url: "http://127.0.0.1:3000"
  use_https: false
```

### EC2 Deployment Configuration
```yaml
deployment:
  environment: "production"
  domain: "your-ec2-domain.com"
  backend_url: "http://your-ec2-domain.com:5000"
  frontend_url: "http://your-ec2-domain.com"
  use_https: false
```

### HTTPS Configuration (Future)
```yaml
deployment:
  environment: "production"
  domain: "mooddj.com"
  backend_url: "https://api.mooddj.com"
  frontend_url: "https://mooddj.com"
  use_https: true
```

---

## Usage Instructions

### Running Individual Tests

```bash
cd tests/deployment

# API tests only
python3 test_api_endpoints.py

# WebSocket tests only
python3 test_websocket.py

# Database tests only
python3 test_database.py

# External API tests only
python3 test_external_apis.py

# Integration tests only (slow)
python3 test_integration.py
```

### Running All Tests

```bash
cd tests/deployment

# Full test suite
./run_all_tests.sh

# Fast tests only (skip integration)
SKIP_INTEGRATION=true ./run_all_tests.sh

# Verbose output
VERBOSE=true ./run_all_tests.sh
```

### Viewing Reports

```bash
# Latest report
cd tests/deployment/reports
ls -lt  # Find latest report
open test_report_*.html  # macOS
# Or open in browser on Windows/Linux
```

### Adding New Tests

1. Create new test function in appropriate file
2. Follow naming convention: `test_<feature_name>`
3. Add docstring explaining what it tests
4. Use assertions to validate behavior
5. Add to test runner if new file created

Example:
```python
def test_new_feature():
    """Test description here"""
    # Arrange
    url = f"{base_url}/api/new-endpoint"
    data = {"param": "value"}

    # Act
    response = requests.post(url, json=data)

    # Assert
    assert response.status_code == 200
    assert response.json()['success'] == True
```

---

## Success Criteria

After full implementation, you should have:

✅ **Automated Testing**
- All API endpoints tested
- WebSocket tested
- Database tested
- External APIs tested
- E2E workflows tested

✅ **Documentation**
- Comprehensive testing guide
- Pre-deployment checklist
- Implementation plan (this document)

✅ **Tooling**
- One command to run all tests
- HTML reports generated
- Logs saved for debugging

✅ **Confidence**
- Catch bugs before deployment
- Verify all features work on live
- Consistent testing process

---

## Next Steps After Implementation

1. **Run Initial Baseline**
   - Run tests against current deployment
   - Document any failures
   - Fix critical issues

2. **Integrate into Workflow**
   - Add to pre-deployment checklist
   - Train team on usage
   - Document in README

3. **Continuous Improvement**
   - Add more test cases as bugs are found
   - Optimize test execution time
   - Add CI/CD integration

4. **Advanced Features** (Future)
   - Performance testing
   - Load testing
   - Security testing
   - Mobile testing

---

**Status:** Ready for Implementation
**Next Action:** Create directory structure and start with Phase 1

