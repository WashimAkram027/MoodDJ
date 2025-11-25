import pytest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestMusicRoutes:
    """Unit tests for Music Routes module"""
    
    @pytest.fixture
    def client(self):
        """Create Flask test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def authenticated_session(self, client):
        """Create authenticated session"""
        with client.session_transaction() as sess:
            sess['spotify_token_info'] = {
                'access_token': 'test_token',
                'expires_at': 9999999999
            }
            sess['user_id'] = 'test_user'
        return client
    
    @patch('routes.music_routes.spotify_service.get_songs_for_mood')
    def test_recommend_songs_endpoint_success(self, mock_get_songs, authenticated_session):
        """
        Test Case 1: Get Recommendations Success
        
        Purpose: Verify song recommendations based on mood
        Input: POST /api/music/recommend with mood='happy', limit=10
        Expected Output: List of songs matching happy mood
        Tests: Recommendation engine integration
        """
        # Mock song recommendations
        mock_get_songs.return_value = [
            {'title': 'Happy Song', 'artist': 'Artist 1', 'valence': 0.8},
            {'title': 'Joyful Tune', 'artist': 'Artist 2', 'valence': 0.9}
        ]
        
        # Execute
        response = authenticated_session.post('/api/music/recommend', json={
            'mood': 'happy',
            'limit': 10
        })
        data = response.get_json()
        
        # Assert
        assert response.status_code == 200
        assert data['success'] == True
        assert data['mood'] == 'happy'
        assert len(data['songs']) == 2
        assert data['count'] == 2
        print("✅ Test 1 PASSED: Recommendations retrieved")
    
    @patch('routes.music_routes.spotify_service.play_track')
    @patch('routes.music_routes.spotify_service.create_spotify_client')
    def test_play_track_endpoint_success(self, mock_client, mock_play, authenticated_session):
        """
        Test Case 2: Play Track Success
        
        Purpose: Verify track playback initiation
        Input: POST /api/music/play with track_id
        Expected Output: {'success': True}
        Tests: Spotify playback control
        """
        # Mock Spotify client
        mock_client.return_value = Mock()
        
        # Mock play track
        mock_play.return_value = {'success': True}
        
        # Execute
        response = authenticated_session.post('/api/music/play', json={
            'track_id': 'test_track_123',
            'device_id': 'test_device'
        })
        data = response.get_json()
        
        # Assert
        assert response.status_code == 200
        assert data['success'] == True
        print("✅ Test 2 PASSED: Track playback initiated")
    
    def test_play_track_endpoint_missing_track_id(self, authenticated_session):
        """
        Test Case 3: Play Track Missing ID
        
        Purpose: Verify error handling when track_id is missing
        Input: POST /api/music/play with no track_id
        Expected Output: 400 error
        Tests: Input validation
        """
        # Execute
        response = authenticated_session.post('/api/music/play', json={})
        
        # Assert
        assert response.status_code == 400
        assert 'error' in response.get_json()
        print("✅ Test 3 PASSED: Missing track_id handled")
    
    def test_play_track_not_authenticated(self, client):
        """
        Test Case 4: Play Track Not Authenticated
        
        Purpose: Verify authentication requirement
        Input: POST /api/music/play without session
        Expected Output: 401 error
        Tests: Authentication enforcement
        """
        # Execute (no session)
        response = client.post('/api/music/play', json={
            'track_id': 'test_track_123'
        })
        
        # Assert
        assert response.status_code == 401
        assert 'error' in response.get_json()
        print("✅ Test 4 PASSED: Authentication required")
    
    @patch('routes.music_routes.spotify_service.get_current_playback')
    @patch('routes.music_routes.spotify_service.create_spotify_client')
    def test_get_current_playback_endpoint(self, mock_client, mock_playback, authenticated_session):
        """
        Test Case 5: Get Current Playback
        
        Purpose: Verify current playback state retrieval
        Input: GET /api/music/current
        Expected Output: Current track info
        Tests: Playback state monitoring
        """
        # Mock Spotify client
        mock_client.return_value = Mock()
        
        # Mock playback state
        mock_playback.return_value = {
            'is_playing': True,
            'track': {
                'id': 'track123',
                'title': 'Test Song',
                'artist': 'Test Artist'
            }
        }
        
        # Execute
        response = authenticated_session.get('/api/music/current')
        data = response.get_json()
        
        # Assert
        assert response.status_code == 200
        assert data['success'] == True
        assert data['playback']['is_playing'] == True
        print("✅ Test 5 PASSED: Current playback retrieved")
    
    @patch('config.database.execute_query')
    def test_sync_status_endpoint(self, mock_query, authenticated_session):
        """
        Test Case 6: Check Sync Status
        
        Purpose: Verify sync status checking
        Input: GET /api/music/sync/status
        Expected Output: Sync status with song count
        Tests: Library sync state
        """
        # Mock database query
        mock_query.return_value = [{'song_count': 50}]
        
        # Execute
        response = authenticated_session.get('/api/music/sync/status')
        data = response.get_json()
        
        # Assert
        assert response.status_code == 200
        assert data['success'] == True
        assert data['synced'] == True
        assert data['song_count'] == 50
        print("✅ Test 6 PASSED: Sync status retrieved")
    
    @patch('routes.music_routes.spotify_service.fetch_and_store_user_tracks')
    @patch('routes.music_routes.spotify_service.create_spotify_client')
    def test_sync_library_endpoint(self, mock_client, mock_sync, authenticated_session):
        """
        Test Case 7: Sync Library
        
        Purpose: Verify library synchronization
        Input: POST /api/music/sync with limit=25
        Expected Output: Sync result with counts
        Tests: Library sync functionality
        """
        # Mock Spotify client
        mock_client.return_value = Mock()
        
        # Mock sync result
        mock_sync.return_value = {
            'success': True,
            'total_processed': 25,
            'with_features': 20,
            'without_features': 5
        }
        
        # Execute
        response = authenticated_session.post('/api/music/sync', json={
            'limit': 25
        })
        data = response.get_json()
        
        # Assert
        assert response.status_code == 200
        assert data['success'] == True
        assert data['total_processed'] == 25
        print("✅ Test 7 PASSED: Library synced")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])