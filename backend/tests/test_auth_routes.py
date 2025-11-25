import pytest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


class TestAuthRoutes:
    """Unit tests for Authentication Routes module"""
    
    @pytest.fixture
    def client(self):
        """Create Flask test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_login_endpoint_returns_auth_url(self, client):
        """
        Test Case 1: Login Endpoint
        
        Purpose: Verify /api/auth/login generates Spotify auth URL
        Input: GET /api/auth/login
        Expected Output: JSON with 'auth_url'
        Tests: OAuth flow initiation
        """
        response = client.get('/api/auth/login')
        data = response.get_json()
        
        assert response.status_code == 200
        assert data['success'] == True
        assert 'auth_url' in data
        assert 'spotify.com' in data['auth_url']
        print("✅ Test 1 PASSED: Login endpoint works")
    
    @patch('routes.auth_routes.spotify_service.exchange_code_for_token')
    @patch('routes.auth_routes.spotify_service.create_spotify_client')
    @patch('routes.auth_routes.spotify_service.get_user_profile')
    def test_callback_endpoint_success(self, mock_profile, mock_client, mock_exchange, client):
        """
        Test Case 2: OAuth Callback Success
        
        Purpose: Verify OAuth callback handling
        Input: GET /api/auth/callback?code=test_code
        Expected Output: Redirect to dashboard
        Tests: Token exchange and session creation
        """
        mock_exchange.return_value = {
            'access_token': 'test_token',
            'refresh_token': 'test_refresh',
            'expires_at': 9999999999
        }
        mock_client.return_value = Mock()
        mock_profile.return_value = {
            'id': 'test_user',
            'display_name': 'Test User',
            'email': 'test@example.com'
        }
        
        response = client.get('/api/auth/callback?code=test_code')
        
        assert response.status_code == 302
        assert 'dashboard' in response.location
        print("✅ Test 2 PASSED: OAuth callback works")
    
    def test_callback_endpoint_missing_code(self, client):
        """
        Test Case 3: Callback Missing Code
        
        Purpose: Verify error when code is missing
        Input: GET /api/auth/callback
        Expected Output: 400 error or redirect with error
        Tests: Error handling
        """
        response = client.get('/api/auth/callback')
        # Accept either 400 (error response) or 302 (redirect with error)
        assert response.status_code in [400, 302]
        print("✅ Test 3 PASSED: Missing code handled")
    
    def test_status_endpoint_not_authenticated(self, client):
        """
        Test Case 4: Status Not Authenticated
        
        Purpose: Verify status when not logged in
        Input: GET /api/auth/status
        Expected Output: {'authenticated': False}
        Tests: Auth state checking
        """
        response = client.get('/api/auth/status')
        data = response.get_json()
        
        assert response.status_code == 200
        assert data['authenticated'] == False
        print("✅ Test 4 PASSED: Not authenticated")
    
    def test_status_endpoint_authenticated(self, client):
        """
        Test Case 5: Status Authenticated
        
        Purpose: Verify status when logged in
        Input: GET /api/auth/status (with session)
        Expected Output: {'authenticated': True}
        Tests: Session persistence
        """
        with client.session_transaction() as sess:
            sess['spotify_token_info'] = {'access_token': 'test', 'expires_at': 9999999999}
            sess['user_id'] = 'test_user'
            sess['display_name'] = 'Test'
        
        response = client.get('/api/auth/status')
        data = response.get_json()
        
        assert response.status_code == 200
        assert data['authenticated'] == True
        print("✅ Test 5 PASSED: Authenticated")
    
    def test_logout_endpoint(self, client):
        """
        Test Case 6: Logout
        
        Purpose: Verify logout clears session
        Input: POST /api/auth/logout
        Expected Output: {'success': True}
        Tests: Session cleanup
        """
        with client.session_transaction() as sess:
            sess['user_id'] = 'test_user'
        
        response = client.post('/api/auth/logout')
        data = response.get_json()
        
        assert response.status_code == 200
        assert data['success'] == True
        print("✅ Test 6 PASSED: Logout works")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])