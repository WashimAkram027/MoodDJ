import cv2
import math
from collections import deque
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
# Mouth - Enhanced landmarks for better detection
LM_MOUTH_LEFT = 61  # Left corner
LM_MOUTH_RIGHT = 291  # Right corner
LM_LIP_UP = 13  # Upper lip center
LM_LIP_DOWN = 14  # Lower lip center

# Additional key mouth points for improved accuracy
LM_MOUTH_LEFT_INNER = 78  # Left corner inner
LM_MOUTH_RIGHT_INNER = 308  # Right corner inner

# Eyes
R_EYE_OUTER = 33
R_EYE_INNER = 133
R_EYE_UP = 159
R_EYE_DOWN = 145

L_EYE_OUTER = 263
L_EYE_INNER = 362
L_EYE_UP = 386
L_EYE_DOWN = 374

# Eyebrows - multiple points for curved lines
# Right eyebrow (from inner to outer)
RBROW_INNER = 70
RBROW_MID1 = 63
RBROW_MID2 = 105
RBROW_MID3 = 66
RBROW_OUTER = 107

# Left eyebrow (from inner to outer)
LBROW_INNER = 300
LBROW_MID1 = 293
LBROW_MID2 = 334
LBROW_MID3 = 296
LBROW_OUTER = 336

# ------------- Smoothing -------------
WIN = 5  # frames to smooth over

# ------------- Thresholds (tune if needed) -------------
SMILE_WIDTH_MIN = 0.56  # mouth width vs inter-ocular width


class MoodDetector:
    """
    Encapsulates mood detection logic
    Only detects: HAPPY, ANGRY, NEUTRAL
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
        
        # Smoothing history queues
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
    
    def detect_from_frame(self, frame):
        """
        Mood detection algorithm - 3 moods only: HAPPY, ANGRY, NEUTRAL
        """
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)
        faces = getattr(results, "multi_face_landmarks", None)

        mood = "neutral"
        confidence = 0.0

        if faces:
            lm = faces[0].landmark

            # --- Key points (pixels) ---
            # Main mouth points
            p_ml = xy(lm[LM_MOUTH_LEFT], w, h)
            p_mr = xy(lm[LM_MOUTH_RIGHT], w, h)
            p_mu = xy(lm[LM_LIP_UP], w, h)
            p_md = xy(lm[LM_LIP_DOWN], w, h)

            # Additional inner corner points for better accuracy
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

            # --- Base scales ---
            inter_ocular = dist(p_re_outer, p_le_outer) + 1e-6
            re_width = dist(p_re_outer, p_re_inner) + 1e-6
            le_width = dist(p_le_outer, p_le_inner) + 1e-6

            # --- Features ---
            # Enhanced mouth width - average of outer and inner corners
            mouth_width_outer = dist(p_ml, p_mr) / inter_ocular
            mouth_width_inner = dist(p_ml_inner, p_mr_inner) / inter_ocular
            mouth_width = (mouth_width_outer + mouth_width_inner) / 2.0

            # Mouth openness
            mouth_open = dist(p_mu, p_md) / inter_ocular

            re_open = dist(p_re_up, p_re_down) / re_width
            le_open = dist(p_le_up, p_le_down) / le_width
            eye_open = (re_open + le_open) / 2.0

            # Eyebrow height (using middle points)
            re_center = ((p_re_outer[0] + p_re_inner[0]) // 2, (p_re_outer[1] + p_re_inner[1]) // 2)
            le_center = ((p_le_outer[0] + p_le_inner[0]) // 2, (p_le_outer[1] + p_le_inner[1]) // 2)
            rbrow_raise = abs(p_rbrow_mid2[1] - re_center[1]) / inter_ocular
            lbrow_raise = abs(p_lbrow_mid2[1] - le_center[1]) / inter_ocular
            brow_raise = (rbrow_raise + lbrow_raise) / 2.0

            # Brow closeness (using inner points)
            brow_distance = dist(p_rbrow_inner, p_lbrow_inner) / inter_ocular

            # --- Smooth features ---
            self.hist_smile.append(mouth_width)
            self.hist_mouth_open.append(mouth_open)
            self.hist_eye_open.append(eye_open)
            self.hist_brow_raise.append(brow_raise)
            self.hist_brow_distance.append(brow_distance)

            s_smile = sum(self.hist_smile) / len(self.hist_smile)
            s_mopen = sum(self.hist_mouth_open) / len(self.hist_mouth_open)
            s_eopen = sum(self.hist_eye_open) / len(self.hist_eye_open)
            s_brow = sum(self.hist_brow_raise) / len(self.hist_brow_raise)

            # --- Mood rules (3 moods only) ---
            # HAPPY: wide mouth (smile)
            if s_smile > SMILE_WIDTH_MIN:
                mood = "happy"

            else:
                # ANGRY: Requires ALL conditions to be met
                # Eye squinting + neutral mouth + lowered eyebrows
                eyes_squinting = s_eopen < 0.23
                mouth_neutral = s_smile < 0.55 and s_mopen < 0.15
                brows_lowered = s_brow < 0.24

                if eyes_squinting and mouth_neutral and brows_lowered:
                    mood = "angry"
                else:
                    # Everything else is NEUTRAL
                    mood = "neutral"
            
            # Confidence always 1.0 (frontend expects this field)
            confidence = 1.0

            # Store features for API response
            features = {
                'inter_ocular': inter_ocular,
                'mouth_width': round(s_smile, 3),
                'mouth_open': round(s_mopen, 3),
                'eye_open': round(s_eopen, 3),
                'brow_raise': round(s_brow, 3),
                'brow_distance': round(brow_distance, 3)
            }
        
        else:
            features = {}
        
        return {
            'mood': mood,
            'confidence': round(confidence, 2),
            'features': features,
            'detected': faces is not None
        }
    
    def reset(self):
        """Reset mood detection history"""
        self.hist_smile.clear()
        self.hist_mouth_open.clear()
        self.hist_eye_open.clear()
        self.hist_brow_raise.clear()
        self.hist_brow_distance.clear()
        gf