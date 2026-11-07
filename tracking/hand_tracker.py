"""
PHANTOM: ORBITAL MODE — Optical Hand Tracking & Body-Relative Spatial Engine
Establishes body-relative interaction origins, dual-hand midpoints,
pinch-and-release kinetics, and spatial warp field state.
Optimized with asynchronous optical inference worker for maximum framerate.
"""

import math
import time
import threading
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
        
        # Pinch-and-Release Spatial Kinetics
        self.is_pinching = False
        self.was_pinching = False
        self.pinch_just_started = False
        self.pinch_just_released = False
        self.pinch_world_pos = np.zeros(3, dtype=np.float32)
        self.velocity_history = []
        self.release_velocity = np.zeros(3, dtype=np.float32)

        # Warp disturbance intensity
        self.warp_intensity = 0.0

    def update_pinch_state(self, is_pinch_now, pinch_pos, dt):
        self.pinch_world_pos = pinch_pos
        self.pinch_just_started = (is_pinch_now and not self.was_pinching)
        self.pinch_just_released = (not is_pinch_now and self.was_pinching)
        self.was_pinching = self.is_pinching
        self.is_pinching = is_pinch_now

        self.velocity_history.append(self.palm_velocity.copy())
        if len(self.velocity_history) > 5:
            self.velocity_history.pop(0)

        if self.pinch_just_released:
            if len(self.velocity_history) > 0:
                self.release_velocity = np.mean(self.velocity_history, axis=0)
            else:
                self.release_velocity = self.palm_velocity.copy()
        else:
            self.release_velocity *= 0.0


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

        # Body-Relative Dynamic Origin State
        self.resting_origin = np.array(settings.RESTING_ORIGIN, dtype=np.float32)
        self.current_origin = self.resting_origin.copy()
        self.target_origin = self.resting_origin.copy()
        self.origin_velocity = np.zeros(3, dtype=np.float32)
        self.origin_mode = "RESTING"
        self.tracking_loss_timer = 0.0

        # Asynchronous Optical Tracking Worker
        self.lock = threading.Lock()
        self.raw_results = None
        self.worker_running = True
        self.worker_thread = threading.Thread(target=self._optical_worker_loop, daemon=True)
        self.worker_thread.start()

    def _optical_worker_loop(self):
        """
        Background optical inference thread: processes webcam frames continuously
        so rendering is never throttled by CPU inference.
        """
        while self.worker_running:
            try:
                ret, rgb_frame, _ = self.camera_manager.read_frame()
                if ret and rgb_frame is not None:
                    results = self.hands_detector.process(rgb_frame)
                    with self.lock:
                        self.raw_results = results
                else:
                    time.sleep(0.01)
            except Exception:
                time.sleep(0.01)

    def update(self, dt=0.016):
        """Main-thread update method: consumes latest inferences with zero wait time."""
        return self.process_frame(None, dt)

    def process_frame(self, rgb_frame=None, dt=0.016):
        """
        Consumes latest neural inferences under thread lock, applies temporal smoothing,
        and solves body-relative origin dynamics.
        """
        with self.lock:
            results = self.raw_results

        present_labels = set()

        if results and results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                label = handedness.classification[0].label
                confidence = handedness.classification[0].score
                present_labels.add(label)
                
                tracked = self.hands[label]
                tracked.raw_landmarks = hand_landmarks
                tracked.confidence = confidence
                tracked.is_present = True

                # 1. Compute smoothed world landmarks
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

                # 2. Palm center computed from wrist (0), index base (5), pinky base (17)
                palm_center = (world_pts[0] + world_pts[5] + world_pts[17]) / 3.0
                if np.all(tracked.last_palm_center == 0):
                    tracked.last_palm_center = palm_center.copy()

                # Calculate velocity
                if dt > 0.001:
                    tracked.palm_velocity = (palm_center - tracked.last_palm_center) / dt
                    tracked.velocity_mag = float(np.linalg.norm(tracked.palm_velocity))
                tracked.last_palm_center = tracked.palm_center_world.copy()
                tracked.palm_center_world = palm_center

                # 3. Pinch measurement & pinch focal position
                thumb_tip = world_pts[4]
                index_tip = world_pts[8]
                pinch_center_3d = (thumb_tip + index_tip) * 0.5
                dx = hand_landmarks.landmark[4].x - hand_landmarks.landmark[8].x
                dy = hand_landmarks.landmark[4].y - hand_landmarks.landmark[8].y
                tracked.pinch_distance = float(np.hypot(dx, dy))

                # Gesture recognition
                raw_gesture = self.recognizer.update_single_hand(
                    hand_landmarks, label, tracked.velocity_mag
                )
                tracked.gesture = raw_gesture

                # Pinch state tracking
                is_pinching = (tracked.gesture == settings.GESTURE_PINCH or tracked.pinch_distance < settings.PINCH_THRESHOLD)
                tracked.update_pinch_state(is_pinching, pinch_center_3d, dt)

                # Spatial warp intensity: scales with velocity and proximity
                speed_factor = min(2.5, tracked.velocity_mag / 1.5)
                tracked.warp_intensity = max(0.2, speed_factor)

        # Handle absent hands
        for label, hand_obj in self.hands.items():
            if label not in present_labels:
                hand_obj.is_present = False
                hand_obj.gesture = settings.GESTURE_NONE
                hand_obj.velocity_mag = 0.0
                hand_obj.update_pinch_state(False, hand_obj.palm_center_world, dt)
                hand_obj.warp_intensity = max(0.0, hand_obj.warp_intensity - dt * settings.WARP_DISSIPATION_RATE)

        self.active_count = len(present_labels)

        # Dual hand analysis
        left_pos = self.hands["Left"].palm_center_world if self.hands["Left"].is_present else None
        right_pos = self.hands["Right"].palm_center_world if self.hands["Right"].is_present else None
        self.dual_hand_gesture = self.recognizer.update_dual_hands(left_pos, right_pos)

        # 4. Body-Relative Dynamic Interaction Origin Solver
        self._update_interaction_origin(dt)

        return self.hands

    def _update_interaction_origin(self, dt):
        has_left = self.hands["Left"].is_present
        has_right = self.hands["Right"].is_present

        if has_left and has_right:
            self.target_origin = (self.hands["Left"].palm_center_world + self.hands["Right"].palm_center_world) * 0.5
            self.origin_mode = "DUAL_HAND_MIDPOINT"
            self.tracking_loss_timer = 0.0

        elif has_right:
            self.target_origin = self.hands["Right"].palm_center_world.copy()
            self.origin_mode = "SINGLE_HAND_RIGHT"
            self.tracking_loss_timer = 0.0

        elif has_left:
            self.target_origin = self.hands["Left"].palm_center_world.copy()
            self.origin_mode = "SINGLE_HAND_LEFT"
            self.tracking_loss_timer = 0.0

        else:
            self.tracking_loss_timer += dt
            if self.tracking_loss_timer < settings.DROPOUT_HOLD_SECONDS:
                self.origin_mode = "COASTING"
                self.target_origin += self.origin_velocity * (dt * 0.4)
            else:
                self.origin_mode = "RESTING"
                self.target_origin = self.resting_origin.copy()

        blend = 1.0 - math.exp(-settings.ORIGIN_SMOOTHING_SPEED * dt)
        new_origin = self.current_origin + (self.target_origin - self.current_origin) * blend
        if dt > 0.001:
            self.origin_velocity = (new_origin - self.current_origin) / dt
        self.current_origin = new_origin

    def get_body_relative_origin(self):
        primary_gesture = settings.GESTURE_NONE
        if self.hands["Right"].is_present:
            primary_gesture = self.hands["Right"].gesture
        elif self.hands["Left"].is_present:
            primary_gesture = self.hands["Left"].gesture

        return self.current_origin, self.origin_mode, primary_gesture

    def get_active_warp_fields(self):
        fields = []
        for label, hand in self.hands.items():
            if hand.is_present or hand.warp_intensity > 0.05:
                fields.append({
                    "label": label,
                    "pos": hand.palm_center_world.copy(),
                    "velocity": hand.palm_velocity.copy(),
                    "intensity": hand.warp_intensity,
                    "radius": settings.WARP_BASE_RADIUS * (1.0 + 0.3 * hand.warp_intensity)
                })
        return fields

    def cleanup(self):
        self.worker_running = False
        try:
            self.hands_detector.close()
        except Exception:
            pass
