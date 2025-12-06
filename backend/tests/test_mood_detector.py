import pytest
import base64
from io import BytesIO
from PIL import Image
import sys
import os

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.mood_detector import MoodDetector


class TestMoodDetector:
    """Unit tests for MoodDetector module"""
    
    @pytest.fixture
    def detector(self):
        """Create a MoodDetector instance for each test"""
        return MoodDetector()
    
    @pytest.fixture
    def sample_base64_image(self):
        """Create a sample base64 encoded image"""
        # Create a simple test image
        img = Image.new('RGB', (640, 480), color='white')
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/jpeg;base64,{img_str}"
    
    def test_detector_initialization(self, detector):
        """
        Test Case 1: Detector Initialization
        
        Purpose: Verify that MoodDetector initializes correctly
        Input: None
        Expected Output: MoodDetector instance with initialized components
        Tests: Object creation and initialization
        """
        assert detector is not None
        assert detector.face_mesh is not None
        assert len(detector.mood_history) == 0
        print("✅ Test 1 PASSED: Detector initialized correctly")
    
    def test_detect_no_face(self, detector, sample_base64_image):
        """
        Test Case 2: No Face Detection
        
        Purpose: Verify behavior when no face is in the image
        Input: Base64 image without a human face
        Expected Output: {'mood': 'neutral', 'confidence': 0.0, 'detected': False}
        Tests: Graceful handling of images without faces
        """
        result = detector.detect_from_base64(sample_base64_image)
        
        assert result is not None
        assert 'mood' in result
        assert 'confidence' in result
        assert 'detected' in result
        # Since our test image has no face, detected should be False or mood is neutral
        assert result['mood'] == 'neutral' or result['detected'] == False
        print("✅ Test 2 PASSED: No face handled gracefully")
    
    def test_reset_detector(self, detector):
        """
        Test Case 3: Reset Functionality
        
        Purpose: Verify that reset clears all history
        Input: None (after detector has some history)
        Expected Output: Empty mood history
        Tests: State reset functionality
        """
        # Add some fake history
        detector.mood_history.append('happy')
        detector.mood_history.append('angry')
        
        # Reset
        detector.reset()

        assert len(detector.mood_history) == 0
        print("✅ Test 3 PASSED: Detector reset successfully")
    
    def test_mood_history_limit(self, detector):
        """
        Test Case 4: Mood History Size Limit
        
        Purpose: Verify that mood history doesn't exceed WIN size (3 frames)
        Input: Multiple mood detections
        Expected Output: History limited to 3 most recent moods
        Tests: Memory management and history size constraint
        """
        # Manually add moods beyond the limit
        for i in range(10):
            detector.mood_history.append('happy')
        
        # Should only keep last 3 (WIN=3)
        assert len(detector.mood_history) <= 3
        print("✅ Test 4 PASSED: History size properly limited")


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v', '--tb=short'])