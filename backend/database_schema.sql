-- Create database
DROP DATABASE IF EXISTS mooddj;
CREATE DATABASE mooddj;
USE mooddj;

-- Table: Users
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    spotify_id VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    email VARCHAR(150),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: Moods
CREATE TABLE moods (
    mood_id INT AUTO_INCREMENT PRIMARY KEY,
    mood_name VARCHAR(50) NOT NULL,
    target_valence_min FLOAT DEFAULT 0.0,
    target_valence_max FLOAT DEFAULT 1.0,
    target_energy_min FLOAT DEFAULT 0.0,
    target_energy_max FLOAT DEFAULT 1.0,
    target_tempo_min FLOAT DEFAULT 60,
    target_tempo_max FLOAT DEFAULT 180
);

-- Table: Songs
CREATE TABLE songs (
    song_id INT AUTO_INCREMENT PRIMARY KEY,
    spotify_song_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    artist VARCHAR(200),
    album VARCHAR(200),
    duration_ms INT,
    valence FLOAT,
    energy FLOAT,
    tempo FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_valence (valence),
    INDEX idx_energy (energy),
    INDEX idx_tempo (tempo)
);

-- Table: Mood Sessions (for tracking mood detections)
CREATE TABLE mood_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT DEFAULT 1,
    detected_mood VARCHAR(50) NOT NULL,
    confidence_score FLOAT DEFAULT 1.0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_timestamp (user_id, timestamp)
);

-- Junction Table: UserSongs (links users ↔ songs ↔ moods)
CREATE TABLE user_songs (
    user_song_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    song_id INT NOT NULL,
    mood_id INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES songs(song_id) ON DELETE CASCADE,
    FOREIGN KEY (mood_id) REFERENCES moods(mood_id) ON DELETE CASCADE
);

-- Insert default moods with audio feature parameters
INSERT INTO moods (mood_name, target_valence_min, target_valence_max, target_energy_min, target_energy_max, target_tempo_min, target_tempo_max) 
VALUES 
    ('happy', 0.6, 1.0, 0.5, 1.0, 100, 180),
    ('sad', 0.0, 0.4, 0.2, 0.5, 60, 100),
    ('excited', 0.7, 1.0, 0.7, 1.0, 120, 200),
    ('calm', 0.3, 0.7, 0.2, 0.5, 60, 100),
    ('neutral', 0.4, 0.7, 0.4, 0.7, 80, 130),
    ('angry', 0.0, 0.4, 0.6, 1.0, 120, 180),
    ('surprised', 0.5, 1.0, 0.6, 1.0, 110, 180);

-- Create default user for testing
INSERT INTO users (spotify_id, display_name, email) 
VALUES ('demo_user', 'Demo User', 'demo@mooddj.com');