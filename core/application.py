"""
PHANTOM: ORBITAL MODE — Master Application Lifecycle Controller
Phase 2: SPATIAL DISTORTION & GRAVITATIONAL LENSING ENGINE
"""

import os
import sys
import traceback
import ctypes
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from config import settings
from core.camera import CameraManager
from tracking.hand_tracker import HandTracker
from simulation.orbital_system import OrbitalSystem
from simulation.particle_system import ParticleSystem
from simulation.energy_effects import EnergyEffectsManager
from rendering.renderer import MasterRenderer
from interface.telemetry_hud import TelemetryHUD

# Configure SDL environment before pygame.init
os.environ['SDL_VIDEO_CENTERED'] = '1'
try:
    # Set Windows DPI awareness so OpenGL viewport is not clipped/virtualized
    ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass

class PhantomApplication:
    def __init__(self):
        print("[PHANTOM] Initializing Pygame display & OpenGL context...")
        pygame.init()
        pygame.display.init()

        # Display Dimensions - adapt to user screen resolution if smaller
        info = pygame.display.Info()
        screen_w = info.current_w if info.current_w > 0 else settings.WINDOW_WIDTH
        screen_h = info.current_h if info.current_h > 0 else settings.WINDOW_HEIGHT
        
        self.width = min(settings.WINDOW_WIDTH, int(screen_w * 0.92))
        self.height = min(settings.WINDOW_HEIGHT, int(screen_h * 0.88))
        self.is_fullscreen = False

        # Explicitly configure OpenGL attributes before set_mode
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 2)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 1)
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        pygame.display.gl_set_attribute(pygame.GL_ALPHA_SIZE, 8)
        pygame.display.gl_set_attribute(pygame.GL_ACCELERATED_VISUAL, 1)

        # 1. Create Display Window FIRST before starting camera or inference
        self.flags = DOUBLEBUF | OPENGL | RESIZABLE
        self.screen = pygame.display.set_mode((self.width, self.height), self.flags)
        pygame.display.set_caption(settings.WINDOW_TITLE)

        # Query & Log Hardware OpenGL Telemetry
        gl_version = glGetString(GL_VERSION)
        gl_vendor = glGetString(GL_VENDOR)
        gl_renderer = glGetString(GL_RENDERER)
        print(f"[GRAPHICS ENGINE] Context created successfully:")
        print(f"  * GL Version  : {gl_version.decode() if gl_version else 'Unknown'}")
        print(f"  * GL Vendor   : {gl_vendor.decode() if gl_vendor else 'Unknown'}")
        print(f"  * GL Renderer : {gl_renderer.decode() if gl_renderer else 'Unknown'}")
        print(f"  * Viewport    : {self.width}x{self.height} (Display: {screen_w}x{screen_h})")

        # Force window visible on Windows
        self._ensure_window_visible()

        # 2. Render immediate standby/splash frame so DWM maps the window to screen
        glClearColor(settings.COLOR_BG[0], settings.COLOR_BG[1], settings.COLOR_BG[2], 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        pygame.display.flip()
        pygame.event.pump()

        # 3. Core Systems Initialization
        print("[PHANTOM] Initializing 3D rendering pipeline & spatial simulation...")
        self.renderer = MasterRenderer(self.width, self.height)
        self.hud = TelemetryHUD(self.width, self.height)
        self.orbital_system = OrbitalSystem()
        self.particle_system = ParticleSystem(settings.MAX_PARTICLES)
        self.energy_effects = EnergyEffectsManager()

        pygame.event.pump()

        # 4. Optical Hardware & Tracking Inference
        print("[PHANTOM] Connecting optical capture and neural models...")
        self.camera = CameraManager()
        self.tracker = HandTracker(self.camera)

        self.clock = pygame.time.Clock()
        self.running = True
        self.fps = 60.0
        print("[PHANTOM] Application fully initialized and entering main loop.")

    def _ensure_window_visible(self):
        try:
            wm_info = pygame.display.get_wm_info()
            if "window" in wm_info:
                hwnd = wm_info["window"]
                user32 = ctypes.windll.user32
                user32.ShowWindow(hwnd, 5) # SW_SHOW
                user32.SetForegroundWindow(hwnd)
        except Exception as e:
            print(f"[PHANTOM] Note on window manager: {e}")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                print("[PHANTOM] Window close requested — exiting cleanly.")
                self.running = False

            elif event.type == VIDEORESIZE:
                new_w, new_h = max(1, event.w), max(1, event.h)
                if new_w != self.width or new_h != self.height:
                    self.width, self.height = new_w, new_h
                    self.renderer.set_viewport(self.width, self.height)
                    self.hud.set_viewport(self.width, self.height)

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                elif event.key == K_1:
                    self.orbital_system.set_mode(settings.MODE_ORBITAL)
                elif event.key == K_2:
                    self.orbital_system.set_mode(settings.MODE_CHAOS)
                elif event.key == K_3:
                    self.orbital_system.set_mode(settings.MODE_SINGULARITY)
                elif event.key == K_h:
                    self.hud.toggle_visibility()
                elif event.key == K_r:
                    self.reset_simulation()
                elif event.key == K_f:
                    self.toggle_fullscreen()
                elif event.key == K_SPACE:
                    # Trigger manual energy shockwave pulse
                    self.energy_effects.trigger_shockwave(
                        origin=self.orbital_system.smoothed_center,
                        color=settings.COLOR_WHITE
                    )

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            info = pygame.display.Info()
            self.width, self.height = info.current_w, info.current_h
            self.flags = DOUBLEBUF | OPENGL | FULLSCREEN
        else:
            self.width, self.height = settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT
            self.flags = DOUBLEBUF | OPENGL | RESIZABLE

        self.screen = pygame.display.set_mode((self.width, self.height), self.flags)
        self.renderer.set_viewport(self.width, self.height)
        self.hud.set_viewport(self.width, self.height)

    def reset_simulation(self):
        self.orbital_system._build_orbital_layers()
        self.orbital_system.set_mode(settings.MODE_ORBITAL)
        self.particle_system._init_initial_positions()
        self.renderer.cam_rot_x = 0.0
        self.renderer.cam_rot_y = 0.0

    def update_physics(self, dt):
        # 1. Optical Hand Landmark Processing
        ret, rgb_frame, _ = self.camera.read_frame()
        hands = self.tracker.process_frame(rgb_frame, dt)
        
        primary_pos, primary_gesture, primary_hand = self.tracker.get_primary_interaction_point()
        dual_gesture = self.tracker.dual_hand_gesture

        # 2. Camera Orientation Adjustment via Left Hand Two-Finger Gesture
        left_hand = hands.get("Left")
        if left_hand and left_hand.is_present and left_hand.gesture == settings.GESTURE_TWO_FINGERS:
            # Map wrist-to-middle vector to subtle orbital scene rotation
            wrist = left_hand.raw_landmarks.landmark[0]
            mid = left_hand.raw_landmarks.landmark[9]
            target_rot_x = (mid.y - wrist.y) * 120.0
            target_rot_y = (mid.x - wrist.x) * 120.0
            self.renderer.cam_rot_x += (target_rot_x - self.renderer.cam_rot_x) * (dt * 3.5)
            self.renderer.cam_rot_y += (target_rot_y - self.renderer.cam_rot_y) * (dt * 3.5)
        else:
            # Subtle gentle ambient perspective drift
            self.renderer.cam_rot_y += dt * 1.5

        # 3. Energy Shockwave & Core Effects
        vel = primary_hand.palm_velocity if primary_hand else np.zeros(3, dtype=np.float32)
        is_swipe = (primary_gesture == settings.GESTURE_SHOCKWAVE)
        self.energy_effects.update(
            dt=dt,
            core_pos=self.orbital_system.smoothed_center,
            hand_velocity=vel,
            is_fast_swipe=is_swipe,
            field_intensity=self.orbital_system.field_intensity
        )

        # 4. 3D Orbital Mechanics Simulation
        self.orbital_system.update(
            dt=dt,
            primary_hand_pos=primary_pos if (primary_hand and primary_hand.is_present) else None,
            gesture=primary_gesture,
            dual_gesture=dual_gesture
        )

        # 5. Vectorized Particle Physics
        self.particle_system.update(
            dt=dt,
            center_pos=self.orbital_system.smoothed_center,
            hand_pos=primary_pos if (primary_hand and primary_hand.is_present) else None,
            gesture=primary_gesture,
            shockwaves=self.energy_effects.shockwaves,
            mode=self.orbital_system.mode,
            field_scale=self.orbital_system.field_scale
        )

        return hands

    def render_scene(self, hands):
        self.renderer.begin_frame()

        # 1. Atmospheric Quantum Starfield & Floor Grid
        self.renderer.render_starfield()
        self.renderer.render_grid_plane()

        # 2. Hand Skeletons in 3D Space
        self.renderer.render_hand_skeletons(hands)

        # 3. Celestial Orbital Mechanics
        self.renderer.render_motion_trails(self.orbital_system)
        self.renderer.render_energy_core(
            self.orbital_system.smoothed_center,
            self.energy_effects,
            self.orbital_system.field_intensity
        )
        self.renderer.render_orbital_bodies(self.orbital_system)

        # 4. Energy Shockwaves
        self.renderer.render_shockwaves(self.energy_effects)

        # 5. Glowing Particle Cloud
        self.renderer.render_particles(self.particle_system)

        # 6. Scientific Telemetry HUD Overlay
        self.hud.render(
            fps=self.fps,
            camera_status=self.camera.is_active,
            hands_dict=hands,
            orbital_system=self.orbital_system,
            particle_sys=self.particle_system
        )

        pygame.display.flip()

    def run(self, max_frames=None):
        frame_count = 0
        while self.running:
            dt = self.clock.tick(settings.TARGET_FPS) / 1000.0
            # Clamp dt to prevent physics explosion if a frame lags
            dt = min(0.05, max(0.001, dt))
            self.fps = self.clock.get_fps()

            self.handle_events()
            hands = self.update_physics(dt)
            self.render_scene(hands)

            frame_count += 1
            if max_frames and frame_count >= max_frames:
                break

        self.cleanup()

    def cleanup(self):
        print("[PHANTOM] Terminating application & releasing optical hardware...")
        self.camera.release()
        pygame.quit()

