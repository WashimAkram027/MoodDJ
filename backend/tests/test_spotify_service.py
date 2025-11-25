import pytest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.spotify_service import SpotifyService


class TestSpotifyService:
    """Unit tests for SpotifyService module"""
    
    @pytest.fixture
    def spotify_service(self):
        """Create SpotifyService instance for each test"""
        return SpotifyService()
    
    def test_service_initialization(self, spotify_service):
        """
        Test Case 1: Service Initialization
        
        Purpose: Verify SpotifyService initializes with correct config
        Input: None
        Expected Output: Service with client_id, client_secret, redirect_uri
        Tests: Configuration loading
        """
        assert spotify_service is not None
        assert spotify_service.client_id is not None
        assert spotify_service.client_secret is not None
        assert spotify_service.redirect_uri is not None
        print("✅ Test 1 PASSED: SpotifyService initialized")
    
    def test_detect_mood_from_features_happy(self, spotify_service):
        """
        Test Case 2: Happy Mood Detection from Audio Features
        
        Purpose: Verify correct mood classification for happy songs
        Input: valence=0.8, energy=0.7, tempo=130 (high valence, high energy)
        Expected Output: 'happy'
        Tests: Mood classification algorithm for happy mood
        """
        mood = spotify_service._detect_mood_from_features(
            valence=0.8,
            energy=0.7,
            tempo=130
        )
        
        assert mood == 'happy'
        print("✅ Test 2 PASSED: High valence/energy correctly classified as happy")
    
    def test_detect_mood_from_features_angry(self, spotify_service):
        """
        Test Case 3: Angry Mood Detection from Audio Features
        
        Purpose: Verify correct mood classification for angry songs
        Input: valence=0.2, energy=0.8, tempo=150 (low valence, high energy)
        Expected Output: 'angry'
        Tests: Mood classification algorithm for angry mood
        """
        mood = spotify_service._detect_mood_from_features(
            valence=0.2,
            energy=0.8,
            tempo=150
        )
        
        assert mood == 'angry'
        print("✅ Test 3 PASSED: Low valence/high energy correctly classified as angry")
    
    def test_detect_mood_from_features_neutral(self, spotify_service):
        """
        Test Case 4: Neutral Mood Detection from Audio Features
        
        Purpose: Verify correct mood classification for neutral songs
        Input: valence=0.5, energy=0.5, tempo=100 (medium values)
        Expected Output: 'neutral'
        Tests: Mood classification algorithm for neutral mood
        """
        mood = spotify_service._detect_mood_from_features(
            valence=0.5,
            energy=0.5,
            tempo=100
        )
        
        assert mood == 'neutral'
        print("✅ Test 4 PASSED: Medium values correctly classified as neutral")
    
    @patch('services.spotify_service.execute_query')
    def test_get_songs_for_mood_query_structure(self, mock_query, spotify_service):
        """
        Test Case 5: Song Query Structure for Mood
        
        Purpose: Verify correct SQL query construction for mood filtering
        Input: mood='happy', limit=10, user_id='test_user'
        Expected Output: Query with correct valence/energy/tempo ranges
        Tests: Database query construction and parameter passing
        """
        # Mock database response
        mock_query.return_value = [
            {
                'song_id': 1,
                'title': 'Happy Song',
                'artist': 'Test Artist',
                'valence': 0.8,
                'energy': 0.7,
                'tempo': 120
            }
        ]
        
        # Get songs for happy mood
        songs = spotify_service.get_songs_for_mood('happy', 10, 'test_user')
        
        # Verify query was called
        assert mock_query.called
        
        # Verify query has correct parameters (happy mood ranges)
        call_args = mock_query.call_args
        params = call_args[0][1]  # Second argument is parameters tuple
        
        # Happy mood: valence 0.6-1.0, energy 0.5-1.0, tempo 100-180
        assert params[1] == 0.6  # valence_min
        assert params[2] == 1.0  # valence_max
        assert params[3] == 0.5  # energy_min
        assert params[4] == 1.0  # energy_max
        
        print("✅ Test 5 PASSED: Query constructed with correct mood parameters")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])