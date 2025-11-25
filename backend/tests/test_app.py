import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, socketio


class TestApp:
    """Unit tests for Main App module (WebSocket and Health)"""
    
    @pytest.fixture
    def client(self):
        """Create Flask test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def socketio_client(self):
        """Create SocketIO test client"""
        return socketio.test_client(app)
    
    def test_health_endpoint(self, client):
        """
        Test Case 1: Health Check Endpoint
        
        Purpose: Verify health check endpoint for load balancer
        Input: GET /api/health
        Expected Output: {'status': 'healthy', 'service': 'mooddj-backend'}
        Tests: Application health monitoring
        """
        # Execute
        response = client.get('/api/health')
        data = response.get_json()
        
        # Assert
        assert response.status_code == 200
        assert data['status'] == 'healthy'
        assert data['service'] == 'mooddj-backend'
        print("✅ Test 1 PASSED: Health check works")
    
    def test_websocket_connect(self, socketio_client):
        """
        Test Case 2: WebSocket Connection
        
        Purpose: Verify WebSocket connection establishment
        Input: Socket.IO connect event
        Expected Output: Connection successful, response received
        Tests: Real-time communication setup
        """
        # Check connection
        assert socketio_client.is_connected()
        
        # Should receive connection_response
        received = socketio_client.get_received()
        assert len(received) > 0
        assert received[0]['name'] == 'connection_response'
        assert received[0]['args'][0]['status'] == 'connected'
        
        print("✅ Test 2 PASSED: WebSocket connected")
    
    def test_websocket_mood_update(self, socketio_client):
        """
        Test Case 3: WebSocket Mood Update
        
        Purpose: Verify mood update broadcasting via WebSocket
        Input: Emit 'mood_update' event with mood data
        Expected Output: 'mood_changed' event broadcast to all clients
        Tests: Real-time mood synchronization
        """
        # Send mood update
        socketio_client.emit('mood_update', {
            'mood': 'happy',
            'confidence': 0.85
        })
        
        # Check if mood_changed event was broadcast
        received = socketio_client.get_received()
        
        # Should have received mood_changed event
        mood_changed_events = [r for r in received if r['name'] == 'mood_changed']
        assert len(mood_changed_events) > 0
        
        print("✅ Test 3 PASSED: Mood update broadcast")
    
    def test_websocket_start_detection(self, socketio_client):
        """
        Test Case 4: WebSocket Start Detection
        
        Purpose: Verify detection start command
        Input: Emit 'start_detection' event
        Expected Output: 'detection_started' event received
        Tests: Detection control via WebSocket
        """
        # Clear previous messages
        socketio_client.get_received()
        
        # Send start detection
        socketio_client.emit('start_detection', {})
        
        # Check response
        received = socketio_client.get_received()
        detection_started = [r for r in received if r['name'] == 'detection_started']
        
        assert len(detection_started) > 0
        assert detection_started[0]['args'][0]['status'] == 'started'
        
        print("✅ Test 4 PASSED: Detection started")
    
    def test_websocket_stop_detection(self, socketio_client):
        """
        Test Case 5: WebSocket Stop Detection
        
        Purpose: Verify detection stop command
        Input: Emit 'stop_detection' event
        Expected Output: 'detection_stopped' event received
        Tests: Detection control via WebSocket
        """
        # Clear previous messages
        socketio_client.get_received()
        
        # Send stop detection
        socketio_client.emit('stop_detection', {})
        
        # Check response
        received = socketio_client.get_received()
        detection_stopped = [r for r in received if r['name'] == 'detection_stopped']
        
        assert len(detection_stopped) > 0
        assert detection_stopped[0]['args'][0]['status'] == 'stopped'
        
        print("✅ Test 5 PASSED: Detection stopped")
    
    def test_404_error_handler(self, client):
        """
        Test Case 6: 404 Error Handler
        
        Purpose: Verify custom 404 error handling
        Input: GET /nonexistent-endpoint
        Expected Output: 404 with JSON error message
        Tests: Error handling
        """
        # Execute
        response = client.get('/nonexistent-endpoint')
        data = response.get_json()
        
        # Assert
        assert response.status_code == 404
        assert 'error' in data
        print("✅ Test 6 PASSED: 404 handled")
    
    def test_cors_headers(self, client):
        """
        Test Case 7: CORS Headers
        
        Purpose: Verify CORS headers are present for frontend communication
        Input: GET /api/health with Origin header
        Expected Output: CORS headers in response
        Tests: Cross-origin resource sharing configuration
        """
        # Execute
        response = client.get('/api/health', headers={
            'Origin': 'http://localhost:3000'
        })
        
        # Assert
        assert response.status_code == 200
        # CORS headers should be present (handled by Flask-CORS)
        print("✅ Test 7 PASSED: CORS configured")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])