"""
PHANTOM: ORBITAL MODE — Global Configuration & Design System
Art Direction: DARK SCIENTIFIC FUTURISM
Phase 2: SPATIAL DISTORTION & GRAVITATIONAL LENSING ENGINE
"""

import math

# Window & Display
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "PHANTOM // ORBITAL MODE — SPATIAL DISTORTION ENGINE"
TARGET_FPS = 60
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Field of View & Clipping
FOV = 60.0
NEAR_CLIP = 0.1
FAR_CLIP = 150.0
CAMERA_DEFAULT_POS = (0.0, 0.0, -8.5)

# Color Palette (RGBA float tuples, 0.0 - 1.0)
COLOR_BG = (0.010, 0.014, 0.024, 1.0)           # Deep Obsidian Lab Void
COLOR_CYAN = (0.0, 0.94, 1.0, 0.90)             # Electric Cyan (Primary telemetry & energy)
COLOR_PLASMA = (0.12, 0.45, 1.0, 0.85)          # Plasma Blue (Mid-layer orbits & Doppler receding)
COLOR_VIOLET = (0.68, 0.18, 0.98, 0.85)         # Ultraviolet (Outer resonant structures)
COLOR_WHITE = (0.95, 0.98, 1.0, 0.95)           # Pure Radiance (Core highlights & focal points)
COLOR_AMBER = (1.0, 0.65, 0.15, 0.9)            # Warning / Singularity overload
COLOR_GRID = (0.06, 0.14, 0.22, 0.18)           # Subtle Coordinate Grid
COLOR_TRAIL_FADE = 0.88                         # Trail persistence factor

# Simulation Modes
MODE_ORBITAL = "ORBITAL"
MODE_CHAOS = "CHAOS"
MODE_SINGULARITY = "SINGULARITY"

# Interaction Gestures
GESTURE_NONE = "SCANNING"
GESTURE_OPEN_PALM = "OPEN_PALM"
GESTURE_CLOSED_FIST = "CLOSED_FIST"
GESTURE_PINCH = "PINCH_MANIPULATE"
GESTURE_TWO_FINGERS = "DUAL_FINGER_AXIS"
GESTURE_SPREAD = "FIELD_EXPANSION"
GESTURE_COMPRESS = "FIELD_COMPRESSION"
GESTURE_SHOCKWAVE = "ENERGY_SHOCKWAVE"

# Orbital System Configuration
INNER_LAYER = {
    "count": 5,
    "radius_min": 1.3,
    "radius_max": 2.2,
    "speed_min": 1.4,
    "speed_max": 2.6,
    "scale_range": (0.16, 0.28),
    "types": ["octahedron", "tetrahedron", "cube"]
}

MIDDLE_LAYER = {
    "count": 7,
    "radius_min": 2.9,
    "radius_max": 4.5,
    "speed_min": 0.5,
    "speed_max": 1.1,
    "scale_range": (0.32, 0.52),
    "types": ["icosahedron", "wireframe_cube", "torus_ring"]
}

OUTER_LAYER = {
    "count": 5,
    "radius_min": 5.2,
    "radius_max": 7.8,
    "speed_min": 0.15,
    "speed_max": 0.45,
    "scale_range": (0.6, 1.1),
    "types": ["orbital_ring", "icosahedron", "celestial_bracket"]
}

# Particle System
MAX_PARTICLES = 1600
AMBIENT_DUST_COUNT = 350
PARTICLE_POINT_SIZE = 2.4
CORE_PULSE_SPEED = 2.5

# Gesture Recognition Parameters
PINCH_THRESHOLD = 0.065
FIST_THRESHOLD = 0.11
SWIPE_VELOCITY_THRESHOLD = 1.6  # World units per sec
GESTURE_CONFIRM_FRAMES = 2      # Hysteresis buffer
SMOOTHING_FACTOR = 0.22         # Landmark EMA factor

