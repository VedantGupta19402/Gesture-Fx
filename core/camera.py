"""
PHANTOM: ORBITAL MODE — Optical Acquisition & Coordinate Mapping Engine
"""

import cv2
import numpy as np
import time
from config import settings

class CameraManager:
    """
    Manages webcam capture stream, frame processing, and viewport coordinate projections.
    Provides synthetic fallback frames if camera hardware is busy, shuttered, or absent.
    """
    def __init__(self, camera_index=settings.CAMERA_INDEX,
                 width=settings.CAMERA_WIDTH, height=settings.CAMERA_HEIGHT):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None
        self.is_active = False
        self.last_frame = None
        self.synthetic_time = 0.0
        self.init_camera()

    def init_camera(self):
        try:
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW if cv2.CAP_DSHOW else 0)
            if not self.cap or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(self.camera_index)
            
            if self.cap and self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                
                # Test read an initial frame to verify real stream viability
                ret, test_frame = self.cap.read()
                if ret and test_frame is not None:
                    self.is_active = True
                    print(f"[OPTICAL ENGINE] Camera initialized on index {self.camera_index} ({self.width}x{self.height}).")
                else:
                    self.is_active = False
                    self.cap.release()
                    self.cap = None
                    print("[OPTICAL ENGINE] Optical hardware present but frame stream unavailable (busy/shuttered). Synthesizing stream.")
            else:
                self.is_active = False
                print("[OPTICAL ENGINE] Physical camera offline. Synthesizing telemetry stream.")
        except Exception as e:
            self.is_active = False
            if self.cap:
                self.cap.release()
                self.cap = None
            print(f"[OPTICAL ENGINE] Camera initialization error: {e}. Running synthetic stream.")

    def read_frame(self):
        """
        Reads next frame, horizontally mirrors for natural reflection, and converts to RGB.
        Returns: (success: bool, frame_rgb: np.ndarray, frame_bgr: np.ndarray)
        """
        if self.is_active and self.cap and self.cap.isOpened():
            try:
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    frame = cv2.flip(frame, 1)
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.last_frame = rgb_frame
                    return True, rgb_frame, frame
                else:
                    self.is_active = False
                    self.cap.release()
                    self.cap = None
                    print("[OPTICAL ENGINE] Camera stream ended. Switching to synthetic telemetry.")
            except Exception as e:
                self.is_active = False
                if self.cap:
                    self.cap.release()
                    self.cap = None
                print(f"[OPTICAL ENGINE] Exception in camera read: {e}. Switching to synthetic telemetry.")
        
        # Fast Synthetic Fallback Stream (< 0.1ms)
        self.synthetic_time += 0.016
        synth = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        # Draw a technical calibration reticle
        cx, cy = self.width // 2, self.height // 2
        cv2.circle(synth, (cx, cy), 80, (0, 100, 150), 1)
        cv2.line(synth, (cx - 100, cy), (cx + 100, cy), (0, 80, 120), 1)
        cv2.line(synth, (cx, cy - 100), (cx, cy + 100), (0, 80, 120), 1)
        cv2.putText(synth, "CALIBRATION TEST PATTERN", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 180, 220), 1)
        return False, cv2.cvtColor(synth, cv2.COLOR_BGR2RGB), synth

    def screen_to_world_coords(self, norm_x, norm_y, norm_z=0.0):
        """
        Transforms MediaPipe normalized coordinates (0.0 to 1.0) into OpenGL 3D space.
        World coordinates:
          X: [-4.5, 4.5] (left to right)
          Y: [-3.5, 3.5] (bottom to top, screen Y is inverted)
          Z: [-6.5 to -9.5] depth plane
        """
        world_x = (norm_x - 0.5) * 8.6
        world_y = (0.5 - norm_y) * 6.2
        # MediaPipe z represents relative depth around palm center (approx -0.1 to 0.1)
        world_z = -8.0 - (norm_z * 7.5)
        return np.array([world_x, world_y, world_z], dtype=np.float32)

    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.is_active = False
            print("[OPTICAL ENGINE] Camera released.")

