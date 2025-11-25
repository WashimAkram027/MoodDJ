import pytest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestMoodRoutes:
    """Unit tests for Mood Routes module"""
    
    @pytest.fixture
    def client(self):
        """Create Flask test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @patch('routes.mood_routes.mood_detector.detect_from_base64')
    def test_detect_mood_endpoint_success(self, mock_detect, client):
        """
        Test Case 1: Mood Detection Success
        
        Purpose: Verify /api/mood/detect processes image and returns mood
        Input: POST with base64 image data
        Expected Output: {'mood': 'happy', 'confidence': 0.85, 'detected': True}
        Tests: Mood detection endpoint functionality
        """
        # Mock mood detection
        mock_detect.return_value = {
            'mood': 'happy',
            'confidence': 0.85,
            'detected': True,
            'features': {'mouth_width': 0.6}
        }
        
        # Execute
        response = client.post('/api/mood/detect', json={
            'image': 'data:image/jpeg;base64,/9j/4AAQ...'
        })
        data = response.get_json()
        
        # Assert
        assert response.status_code == 200
        assert data['mood'] == 'happy'
        assert data['confidence'] == 0.85
        assert data['detected'] == True
        print("✅ Test 1 PASSED: Mood detection successful")
    
    def test_detect_mood_endpoint_missing_image(self, client):
        """
        Test Case 2: Missing Image Data
        
        Purpose: Verify error handling when image is not provided
        Input: POST with no image data
        Expected Output: 400 error with error message
        Tests: Input validation
        """
        # Execute
        response = client.post('/api/mood/detect', json={})
        
        # Assert
        assert response.status_code == 400
        assert 'error' in response.get_json()
        print("✅ Test 2 PASSED: Missing image handled")
    
    @patch('routes.mood_routes.execute_query')
    def test_log_mood_endpoint_success(self, mock_query, client):
        """
        Test Case 3: Log Mood Success
        
        Purpose: Verify mood logging to database
        Input: POST with mood and confidence data
        Expected Output: {'success': True, 'session_id': 123}
        Tests: Mood persistence functionality
        """
        # Mock database insert
        mock_query.return_value = 123  # session_id
        
        # Execute
        response = client.post('/api/mood/log', json={
            'mood': 'angry',
            'confidence': 0.75,
            'user_id': 1
        })
        data = response.get_json()
        
        # Assert
        assert response.status_code == 201
        assert data['success'] == True
        assert data['session_id'] == 123
        print("✅ Test 3 PASSED: Mood logged successfully")
    
    def test_log_mood_endpoint_missing_mood(self, client):
        """
        Test Case 4: Log Mood Missing Data
        
        Purpose: Verify error handling when mood is missing
        Input: POST with no mood data
        Expected Output: 400 error
        Tests: Input validation for logging
        """
        # Execute
        response = client.post('/api/mood/log', json={
            'confidence': 0.8
        })
        
        # Assert
        assert response.status_code == 400
        assert 'error' in response.get_json()
        print("✅ Test 4 PASSED: Missing mood handled")
    
    @patch('routes.mood_routes.execute_query')
    def test_get_mood_history_endpoint(self, mock_query, client):
        """
        Test Case 5: Get Mood History
        
        Purpose: Verify mood history retrieval
        Input: GET /api/mood/history?user_id=1&limit=10
        Expected Output: Array of mood history records
        Tests: History retrieval functionality
        """
        # Mock database query
        mock_query.return_value = [
            {'detected_mood': 'happy', 'confidence_score': 0.8, 'timestamp': '2024-01-01'},
            {'detected_mood': 'neutral', 'confidence_score': 0.6, 'timestamp': '2024-01-02'}
        ]
        
        # Execute
        response = client.get('/api/mood/history?user_id=1&limit=10')
        data = response.get_json()
        
        # Assert
        assert response.status_code == 200
        assert data['success'] == True
        assert len(data['history']) == 2
        assert data['history'][0]['detected_mood'] == 'happy'
        print("✅ Test 5 PASSED: Mood history retrieved")
    
    @patch('routes.mood_routes.execute_query')
    def test_get_mood_stats_endpoint(self, mock_query, client):
        """
        Test Case 6: Get Mood Statistics
        
        Purpose: Verify mood statistics aggregation
        Input: GET /api/mood/stats?user_id=1
        Expected Output: Aggregated mood counts and averages
        Tests: Statistics calculation
        """
        # Mock database query
        mock_query.return_value = [
            {'detected_mood': 'happy', 'count': 10, 'avg_confidence': 0.85},
            {'detected_mood': 'angry', 'count': 3, 'avg_confidence': 0.75}
        ]
        
        # Execute
        response = client.get('/api/mood/stats?user_id=1')
        data = response.get_json()
        
        # Assert
        assert response.status_code == 200
        assert data['success'] == True
        assert len(data['stats']) == 2
        print("✅ Test 6 PASSED: Mood stats retrieved")
    
    @patch('routes.mood_routes.mood_detector.reset')
    def test_reset_detector_endpoint(self, mock_reset, client):
        """
        Test Case 7: Reset Detector
        
        Purpose: Verify detector reset functionality
        Input: POST /api/mood/reset
        Expected Output: {'success': True}
        Tests: State reset endpoint
        """
        # Execute
        response = client.post('/api/mood/reset')
        data = response.get_json()
        
        # Assert
        assert response.status_code == 200
        assert data['success'] == True
        assert mock_reset.called
        print("✅ Test 7 PASSED: Detector reset")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
    