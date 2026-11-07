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
        
        # Distant quantum starfield
        self._init_quantum_starfield()
        self.init_gl()

    def _init_quantum_starfield(self):
        count = 320
        self.stars_pos = np.random.uniform(-18.0, 18.0, size=(count, 3)).astype(np.float32)
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
        self.materials.set_additive_glow()
        glPointSize(1.5)
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.stars_pos)
        glColor4f(0.5, 0.8, 1.0, 0.35)
        glDrawArrays(GL_POINTS, 0, len(self.stars_pos))
        glDisableClientState(GL_VERTEX_ARRAY)

    def render_grid_plane(self, center_singularity):
        """
        Draws the holographic floor grid with gravitational curvature
        deflection bending towards the virtual singularity.
        """
        self.materials.set_additive_glow()
        glColor4fv(settings.COLOR_GRID)
        glLineWidth(1.0)
        
        y_floor = -3.8
        grid_range = 10.0
        step = 1.0
        
        # Gravitational bending helper
        cx, cz = center_singularity[0], center_singularity[2]

        glBegin(GL_LINES)
        curr = -grid_range
        while curr <= grid_range:
            # Longitudinal lines with gravitational deflection
            for z_val in np.arange(-16.0, 2.0, 1.5):
                z_next = z_val + 1.5
                
                # Point A
                dx = curr - cx
                dz = z_val - cz
                d2 = dx * dx + dz * dz + 0.5
                bend_a = settings.LENSING_STRENGTH * 0.45 / d2
                pA_x = curr - dx * bend_a
                pA_y = y_floor - bend_a * 0.3
                pA_z = z_val - dz * bend_a

                # Point B
                dx_b = curr - cx
                dz_b = z_next - cz
                d2_b = dx_b * dx_b + dz_b * dz_b + 0.5
                bend_b = settings.LENSING_STRENGTH * 0.45 / d2_b
                pB_x = curr - dx_b * bend_b
                pB_y = y_floor - bend_b * 0.3
                pB_z = z_next - dz_b * bend_b

                glVertex3f(pA_x, pA_y, pA_z)
                glVertex3f(pB_x, pB_y, pB_z)

            # Lateral lines
            glVertex3f(-grid_range, y_floor, curr - 7.0)
            glVertex3f(grid_range, y_floor, curr - 7.0)
            curr += step
        glEnd()

    def render_hand_skeletons(self, hands_dict, warp_fields, grabbed_body=None):
        """
        Renders tracked hand skeletons, metric distortion warp bubbles,
        and energized pinch-to-launch tether lightning.
        """
        self.materials.set_additive_glow()
        glLineWidth(2.2)

        for label, hand in hands_dict.items():
            if not hand.is_present:
                continue

            pts = hand.smoothed_world_landmarks
            is_right = (label == "Right")
            node_color = settings.COLOR_CYAN if is_right else settings.COLOR_PLASMA
            
            # 1. Skeletal Laser Links
            glColor4f(node_color[0], node_color[1], node_color[2], 0.65)
            glBegin(GL_LINES)
            for j1, j2 in HAND_CONNECTIONS:
                glVertex3fv(pts[j1])
                glVertex3fv(pts[j2])
            glEnd()

            # 2. Glowing Landmark Nodes
            glColor4f(1.0, 1.0, 1.0, 0.95)
            for i, p in enumerate(pts):
                glPushMatrix()
                glTranslatef(p[0], p[1], p[2])
                r = 0.055 if i in [4, 8, 12, 16, 20] else 0.035
                self.geometry.draw_sphere(radius=r, slices=8, stacks=8)
                glPopMatrix()

            # 3. 3D Spatial Warp Bubble (Distortion Field)
            glPushMatrix()
            glTranslatef(hand.palm_center_world[0], hand.palm_center_world[1], hand.palm_center_world[2])
            glLineWidth(1.2)
            warp_r = settings.WARP_BASE_RADIUS * (0.8 + 0.3 * hand.warp_intensity)
            self.geometry.draw_warp_bubble(radius=warp_r, intensity=hand.warp_intensity)
            glPopMatrix()

            # 4. Energized Tether when an Orbital Object is Grabbed
            if grabbed_body and grabbed_body.is_grabbed and grabbed_body.grabbed_hand_label == label:
                glLineWidth(2.4)
                self.geometry.draw_energy_beam(
                    hand.pinch_world_pos,
                    grabbed_body.world_pos,
                    color=settings.COLOR_WHITE,
                    jitter=0.08
                )

    def render_advanced_energy_core(self, center_pos, effects_mgr, field_intensity=0.5):
        """
        Renders the multi-layered Advanced Energy Core:
        - Layer 1: Event Horizon Shadow + Razor Photon Ring
        - Layer 2: Relativistic Accretion Disk with Keplerian rotation & Doppler beaming
        - Layer 3: Dual Counter-Rotating Icosahedrons
        - Layer 4: Orthogonal Gimbal Torus Rings
        - Layer 5: Pulsating Geodesic Energy Shells
        """
        pulse = 1.0 + 0.16 * math.sin(effects_mgr.pulse_phase)
        core_scale = (0.55 + 0.25 * field_intensity) * pulse

        glPushMatrix()
        glTranslatef(center_pos[0], center_pos[1], center_pos[2])

        # -------------------------------------------------------------
        # LAYER 1: VIRTUAL SINGULARITY (Dark Event Horizon & Photon Halo)
        # -------------------------------------------------------------
        # A. Dark Event Horizon Sphere (Absorptive silence)
        self.materials.set_standard_alpha()
        glColor4fv(settings.COLOR_SINGULARITY)
        self.geometry.draw_event_horizon(radius=settings.EVENT_HORIZON_RADIUS * core_scale)

        # B. Razor-Sharp Photon Ring (Gravitational lensing light loop)
        self.materials.set_additive_glow()
        glLineWidth(2.6)
        glColor4f(settings.COLOR_WHITE[0], settings.COLOR_WHITE[1], settings.COLOR_WHITE[2], 0.95)
        self.geometry.draw_photon_ring(radius=settings.PHOTON_RING_RADIUS * core_scale, segments=64)
        
        # Secondary resonant halo
        glColor4f(settings.COLOR_CYAN[0], settings.COLOR_CYAN[1], settings.COLOR_CYAN[2], 0.45)
        self.geometry.draw_photon_ring(radius=settings.PHOTON_RING_RADIUS * core_scale * 1.12, segments=48)

        # -------------------------------------------------------------
        # LAYER 2: RELATIVISTIC ACCRETION DISK
        # -------------------------------------------------------------
        glPushMatrix()
        glRotatef(math.degrees(settings.ACCRETION_DISK_TILT), 1.0, 0.0, 0.4)
        self.geometry.draw_accretion_disk(
            inner_r=settings.ACCRETION_DISK_INNER * core_scale,
            outer_r=settings.ACCRETION_DISK_OUTER * core_scale,
            time_val=effects_mgr.accretion_time
        )
        glPopMatrix()

        # -------------------------------------------------------------
        # LAYER 3: DUAL COUNTER-ROTATING ICOSAHEDRONS
        # -------------------------------------------------------------
        # Inner Electric Cyan Icosahedron
        glPushMatrix()
        glRotatef(effects_mgr.core_rot_ico_1, 1.0, 0.5, 0.2)
        glLineWidth(1.8)
        glColor4f(settings.COLOR_CYAN[0], settings.COLOR_CYAN[1], settings.COLOR_CYAN[2], 0.85)
        self.geometry.draw_icosahedron(scale=0.52 * core_scale, show_faces=False)
        glPopMatrix()

        # Outer Ultraviolet Icosahedron with Translucent Face Glow
        glPushMatrix()
        glRotatef(effects_mgr.core_rot_ico_2, -0.4, 1.0, 0.6)
        glLineWidth(1.6)
        glColor4f(settings.COLOR_VIOLET[0], settings.COLOR_VIOLET[1], settings.COLOR_VIOLET[2], 0.25)
        self.geometry.draw_icosahedron(scale=0.74 * core_scale, show_faces=True)
        glPopMatrix()

        # -------------------------------------------------------------
        # LAYER 4: ORTHOGONAL GIMBAL TORUS RINGS
        # -------------------------------------------------------------
        # Equatorial Gimbal
        glPushMatrix()
        glRotatef(effects_mgr.gimbal_torus_1, 0.0, 1.0, 0.0)
        glLineWidth(1.4)
        glColor4f(settings.COLOR_CYAN[0], settings.COLOR_CYAN[1], settings.COLOR_CYAN[2], 0.60)
        self.geometry.draw_torus(major_radius=0.98 * core_scale, minor_radius=0.045 * core_scale, rings=24, sides=6)
        glPopMatrix()

        # Polar Meridian Gimbal
        glPushMatrix()
        glRotatef(effects_mgr.gimbal_torus_2, 1.0, 0.0, 0.0)
        glLineWidth(1.4)
        glColor4f(settings.COLOR_PLASMA[0], settings.COLOR_PLASMA[1], settings.COLOR_PLASMA[2], 0.55)
        self.geometry.draw_torus(major_radius=1.14 * core_scale, minor_radius=0.045 * core_scale, rings=24, sides=6)
        glPopMatrix()

        # -------------------------------------------------------------
        # LAYER 5: PULSATING GEODESIC ENERGY SHELLS
        # -------------------------------------------------------------
        for phase in effects_mgr.shell_phases:
            shell_r = (0.6 + 0.9 * (phase / (math.pi * 2.0))) * core_scale
            shell_alpha = max(0.0, (1.0 - (phase / (math.pi * 2.0))) * 0.35)
            glLineWidth(1.0)
            self.geometry.draw_pulsating_shell(radius=shell_r, alpha=shell_alpha)

        glPopMatrix()

    def render_motion_trails(self, orbital_system):
        self.materials.set_additive_glow()
        glLineWidth(1.4)

        for body in orbital_system.bodies:
            trail_len = len(body.trail)
            if trail_len < 2:
                continue

            glBegin(GL_LINE_STRIP)
            for idx, pos in enumerate(body.trail):
                alpha_factor = (idx / trail_len) * 0.50
                glColor4f(body.color[0], body.color[1], body.color[2], alpha_factor)
                glVertex3fv(pos)
            glEnd()

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

