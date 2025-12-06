import pytest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.audio_features_service import AudioFeaturesService


class TestAudioFeaturesService:
    """Unit tests for AudioFeaturesService module"""
    
    @pytest.fixture
    def audio_service(self):
        """Create AudioFeaturesService instance for each test"""
        return AudioFeaturesService()
    
    def test_service_initialization(self, audio_service):
        """
        Test Case 1: Service Initialization
        
        Purpose: Verify AudioFeaturesService initializes with RapidAPI config
        Input: None
        Expected Output: Service with rapidapi_key and rapidapi_host
        Tests: Configuration loading from environment variables
        """
        assert audio_service is not None
        assert audio_service.rapidapi_host == "track-analysis.p.rapidapi.com"
        # Check if service knows whether it's enabled or not
        assert hasattr(audio_service, 'enabled')
        print("✅ Test 1 PASSED: AudioFeaturesService initialized")
    
    @patch('services.audio_features_service.requests.get')
    def test_get_audio_features_success(self, mock_get, audio_service):
        """
        Test Case 2: Successful Audio Features Retrieval
        
        Purpose: Verify successful API call and response parsing
        Input: track_id='7s25THrKz86DM225dOYwnr' (valid Spotify ID)
        Expected Output: {'valence': 0.72, 'energy': 0.85, 'tempo': 128.0}
        Tests: API integration, response parsing, data validation
        """
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'tempo': 128.0,
            'energy': 85,      # 0-100 scale
            'happiness': 72    # 0-100 scale (maps to valence)
        }
        mock_get.return_value = mock_response
        
        # Execute
        track_id = "7s25THrKz86DM225dOYwnr"
        result = audio_service.get_audio_features(track_id)
        
        # Assert
        assert result is not None
        assert 'valence' in result
        assert 'energy' in result
        assert 'tempo' in result
        
        # Verify values are in correct range (0.0-1.0 for valence/energy)
        assert 0.0 <= result['valence'] <= 1.0
        assert 0.0 <= result['energy'] <= 1.0
        assert result['tempo'] > 0
        
        # Verify conversion from 0-100 to 0.0-1.0
        assert result['valence'] == 0.72  # 72/100
        assert result['energy'] == 0.85   # 85/100
        assert result['tempo'] == 128.0
        
        print("✅ Test 2 PASSED: Audio features retrieved successfully")
    
    @patch('services.audio_features_service.requests.get')
    def test_get_audio_features_not_found(self, mock_get, audio_service):
        """
        Test Case 3: Track Not Found (404)
        
        Purpose: Verify graceful handling when track doesn't exist in database
        Input: track_id='invalid_track_id'
        Expected Output: None
        Tests: Error handling for missing tracks
        """
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Execute
        result = audio_service.get_audio_features("invalid_track_id")
        
        # Assert
        assert result is None
        print("✅ Test 3 PASSED: 404 handled gracefully")
    
    @patch('services.audio_features_service.requests.get')
    def test_get_audio_features_rate_limit(self, mock_get, audio_service):
        """
        Test Case 4: Rate Limit Handling (429)
        
        Purpose: Verify rate limit detection and retry logic
        Input: Valid track_id but API returns 429
        Expected Output: None (after retries exhausted)
        Tests: Rate limiting resilience
        """
        # Mock rate limit response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '1'}
        mock_get.return_value = mock_response
        
        # Execute (with retry disabled for speed)
        result = audio_service.get_audio_features(
            "test_track", 
            retry_on_rate_limit=False
        )
        
        # Assert
        assert result is None
        print("✅ Test 4 PASSED: Rate limit handled")
    
    @patch('services.audio_features_service.requests.get')
    def test_parse_response_incomplete_data(self, mock_get, audio_service):
        """
        Test Case 5: Incomplete Response Data
        
        Purpose: Verify handling of responses missing required fields
        Input: API response missing 'tempo' field
        Expected Output: None
        Tests: Data validation and error handling
        """
        # Mock incomplete response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'energy': 85,
            'happiness': 72
            # Missing 'tempo'
        }
        mock_get.return_value = mock_response
        
        # Execute
        result = audio_service.get_audio_features("test_track")
        
        # Assert
        assert result is None
        print("✅ Test 5 PASSED: Incomplete data handled")
    
    def test_is_enabled_with_api_key(self, audio_service):
        """
        Test Case 6: Service Enabled Check
        
        Purpose: Verify service correctly reports if RapidAPI key is configured
        Input: None
        Expected Output: Boolean indicating if service is enabled
        Tests: Configuration validation
        """
        is_enabled = audio_service.is_enabled()
        
        # Should be boolean
        assert isinstance(is_enabled, bool)
        print(f"✅ Test 6 PASSED: Service enabled = {is_enabled}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])