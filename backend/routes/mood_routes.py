from flask import Blueprint, request, jsonify
from services.mood_detector import MoodDetector
from config.database import execute_query
from datetime import datetime

mood_bp = Blueprint('mood', __name__)
mood_detector = MoodDetector()

@mood_bp.route('/detect', methods=['POST'])
def detect_mood():
    """Detect mood from an image"""
    try:
        data = request.json
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Detect mood from base64 image
        result = mood_detector.detect_from_base64(image_data)
        
        if result:
            return jsonify(result), 200
        else:
            return jsonify({'error': 'Could not detect mood'}), 400
            
    except Exception as e:
        print(f"Error in detect_mood: {e}")
        return jsonify({'error': str(e)}), 500

@mood_bp.route('/log', methods=['POST'])
def log_mood():
    """Log mood detection to database"""
    try:
        data = request.json
        user_id = data.get('user_id', 1)  # Default user for demo
        mood = data.get('mood')
        confidence = data.get('confidence', 1.0)
        
        if not mood:
            return jsonify({'error': 'Mood is required'}), 400
        
        query = """
            INSERT INTO mood_sessions (user_id, detected_mood, confidence_score)
            VALUES (%s, %s, %s)
        """
        
        session_id = execute_query(query, (user_id, mood, confidence))
        
        return jsonify({
            'success': True,
            'session_id': session_id
        }), 201
        
    except Exception as e:
        print(f"Error logging mood: {e}")
        return jsonify({'error': str(e)}), 500

@mood_bp.route('/history', methods=['GET'])
def get_mood_history():
    """Get mood detection history"""
    try:
        user_id = request.args.get('user_id', 1)
        limit = request.args.get('limit', 10)
        
        query = """
            SELECT detected_mood, confidence_score, timestamp
            FROM mood_sessions
            WHERE user_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """
        
        history = execute_query(query, (user_id, limit), fetch=True)
        
        return jsonify({
            'success': True,
            'history': history
        }), 200
        
    except Exception as e:
        print(f"Error fetching mood history: {e}")
        return jsonify({'error': str(e)}), 500

@mood_bp.route('/stats', methods=['GET'])
def get_mood_stats():
    """Get mood statistics"""
    try:
        user_id = request.args.get('user_id', 1)
        
        query = """
            SELECT 
                detected_mood,
                COUNT(*) as count,
                AVG(confidence_score) as avg_confidence
            FROM mood_sessions
            WHERE user_id = %s
            GROUP BY detected_mood
        """
        
        stats = execute_query(query, (user_id,), fetch=True)
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        print(f"Error fetching mood stats: {e}")
        return jsonify({'error': str(e)}), 500

@mood_bp.route('/reset', methods=['POST'])
def reset_detector():
    """Reset mood detector history"""
    try:
        mood_detector.reset()
        return jsonify({'success': True, 'message': 'Detector reset'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500