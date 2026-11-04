"""
PHANTOM: ORBITAL MODE — Spatial Gesture Recognition Engine
Identifies high-level scientific control gestures with temporal hysteresis.
"""

import math
import numpy as np
from config import settings

class GestureRecognizer:
    def __init__(self):
        # Frame hysteresis history per hand label
        self.history = {"Left": [], "Right": []}
        self.active_gesture = {"Left": settings.GESTURE_NONE, "Right": settings.GESTURE_NONE}
        self.last_two_hand_dist = None
        self.two_hand_gesture = settings.GESTURE_NONE

    def _euclidean_dist_2d(self, p1, p2):
        return math.hypot(p1.x - p2.x, p1.y - p2.y)

    def _finger_is_extended(self, tip, pip, mcp):
        """Returns True if fingertip is further from palm base/mcp than pip joint."""
        return tip.y < pip.y

    def analyze_single_hand(self, raw_hand, handedness_label, velocity_magnitude):
        """
        Analyzes 21 landmarks of a single hand and classifies immediate gesture candidate.
        """
        lm = raw_hand.landmark
        
        # 1. Shockwave Check: High velocity hand motion
        if velocity_magnitude > settings.SWIPE_VELOCITY_THRESHOLD:
            return settings.GESTURE_SHOCKWAVE

        # 2. Pinch Detection: Thumb tip (4) to Index tip (8)
        pinch_dist = self._euclidean_dist_2d(lm[4], lm[8])
        if pinch_dist < settings.PINCH_THRESHOLD:
            return settings.GESTURE_PINCH

        # 3. Two-Finger Mode: Index (8) & Middle (12) extended, Ring (16) & Pinky (20) curled
        index_up = lm[8].y < lm[6].y
        middle_up = lm[12].y < lm[10].y
        ring_curled = lm[16].y > lm[14].y
        pinky_curled = lm[20].y > lm[18].y
        if index_up and middle_up and ring_curled and pinky_curled:
            return settings.GESTURE_TWO_FINGERS

        # 4. Closed Fist Detection: All fingertips curled closer to wrist (0) or MCPs
        wrist = lm[0]
        fingertip_indices = [8, 12, 16, 20]
        mcp_indices = [5, 9, 13, 17]
        curled_count = 0
        for tip_idx, mcp_idx in zip(fingertip_indices, mcp_indices):
            d_tip = self._euclidean_dist_2d(lm[tip_idx], wrist)
            d_mcp = self._euclidean_dist_2d(lm[mcp_idx], wrist)
            if d_tip < d_mcp * 1.15:
                curled_count += 1
        
        if curled_count >= 3:
            return settings.GESTURE_CLOSED_FIST

        # 5. Open Palm: All four fingers extended away from wrist
        extended_count = sum(1 for tip_idx, mcp_idx in zip(fingertip_indices, mcp_indices)
                             if self._euclidean_dist_2d(lm[tip_idx], wrist) > self._euclidean_dist_2d(lm[mcp_idx], wrist) * 1.15)
        if extended_count >= 3:
            return settings.GESTURE_OPEN_PALM

        return settings.GESTURE_NONE

    def update_single_hand(self, raw_hand, handedness_label, velocity_mag):
        """
        Applies hysteresis buffer to eliminate jitter and flickering.
        """
        candidate = self.analyze_single_hand(raw_hand, handedness_label, velocity_mag)
        hist = self.history.setdefault(handedness_label, [])
        hist.append(candidate)
        if len(hist) > settings.GESTURE_CONFIRM_FRAMES:
            hist.pop(0)

        # Confirm gesture if majority of recent frames match
        if len(hist) == settings.GESTURE_CONFIRM_FRAMES and hist.count(candidate) >= settings.GESTURE_CONFIRM_FRAMES:
            self.active_gesture[handedness_label] = candidate
        
        # Immediate reaction for shockwave to maintain zero latency
        if candidate == settings.GESTURE_SHOCKWAVE:
            self.active_gesture[handedness_label] = settings.GESTURE_SHOCKWAVE

        return self.active_gesture[handedness_label]

    def update_dual_hands(self, hand_left_world, hand_right_world):
        """
        Analyzes 2-hand relative distance for field expansion / compression.
        """
        if hand_left_world is None or hand_right_world is None:
            self.last_two_hand_dist = None
            self.two_hand_gesture = settings.GESTURE_NONE
            return settings.GESTURE_NONE

        current_dist = float(np.linalg.norm(hand_left_world - hand_right_world))
        if self.last_two_hand_dist is not None:
            delta = current_dist - self.last_two_hand_dist
            if delta > 0.08:
                self.two_hand_gesture = settings.GESTURE_SPREAD
            elif delta < -0.08:
                self.two_hand_gesture = settings.GESTURE_COMPRESS
            else:
                self.two_hand_gesture = settings.GESTURE_NONE
        
        self.last_two_hand_dist = current_dist
        return self.two_hand_gesture

