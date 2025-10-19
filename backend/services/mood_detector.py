import cv2
import math
from collections import deque
import mediapipe as mp
import numpy as np
import base64
from io import BytesIO
from PIL import Image

class MoodDetector:
    """Encapsulates mood detection logic from camera.py"""
    
    def __init__(self):
        # MediaPipe setup
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Smoothing windows
        self.WIN = 10
        self.hist_smile = deque(maxlen=self.WIN)
        self.hist_mouth_open = deque(maxlen=self.WIN)
        self.hist_eye_open = deque(maxlen=self.WIN)
        self.hist_brow_raise = deque(maxlen=self.WIN)
        
        # Thresholds
        self.SMILE_WIDTH_MIN = 0.60
        self.MOUTH_OPEN_SURPRISE = 0.20
        self.EYE_OPEN_SURPRISE = 0.27
        self.BROW_RAISE_SURPRISE = 0.20
        
        # Landmark indices
        self.LM_MOUTH_LEFT = 61
        self.LM_MOUTH_RIGHT = 291
        self.LM_LIP_UP = 13
        self.LM_LIP_DOWN = 14
        self.R_EYE_OUTER = 33
        self.R_EYE_INNER = 133
        self.R_EYE_UP = 159
        self.R_EYE_DOWN = 145
        self.L_EYE_OUTER = 263
        self.L_EYE_INNER = 362
        self.L_EYE_UP = 386
        self.L_EYE_DOWN = 374
        self.RBROW = 105
        self.LBROW = 334
    
    def dist(self, p, q):
        """Calculate distance between two points"""
        return math.hypot(p[0]-q[0], p[1]-q[1])
    
    def xy(self, lmk, wi, hi):
        """Convert landmark to pixel coordinates"""
        return int(lmk.x * wi), int(lmk.y * hi)
    
    def detect_from_base64(self, image_base64):
        """Detect mood from base64 encoded image"""
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
        """Detect mood from a frame"""
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)
        faces = getattr(results, "multi_face_landmarks", None)
        
        mood = "neutral"
        confidence = 0.0
        features = {}
        
        if faces:
            lm = faces[0].landmark
            
            # Extract features
            features = self._extract_features(lm, w, h)
            
            # Get smoothed features
            s_smile = sum(self.hist_smile)/len(self.hist_smile) if self.hist_smile else 0
            s_mopen = sum(self.hist_mouth_open)/len(self.hist_mouth_open) if self.hist_mouth_open else 0
            s_eopen = sum(self.hist_eye_open)/len(self.hist_eye_open) if self.hist_eye_open else 0
            s_brow = sum(self.hist_brow_raise)/len(self.hist_brow_raise) if self.hist_brow_raise else 0
            
            # Mood detection logic
            if ((s_mopen > self.MOUTH_OPEN_SURPRISE and
                 s_eopen > self.EYE_OPEN_SURPRISE and
                 s_brow > self.BROW_RAISE_SURPRISE) or
                    (s_brow > 0.30)):
                mood = "surprised"
                confidence = min(s_brow / 0.30, 1.0)
            elif s_smile > self.SMILE_WIDTH_MIN:
                mood = "happy"
                confidence = min(s_smile / self.SMILE_WIDTH_MIN, 1.0)
            else:
                # Calculate brow distance for anger detection
                p_rbrow = self.xy(lm[self.RBROW], w, h)
                p_lbrow = self.xy(lm[self.LBROW], w, h)
                inter_ocular = features.get('inter_ocular', 1)
                brow_distance = self.dist(p_rbrow, p_lbrow) / inter_ocular
                
                if s_brow < 0.18 and brow_distance < 0.36:
                    mood = "angry"
                    confidence = 1.0 - (brow_distance / 0.36)
                elif s_smile < 0.42 and s_mopen < 0.14:
                    mood = "sad"
                    confidence = 1.0 - (s_smile / 0.42)
                else:
                    mood = "neutral"
                    confidence = 0.7
        
        return {
            'mood': mood,
            'confidence': round(confidence, 2),
            'features': features,
            'detected': faces is not None
        }
    
    def _extract_features(self, lm, w, h):
        """Extract facial features from landmarks"""
        # Get key points
        p_ml = self.xy(lm[self.LM_MOUTH_LEFT], w, h)
        p_mr = self.xy(lm[self.LM_MOUTH_RIGHT], w, h)
        p_mu = self.xy(lm[self.LM_LIP_UP], w, h)
        p_md = self.xy(lm[self.LM_LIP_DOWN], w, h)
        
        p_re_outer = self.xy(lm[self.R_EYE_OUTER], w, h)
        p_re_inner = self.xy(lm[self.R_EYE_INNER], w, h)
        p_re_up = self.xy(lm[self.R_EYE_UP], w, h)
        p_re_down = self.xy(lm[self.R_EYE_DOWN], w, h)
        
        p_le_outer = self.xy(lm[self.L_EYE_OUTER], w, h)
        p_le_inner = self.xy(lm[self.L_EYE_INNER], w, h)
        p_le_up = self.xy(lm[self.L_EYE_UP], w, h)
        p_le_down = self.xy(lm[self.L_EYE_DOWN], w, h)
        
        # Calculate features
        inter_ocular = self.dist(p_re_outer, p_le_outer) + 1e-6
        mouth_width = self.dist(p_ml, p_mr) / inter_ocular
        mouth_open = self.dist(p_mu, p_md) / inter_ocular
        
        re_width = self.dist(p_re_outer, p_re_inner) + 1e-6
        le_width = self.dist(p_le_outer, p_le_inner) + 1e-6
        re_open = self.dist(p_re_up, p_re_down) / re_width
        le_open = self.dist(p_le_up, p_le_down) / le_width
        eye_open = (re_open + le_open) / 2.0
        
        # Eyebrow height
        re_center = ((p_re_outer[0]+p_re_inner[0])//2, (p_re_outer[1]+p_re_inner[1])//2)
        le_center = ((p_le_outer[0]+p_le_inner[0])//2, (p_le_outer[1]+p_le_inner[1])//2)
        rbrow_raise = abs(self.xy(lm[self.RBROW], w, h)[1] - re_center[1]) / inter_ocular
        lbrow_raise = abs(self.xy(lm[self.LBROW], w, h)[1] - le_center[1]) / inter_ocular
        brow_raise = (rbrow_raise + lbrow_raise) / 2.0
        
        # Update history
        self.hist_smile.append(mouth_width)
        self.hist_mouth_open.append(mouth_open)
        self.hist_eye_open.append(eye_open)
        self.hist_brow_raise.append(brow_raise)
        
        return {
            'inter_ocular': inter_ocular,
            'mouth_width': round(mouth_width, 3),
            'mouth_open': round(mouth_open, 3),
            'eye_open': round(eye_open, 3),
            'brow_raise': round(brow_raise, 3)
        }
    
    def reset(self):
        """Reset mood detection history"""
        self.hist_smile.clear()
        self.hist_mouth_open.clear()
        self.hist_eye_open.clear()
        self.hist_brow_raise.clear()