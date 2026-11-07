"""
PHANTOM: ORBITAL MODE — Holographic 3D Master Scene Renderer
Composites the spatial distortion engine: event horizon, photon ring, relativistic
accretion disk, counter-rotating gimbals, pulsating shells, hand warp bubbles,
and energized lightning tethers.
"""

import math
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from config import settings
from rendering.geometry import GeometryVault
from rendering.materials import MaterialManager

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index
    (5, 9), (9, 10), (10, 11), (11, 12),    # Middle
    (9, 13), (13, 14), (14, 15), (15, 16), # Ring
    (13, 17), (17, 18), (18, 19), (19, 20),# Pinky
    (0, 17)                                # Palm Base
]

class MasterRenderer:
    def __init__(self, width=settings.WINDOW_WIDTH, height=settings.WINDOW_HEIGHT):
        self.width = width
        self.height = height
        self.geometry = GeometryVault()
        self.materials = MaterialManager()
        
        # Camera orbit view state
        self.cam_rot_x = 0.0
        self.cam_rot_y = 0.0
        self.cam_zoom = -8.5
        
        # Distant quantum starfield for atmospheric depth
        self._init_quantum_starfield()
        self.init_gl()

    def _init_quantum_starfield(self):
        count = 300
        self.stars_pos = np.random.uniform(-18.0, 18.0, size=(count, 3)).astype(np.float32)
        # Deep z range: -30 to -5
        self.stars_pos[:, 2] = np.random.uniform(-35.0, -10.0, size=count)
        self.stars_brightness = np.random.uniform(0.12, 0.45, size=count).astype(np.float32)

    def init_gl(self):
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        
        glClearColor(settings.COLOR_BG[0], settings.COLOR_BG[1], settings.COLOR_BG[2], 1.0)
        self.materials.enable_antialiased_lines()
        glPointSize(settings.PARTICLE_POINT_SIZE)
        glLineWidth(1.4)
        self.set_viewport(self.width, self.height)

    def set_viewport(self, width, height):
        self.width = max(1, width)
        self.height = max(1, height)
        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(settings.FOV, self.width / self.height, settings.NEAR_CLIP, settings.FAR_CLIP)
        glMatrixMode(GL_MODELVIEW)

    def begin_frame(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Apply camera view transformations
        glTranslatef(0.0, 0.0, self.cam_zoom)
        glRotatef(self.cam_rot_x, 1.0, 0.0, 0.0)
        glRotatef(self.cam_rot_y, 0.0, 1.0, 0.0)

    def render_starfield(self):
        """Draws subtle distant quantum points to establish spatial depth."""
        self.materials.set_additive_glow()
        glPointSize(1.5)
        glBegin(GL_POINTS)
        for i in range(len(self.stars_pos)):
            b = self.stars_brightness[i]
            glColor4f(0.5, 0.8, 1.0, b)
            glVertex3fv(self.stars_pos[i])
        glEnd()

    def render_grid_plane(self):
        """Draws a subtle holographic floor coordinate grid."""
        self.materials.set_additive_glow()
        glColor4fv(settings.COLOR_GRID)
        glLineWidth(1.0)
        
        y_floor = -3.8
        grid_range = 10.0
        step = 1.0
        
        glBegin(GL_LINES)
        curr = -grid_range
        while curr <= grid_range:
            glVertex3f(curr, y_floor, -16.0)
            glVertex3f(curr, y_floor, 2.0)
            glVertex3f(-grid_range, y_floor, curr - 7.0)
            glVertex3f(grid_range, y_floor, curr - 7.0)
            curr += step
        glEnd()

    def render_hand_skeletons(self, hands_dict):
        """Renders tracked hand skeletons directly into 3D world space."""
        self.materials.set_additive_glow()
        glLineWidth(2.2)

        for label, hand in hands_dict.items():
            if not hand.is_present:
                continue

            pts = hand.smoothed_world_landmarks
            is_right = (label == "Right")
            node_color = settings.COLOR_CYAN if is_right else settings.COLOR_PLASMA
            
            # Draw skeletal laser links
            glColor4f(node_color[0], node_color[1], node_color[2], 0.65)
            glBegin(GL_LINES)
            for j1, j2 in HAND_CONNECTIONS:
                glVertex3fv(pts[j1])
                glVertex3fv(pts[j2])
            glEnd()

            # Draw glowing landmark joint nodes
            glColor4f(1.0, 1.0, 1.0, 0.95)
            for i, p in enumerate(pts):
                glPushMatrix()
                glTranslatef(p[0], p[1], p[2])
                r = 0.055 if i in [4, 8, 12, 16, 20] else 0.035
                self.geometry.draw_sphere(radius=r, slices=8, stacks=8)
                glPopMatrix()

            # Interaction aura around palm center
            glPushMatrix()
            glTranslatef(hand.palm_center_world[0], hand.palm_center_world[1], hand.palm_center_world[2])
            glColor4f(node_color[0], node_color[1], node_color[2], 0.25)
            self.geometry.draw_sphere(radius=0.28, slices=10, stacks=10, wireframe=True)
            glPopMatrix()

    def render_motion_trails(self, orbital_system):
        """Renders persistent fading trails behind orbiting celestial objects."""
        self.materials.set_additive_glow()
        glLineWidth(1.2)

        for body in orbital_system.bodies:
            trail_len = len(body.trail)
            if trail_len < 2:
                continue

            glBegin(GL_LINE_STRIP)
            for idx, pos in enumerate(body.trail):
                alpha_factor = (idx / trail_len) * 0.45
                glColor4f(body.color[0], body.color[1], body.color[2], alpha_factor)
                glVertex3fv(pos)
            glEnd()

    def render_energy_core(self, center_pos, effects_mgr, field_intensity=0.5):
        """Renders the pulsating central scientific energy core."""
        self.materials.set_additive_glow()
        
        pulse = 1.0 + 0.18 * math.sin(effects_mgr.pulse_phase)
        core_scale = (0.55 + 0.25 * field_intensity) * pulse

        glPushMatrix()
        glTranslatef(center_pos[0], center_pos[1], center_pos[2])

        # 1. Inner Radiant Sphere
        glColor4f(settings.COLOR_WHITE[0], settings.COLOR_WHITE[1], settings.COLOR_WHITE[2], 0.85)
        self.geometry.draw_sphere(radius=0.18 * core_scale, slices=12, stacks=12)

        # 2. Dual Counter-Rotating Icosahedrons
        glPushMatrix()
        glRotatef(effects_mgr.core_rotation_1, 1.0, 0.5, 0.0)
        glColor4f(settings.COLOR_CYAN[0], settings.COLOR_CYAN[1], settings.COLOR_CYAN[2], 0.75)
        self.geometry.draw_icosahedron(scale=0.45 * core_scale, show_faces=False)
        glPopMatrix()

        glPushMatrix()
        glRotatef(effects_mgr.core_rotation_2, 0.0, 1.0, 0.5)
        glColor4f(settings.COLOR_VIOLET[0], settings.COLOR_VIOLET[1], settings.COLOR_VIOLET[2], 0.65)
        self.geometry.draw_icosahedron(scale=0.68 * core_scale, show_faces=False)
        glPopMatrix()

        # 3. Equatorial Orbital Energy Rings
        glColor4f(settings.COLOR_PLASMA[0], settings.COLOR_PLASMA[1], settings.COLOR_PLASMA[2], 0.5)
        self.geometry.draw_orbital_ring(radius=0.95 * core_scale, segments=36, tick_count=8)

        glPopMatrix()

    def render_orbital_bodies(self, orbital_system):
        """Renders all geometric objects in INNER, MIDDLE, and OUTER orbital tiers."""
        self.materials.set_additive_glow()

        for body in orbital_system.bodies:
            glPushMatrix()
            glTranslatef(body.world_pos[0], body.world_pos[1], body.world_pos[2])
            
            # Apply individual rotational dynamics
            glRotatef(body.rot_angles[0], 1.0, 0.0, 0.0)
            glRotatef(body.rot_angles[1], 0.0, 1.0, 0.0)
            glRotatef(body.rot_angles[2], 0.0, 0.0, 1.0)

            scale = body.scale
            glColor4fv(body.color)

            # Dispatch based on scientific geometry type
            gt = body.geom_type
            if gt == "icosahedron":
                self.geometry.draw_icosahedron(scale=scale, show_faces=True)
            elif gt == "wireframe_cube":
                glLineWidth(1.8)
                self.geometry.draw_cube(scale=scale, inner_cross=True)
            elif gt == "torus_ring":
                glLineWidth(1.4)
                self.geometry.draw_torus(major_radius=scale, minor_radius=scale * 0.18)
            elif gt == "octahedron":
                glLineWidth(1.8)
                self.geometry.draw_octahedron(scale=scale)
            elif gt == "tetrahedron":
                glLineWidth(1.6)
                self.geometry.draw_octahedron(scale=scale * 0.8)
            elif gt == "orbital_ring":
                glLineWidth(1.4)
                self.geometry.draw_orbital_ring(radius=scale * 1.5, segments=48, tick_count=12)
            elif gt == "celestial_bracket":
                glLineWidth(2.0)
                self.geometry.draw_celestial_bracket(radius=scale * 1.8, arc_degrees=60)
            else:
                self.geometry.draw_sphere(radius=scale * 0.45, slices=10, stacks=10, wireframe=True)

            glPopMatrix()

    def render_shockwaves(self, effects_mgr):
        """Renders expanding 3D energy shockwave rings."""
        self.materials.set_additive_glow()
        glLineWidth(2.5)

        for sw in effects_mgr.shockwaves:
            alpha = sw.alpha
            if alpha <= 0.01:
                continue

            glPushMatrix()
            glTranslatef(sw.origin[0], sw.origin[1], sw.origin[2])

            # Orient ring perpendicular to shockwave normal
            # For screen normal (0, 0, 1) default is flat on XY
            glColor4f(sw.color[0], sw.color[1], sw.color[2], alpha * 0.85)
            self.geometry.draw_orbital_ring(radius=sw.radius, segments=56, tick_count=12)

            # Secondary resonant echo ring
            glColor4f(settings.COLOR_VIOLET[0], settings.COLOR_VIOLET[1], settings.COLOR_VIOLET[2], alpha * 0.4)
            self.geometry.draw_orbital_ring(radius=max(0.1, sw.radius * 0.82), segments=40, tick_count=0)

            glPopMatrix()

    def render_particles(self, particle_sys):
        """Renders vectorized particle simulation via fast point primitives."""
        self.materials.set_additive_glow()
        glPointSize(settings.PARTICLE_POINT_SIZE)

        # Draw point cloud using batch vertex calls
        glBegin(GL_POINTS)
        for i in range(particle_sys.count):
            c = particle_sys.colors[i]
            glColor4f(c[0], c[1], c[2], c[3])
            glVertex3fv(particle_sys.positions[i])
        glEnd()

