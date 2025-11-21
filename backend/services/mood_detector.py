# backend/services/mood_detector.py
# Modified to use MAJORITY VOTING instead of AVERAGING

import cv2
import math
from collections import deque, Counter
import mediapipe as mp
import numpy as np
import base64
from io import BytesIO
from PIL import Image


# ------------- Landmark helpers -------------
def dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def xy(lmk, wi, hi):
    return int(lmk.x * wi), int(lmk.y * hi)


# Face Mesh landmark indices (MediaPipe)
LM_MOUTH_LEFT = 61
LM_MOUTH_RIGHT = 291
LM_LIP_UP = 13
LM_LIP_DOWN = 14
LM_MOUTH_LEFT_INNER = 78
LM_MOUTH_RIGHT_INNER = 308

R_EYE_OUTER = 33
R_EYE_INNER = 133
R_EYE_UP = 159
R_EYE_DOWN = 145

L_EYE_OUTER = 263
L_EYE_INNER = 362
L_EYE_UP = 386
L_EYE_DOWN = 374

RBROW_INNER = 70
RBROW_MID1 = 63
RBROW_MID2 = 105
RBROW_MID3 = 66
RBROW_OUTER = 107

LBROW_INNER = 300
LBROW_MID1 = 293
LBROW_MID2 = 334
LBROW_MID3 = 296
LBROW_OUTER = 336

# ------------- Configuration -------------
WIN = 3  # Number of frames to collect for voting
SMILE_WIDTH_MIN = 0.54  # Threshold for smile detection


