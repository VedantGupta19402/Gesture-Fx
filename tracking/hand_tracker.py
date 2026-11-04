"""
PHANTOM: ORBITAL MODE — Optical Hand Tracking & Temporal Smoothing Engine
"""

import numpy as np
import mediapipe as mp
from config import settings
from tracking.gesture_recognizer import GestureRecognizer

class TrackedHand:
    def __init__(self, label):
        self.label = label
        self.raw_landmarks = None
        self.smoothed_world_landmarks = [np.zeros(3, dtype=np.float32) for _ in range(21)]
        self.palm_center_world = np.zeros(3, dtype=np.float32)
        self.last_palm_center = np.zeros(3, dtype=np.float32)
        self.palm_velocity = np.zeros(3, dtype=np.float32)
        self.velocity_mag = 0.0
        self.gesture = settings.GESTURE_NONE
        self.pinch_distance = 1.0
        self.confidence = 0.0
        self.is_present = False

class HandTracker:
    def __init__(self, camera_manager):
        self.camera_manager = camera_manager
        self.mp_hands = mp.solutions.hands
        self.hands_detector = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.65,
            min_tracking_confidence=0.55
        )
        self.recognizer = GestureRecognizer()
        self.hands = {
            "Left": TrackedHand("Left"),
            "Right": TrackedHand("Right")
        }
        self.dual_hand_gesture = settings.GESTURE_NONE
        self.active_count = 0

    def process_frame(self, rgb_frame, dt=0.016):
        """
        Processes frame through MediaPipe and updates smoothed kinematic representations.
        """
        results = self.hands_detector.process(rgb_frame)
        present_labels = set()

        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                label = handedness.classification[0].label
                confidence = handedness.classification[0].score
                present_labels.add(label)
                
                tracked = self.hands[label]
                tracked.raw_landmarks = hand_landmarks
                tracked.confidence = confidence
                tracked.is_present = True

                # Compute smoothed world landmarks
                alpha = settings.SMOOTHING_FACTOR
                world_pts = []
                for i, lm in enumerate(hand_landmarks.landmark):
                    pt_world = self.camera_manager.screen_to_world_coords(lm.x, lm.y, lm.z)
                    if not tracked.is_present:
                        tracked.smoothed_world_landmarks[i] = pt_world
                    else:
                        tracked.smoothed_world_landmarks[i] = (
                            tracked.smoothed_world_landmarks[i] * (1.0 - alpha) + pt_world * alpha
                        )
                    world_pts.append(tracked.smoothed_world_landmarks[i])

                # Palm center computed from wrist (0), index base (5), pinky base (17)
                palm_center = (world_pts[0] + world_pts[5] + world_pts[17]) / 3.0
                if np.all(tracked.last_palm_center == 0):
                    tracked.last_palm_center = palm_center.copy()

                # Calculate velocity
                if dt > 0.001:
                    tracked.palm_velocity = (palm_center - tracked.last_palm_center) / dt
                    tracked.velocity_mag = float(np.linalg.norm(tracked.palm_velocity))
                tracked.last_palm_center = tracked.palm_center_world.copy()
                tracked.palm_center_world = palm_center

                # Pinch distance
                dx = hand_landmarks.landmark[4].x - hand_landmarks.landmark[8].x
                dy = hand_landmarks.landmark[4].y - hand_landmarks.landmark[8].y
                tracked.pinch_distance = float(np.hypot(dx, dy))

                # Gesture recognition
                tracked.gesture = self.recognizer.update_single_hand(
                    hand_landmarks, label, tracked.velocity_mag
                )

        # Mark absent hands
        for label, hand_obj in self.hands.items():
            if label not in present_labels:
                hand_obj.is_present = False
                hand_obj.gesture = settings.GESTURE_NONE
                hand_obj.velocity_mag = 0.0

        self.active_count = len(present_labels)

        # Dual hand analysis
        left_pos = self.hands["Left"].palm_center_world if self.hands["Left"].is_present else None
        right_pos = self.hands["Right"].palm_center_world if self.hands["Right"].is_present else None
        self.dual_hand_gesture = self.recognizer.update_dual_hands(left_pos, right_pos)

        return self.hands

    def get_primary_interaction_point(self):
        """
        Returns the primary focal point of user interaction (Right hand prioritized, then Left).
        """
        if self.hands["Right"].is_present:
            return self.hands["Right"].palm_center_world, self.hands["Right"].gesture, self.hands["Right"]
        if self.hands["Left"].is_present:
            return self.hands["Left"].palm_center_world, self.hands["Left"].gesture, self.hands["Left"]
        return np.array([0.0, 0.0, -8.0], dtype=np.float32), settings.GESTURE_NONE, None