class MoodDetector:
    """
    Mood detector using MAJORITY VOTING (mode-based) instead of averaging.
    Detects: HAPPY, ANGRY, NEUTRAL based on which mood appears most frequently.
    """
    
    def __init__(self):
        # MediaPipe setup
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # 🎯 NEW: Store detected MOODS instead of features
        # This list stores the actual mood string (happy/angry/neutral)
        self.mood_history = deque(maxlen=WIN)
        
        # Still keep feature history for debugging/display
        self.hist_smile = deque(maxlen=WIN)
        self.hist_mouth_open = deque(maxlen=WIN)
        self.hist_eye_open = deque(maxlen=WIN)
        self.hist_brow_raise = deque(maxlen=WIN)
        self.hist_brow_distance = deque(maxlen=WIN)
    
    def detect_from_base64(self, image_base64):
        """Detect mood from base64 encoded image (for API)"""
        try:
            # Decode base64 image
            image_data = base64.b64decode(image_base64.split(',')[1])
            image = Image.open(BytesIO(image_data))
            frame = np.array(image)
            
            # Convert RGB to BGR for OpenCV
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            return self.detect_from_frame(frame)
        except Exception as e:
            print(f"Error detecting mood from base64: {e}")
            return None
    
    def _determine_instant_mood(self, s_smile, s_mopen, s_eopen, s_brow):
        """
        Determine mood for CURRENT frame based on features.
        This gets called for each frame, then we vote on the results.
        
        Returns: 'happy', 'angry', or 'neutral'
        """
        # HAPPY: wide mouth (smile)
        if s_smile > SMILE_WIDTH_MIN:
            return "happy"
        
        # ANGRY: Requires ALL conditions
        eyes_squinting = s_eopen < 0.23
        mouth_neutral = s_smile < 0.55 and s_mopen < 0.15
        brows_lowered = s_brow < 0.24
        
        if eyes_squinting and mouth_neutral and brows_lowered:
            return "angry"
        
        # Everything else is NEUTRAL
        return "neutral"
    
    def _get_majority_mood(self):
        """
        🎯 MAJORITY VOTING: Find which mood appeared most frequently.
        
        Example:
        mood_history = ['happy', 'happy', 'neutral', 'happy', 'neutral']
        Counter result: {'happy': 3, 'neutral': 2}
        Winner: 'happy' (appears 3 times)
        
        Returns: The mood that wins the vote
        """
        if not self.mood_history:
            return "neutral"
        
        # Count how many times each mood appears
        mood_counts = Counter(self.mood_history)
        
        # Get the most common mood (the winner!)
        # most_common(1) returns: [('happy', 3)] if happy appears 3 times
        winner_mood, winner_count = mood_counts.most_common(1)[0]
        
        # Calculate confidence based on how dominant the winner is
        total_votes = len(self.mood_history)
        confidence = winner_count / total_votes if total_votes > 0 else 0.0
        
        return winner_mood, confidence
    
    def detect_from_frame(self, frame):
        """
        Main detection logic using MAJORITY VOTING.
        
        Process:
        1. Detect facial features for current frame
        2. Determine instant mood for this frame
        3. Add to mood history
        4. Vote on last N moods
        5. Return the winning mood
        """
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)
        faces = getattr(results, "multi_face_landmarks", None)

        if faces:
            lm = faces[0].landmark

            # --- Extract facial features (same as before) ---
            p_ml = xy(lm[LM_MOUTH_LEFT], w, h)
            p_mr = xy(lm[LM_MOUTH_RIGHT], w, h)
            p_mu = xy(lm[LM_LIP_UP], w, h)
            p_md = xy(lm[LM_LIP_DOWN], w, h)
            p_ml_inner = xy(lm[LM_MOUTH_LEFT_INNER], w, h)
            p_mr_inner = xy(lm[LM_MOUTH_RIGHT_INNER], w, h)

            p_re_outer = xy(lm[R_EYE_OUTER], w, h)
            p_re_inner = xy(lm[R_EYE_INNER], w, h)
            p_re_up = xy(lm[R_EYE_UP], w, h)
            p_re_down = xy(lm[R_EYE_DOWN], w, h)

            p_le_outer = xy(lm[L_EYE_OUTER], w, h)
            p_le_inner = xy(lm[L_EYE_INNER], w, h)
            p_le_up = xy(lm[L_EYE_UP], w, h)
            p_le_down = xy(lm[L_EYE_DOWN], w, h)

            p_rbrow_inner = xy(lm[RBROW_INNER], w, h)
            p_rbrow_mid2 = xy(lm[RBROW_MID2], w, h)
            p_lbrow_inner = xy(lm[LBROW_INNER], w, h)
            p_lbrow_mid2 = xy(lm[LBROW_MID2], w, h)

            # --- Calculate scales ---
            inter_ocular = dist(p_re_outer, p_le_outer) + 1e-6
            re_width = dist(p_re_outer, p_re_inner) + 1e-6
            le_width = dist(p_le_outer, p_le_inner) + 1e-6

            # --- Calculate features ---
            mouth_width_outer = dist(p_ml, p_mr) / inter_ocular
            mouth_width_inner = dist(p_ml_inner, p_mr_inner) / inter_ocular
            mouth_width = (mouth_width_outer + mouth_width_inner) / 2.0

            mouth_open = dist(p_mu, p_md) / inter_ocular

            re_open = dist(p_re_up, p_re_down) / re_width
            le_open = dist(p_le_up, p_le_down) / le_width
            eye_open = (re_open + le_open) / 2.0

            re_center = ((p_re_outer[0] + p_re_inner[0]) // 2, (p_re_outer[1] + p_re_inner[1]) // 2)
            le_center = ((p_le_outer[0] + p_le_inner[0]) // 2, (p_le_outer[1] + p_le_inner[1]) // 2)
            rbrow_raise = abs(p_rbrow_mid2[1] - re_center[1]) / inter_ocular
            lbrow_raise = abs(p_lbrow_mid2[1] - le_center[1]) / inter_ocular
            brow_raise = (rbrow_raise + lbrow_raise) / 2.0

            brow_distance = dist(p_rbrow_inner, p_lbrow_inner) / inter_ocular

            # --- Store features in history (for debugging) ---
            self.hist_smile.append(mouth_width)
            self.hist_mouth_open.append(mouth_open)
            self.hist_eye_open.append(eye_open)
            self.hist_brow_raise.append(brow_raise)
            self.hist_brow_distance.append(brow_distance)

            # --- Smooth features (for instant mood determination) ---
            s_smile = sum(self.hist_smile) / len(self.hist_smile)
            s_mopen = sum(self.hist_mouth_open) / len(self.hist_mouth_open)
            s_eopen = sum(self.hist_eye_open) / len(self.hist_eye_open)
            s_brow = sum(self.hist_brow_raise) / len(self.hist_brow_raise)

            # 🎯 NEW: Determine instant mood for THIS frame
            instant_mood = self._determine_instant_mood(s_smile, s_mopen, s_eopen, s_brow)
            
            # 🎯 NEW: Add to mood history
            self.mood_history.append(instant_mood)
            
            # 🎯 NEW: Get the winning mood via majority voting
            final_mood, confidence = self._get_majority_mood()
            
            # Store features for API response
            features = {
                'inter_ocular': inter_ocular,
                'mouth_width': round(s_smile, 3),
                'mouth_open': round(s_mopen, 3),
                'eye_open': round(s_eopen, 3),
                'brow_raise': round(s_brow, 3),
                'brow_distance': round(brow_distance, 3),
                'instant_mood': instant_mood,  # Mood for this frame
                'mood_history': list(self.mood_history),  # Last N moods
                'mood_counts': dict(Counter(self.mood_history))  # Vote tally
            }
        
        else:
            # No face detected
            final_mood = "neutral"
            confidence = 0.0
            features = {}
        
        return {
            'mood': final_mood,
            'confidence': round(confidence, 2),
            'features': features,
            'detected': faces is not None
        }
    
    def reset(self):
        """Reset mood detection history"""
        self.mood_history.clear()
        self.hist_smile.clear()
        self.hist_mouth_open.clear()
        self.hist_eye_open.clear()
        self.hist_brow_raise.clear()
        self.hist_brow_distance.clear()