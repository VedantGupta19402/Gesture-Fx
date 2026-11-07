"""
PHANTOM: ORBITAL MODE — 3D Holographic Geometry Engine (Hardware Accelerated)
Compiles geometric primitives into GPU display lists (Icosahedrons, Torus Rings,
Accretion Disks, Event Horizon Spheres, Photon Rings, Pulsating Shells, Warp Bubbles).
"""

import math
import random
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from config import settings

class GeometryVault:
    def __init__(self):
        self._init_icosahedron_data()
        self._init_cube_data()
        self._init_octahedron_data()
        self.quadric = gluNewQuadric()
        gluQuadricNormals(self.quadric, GLU_SMOOTH)
        self._compile_display_lists()

    def _init_icosahedron_data(self):
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        raw_v = [
            (-1,  phi, 0), ( 1,  phi, 0), (-1, -phi, 0), ( 1, -phi, 0),
            (0, -1,  phi), (0,  1,  phi), (0, -1, -phi), (0,  1, -phi),
            ( phi, 0, -1), ( phi, 0,  1), (-phi, 0, -1), (-phi, 0,  1)
        ]
        self.ico_verts = [np.array(v, dtype=np.float32) / math.sqrt(1 + phi * phi) for v in raw_v]
        self.ico_faces = [
            (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
            (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
            (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
            (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)
        ]
        edges = set()
        for f in self.ico_faces:
            for i in range(3):
                e = tuple(sorted((f[i], f[(i + 1) % 3])))
                edges.add(e)
        self.ico_edges = list(edges)

    def _init_cube_data(self):
        s = 0.5
        self.cube_verts = [
            np.array([-s, -s, -s], dtype=np.float32),
            np.array([ s, -s, -s], dtype=np.float32),
            np.array([ s,  s, -s], dtype=np.float32),
            np.array([-s,  s, -s], dtype=np.float32),
            np.array([-s, -s,  s], dtype=np.float32),
            np.array([ s, -s,  s], dtype=np.float32),
            np.array([ s,  s,  s], dtype=np.float32),
            np.array([-s,  s,  s], dtype=np.float32)
        ]
        self.cube_edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]

    def _init_octahedron_data(self):
        self.octa_verts = [
            np.array([ 1.0,  0.0,  0.0], dtype=np.float32),
            np.array([-1.0,  0.0,  0.0], dtype=np.float32),
            np.array([ 0.0,  1.0,  0.0], dtype=np.float32),
            np.array([ 0.0, -1.0,  0.0], dtype=np.float32),
            np.array([ 0.0,  0.0,  1.0], dtype=np.float32),
            np.array([ 0.0,  0.0, -1.0], dtype=np.float32),
        ]
        self.octa_edges = [
            (0, 2), (2, 1), (1, 3), (3, 0),
            (0, 4), (4, 1), (1, 5), (5, 0),
            (2, 4), (4, 3), (3, 5), (5, 2)
        ]

    def _compile_display_lists(self):
        # 1. Cube
        self.dl_cube = glGenLists(1)
        glNewList(self.dl_cube, GL_COMPILE)
        glBegin(GL_LINES)
        for i1, i2 in self.cube_edges:
            v1 = self.cube_verts[i1]
            v2 = self.cube_verts[i2]
            glVertex3f(v1[0], v1[1], v1[2])
            glVertex3f(v2[0], v2[1], v2[2])
        d = 0.25
        glVertex3f(-d, 0, 0); glVertex3f(d, 0, 0)
        glVertex3f(0, -d, 0); glVertex3f(0, d, 0)
        glVertex3f(0, 0, -d); glVertex3f(0, 0, d)
        glEnd()
        glEndList()

        # 2. Icosahedron Edges
        self.dl_ico_edges = glGenLists(1)
        glNewList(self.dl_ico_edges, GL_COMPILE)
        glBegin(GL_LINES)
        for i1, i2 in self.ico_edges:
            v1 = self.ico_verts[i1]
            v2 = self.ico_verts[i2]
            glVertex3f(v1[0], v1[1], v1[2])
            glVertex3f(v2[0], v2[1], v2[2])
        glEnd()
        glEndList()

        # 3. Icosahedron Faces
        self.dl_ico_faces = glGenLists(1)
        glNewList(self.dl_ico_faces, GL_COMPILE)
        glBegin(GL_TRIANGLES)
        for f in self.ico_faces:
            v0 = self.ico_verts[f[0]]
            v1 = self.ico_verts[f[1]]
            v2 = self.ico_verts[f[2]]
            glVertex3f(v0[0], v0[1], v0[2])
            glVertex3f(v1[0], v1[1], v1[2])
            glVertex3f(v2[0], v2[1], v2[2])
        glEnd()
        glEndList()

        # 4. Octahedron
        self.dl_octa = glGenLists(1)
        glNewList(self.dl_octa, GL_COMPILE)
        glBegin(GL_LINES)
        for i1, i2 in self.octa_edges:
            v1 = self.octa_verts[i1]
            v2 = self.octa_verts[i2]
            glVertex3f(v1[0], v1[1], v1[2])
            glVertex3f(v2[0], v2[1], v2[2])
        glEnd()
        glEndList()

        # 5. Unit Torus
        self.dl_torus = glGenLists(1)
        glNewList(self.dl_torus, GL_COMPILE)
        rings = 20
        sides = 6
        glBegin(GL_LINES)
        for i in range(rings):
            u1 = 2.0 * math.pi * i / rings
            u2 = 2.0 * math.pi * (i + 1) / rings
            cos_u1, sin_u1 = math.cos(u1), math.sin(u1)
            cos_u2, sin_u2 = math.cos(u2), math.sin(u2)
            for j in range(sides):
                v = 2.0 * math.pi * j / sides
                cos_v, sin_v = math.cos(v), math.sin(v)
                r_maj = 1.0
                r_min = 0.14
                p0_x = (r_maj + r_min * cos_v) * cos_u1
                p0_y = (r_maj + r_min * cos_v) * sin_u1
                p0_z = r_min * sin_v
                p1_x = (r_maj + r_min * cos_v) * cos_u2
                p1_y = (r_maj + r_min * cos_v) * sin_u2
                p1_z = r_min * sin_v
                glVertex3f(p0_x, p0_y, p0_z)
                glVertex3f(p1_x, p1_y, p1_z)
        glEnd()
        glEndList()

        # 6. Photon Ring (Unit)
        self.dl_photon_ring = glGenLists(1)
        glNewList(self.dl_photon_ring, GL_COMPILE)
        glBegin(GL_LINE_LOOP)
        for s in range(48):
            th = 2.0 * math.pi * s / 48
            glVertex3f(math.cos(th), math.sin(th), 0.0)
        glEnd()
        glEndList()

    def draw_sphere(self, radius=0.25, slices=12, stacks=12, wireframe=False):
        if wireframe:
            gluQuadricDrawStyle(self.quadric, GLU_LINE)
        else:
            gluQuadricDrawStyle(self.quadric, GLU_FILL)
        gluSphere(self.quadric, radius, slices, stacks)

    def draw_event_horizon(self, radius=0.36):
        gluQuadricDrawStyle(self.quadric, GLU_FILL)
        gluSphere(self.quadric, radius, 16, 16)

    def draw_photon_ring(self, radius=0.54, segments=48):
        glPushMatrix()
        glScalef(radius, radius, radius)
        glCallList(self.dl_photon_ring)
        glPopMatrix()

    def draw_accretion_disk(self, inner_r=0.75, outer_r=2.45, time_val=0.0):
        ring_count = 3
        segments = 32
        dr = (outer_r - inner_r) / float(ring_count)

        for ring_idx in range(ring_count):
            r1 = inner_r + ring_idx * dr
            r2 = r1 + dr * 0.82
            kepler_speed = (inner_r / r1) ** 1.5
            ring_phase = time_val * kepler_speed * 1.8

            glBegin(GL_LINES)
            for s in range(segments):
                theta1 = (2.0 * math.pi * s / segments) + ring_phase
                theta2 = (2.0 * math.pi * (s + 0.5) / segments) + ring_phase

                doppler_factor = 0.5 + 0.5 * math.cos(theta1)
                alpha = (0.20 + 0.60 * doppler_factor) * (1.0 - (ring_idx / ring_count) * 0.40)
                
                r_col = 0.0 + doppler_factor * 0.95
                g_col = 0.6 + doppler_factor * 0.38
                glColor4f(r_col, g_col, 1.0, alpha)

                glVertex3f(r1 * math.cos(theta1), r1 * math.sin(theta1), 0.0)
                glVertex3f(r2 * math.cos(theta2), r2 * math.sin(theta2), 0.0)
            glEnd()

    def draw_pulsating_shell(self, radius=1.0, alpha=0.35):
        glColor4f(settings.COLOR_CYAN[0], settings.COLOR_CYAN[1], settings.COLOR_CYAN[2], alpha)
        glPushMatrix()
        glScalef(radius, radius, radius)
        glCallList(self.dl_ico_edges)
        glPopMatrix()

    def draw_warp_bubble(self, radius=1.4, intensity=1.0):
        segs = 20
        glColor4f(settings.COLOR_CYAN[0], settings.COLOR_CYAN[1], settings.COLOR_CYAN[2], 0.22 * intensity)
        for tilt_axis in [0, 1, 2]:
            glBegin(GL_LINE_LOOP)
            for i in range(segs):
                theta = 2.0 * math.pi * i / segs
                c, s = radius * math.cos(theta), radius * math.sin(theta)
                if tilt_axis == 0:
                    glVertex3f(c, s, 0.0)
                elif tilt_axis == 1:
                    glVertex3f(c, 0.0, s)
                else:
                    glVertex3f(0.0, c, s)
            glEnd()

    def draw_energy_beam(self, p1, p2, color=settings.COLOR_WHITE, jitter=0.06):
        segments = 5
        glBegin(GL_LINE_STRIP)
        glColor4fv(color)
        glVertex3fv(p1)
        for i in range(1, segments):
            t = i / float(segments)
            mid = p1 + (p2 - p1) * t
            noise = np.random.uniform(-jitter, jitter, size=3).astype(np.float32)
            glVertex3fv(mid + noise)
        glVertex3fv(p2)
        glEnd()

    def draw_cube(self, scale=1.0, inner_cross=True):
        glPushMatrix()
        glScalef(scale, scale, scale)
        glCallList(self.dl_cube)
        glPopMatrix()

    def draw_icosahedron(self, scale=1.0, show_faces=True):
        glPushMatrix()
        glScalef(scale, scale, scale)
        if show_faces:
            glCallList(self.dl_ico_faces)
        glCallList(self.dl_ico_edges)
        glPopMatrix()

    def draw_octahedron(self, scale=1.0):
        glPushMatrix()
        glScalef(scale, scale, scale)
        glCallList(self.dl_octa)
        glPopMatrix()

    def draw_torus(self, major_radius=1.0, minor_radius=0.12, rings=20, sides=6):
        glPushMatrix()
        glScalef(major_radius, major_radius, major_radius)
        glCallList(self.dl_torus)
        glPopMatrix()

    def draw_orbital_ring(self, radius=5.0, segments=48, tick_count=12):
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            theta = 2.0 * math.pi * i / segments
            glVertex3f(radius * math.cos(theta), radius * math.sin(theta), 0.0)
        glEnd()

        if tick_count > 0:
            glBegin(GL_LINES)
            tick_len = radius * 0.05
            for i in range(tick_count):
                theta = 2.0 * math.pi * i / tick_count
                cos_t = math.cos(theta)
                sin_t = math.sin(theta)
                x1 = (radius - tick_len) * cos_t
                y1 = (radius - tick_len) * sin_t
                x2 = (radius + tick_len) * cos_t
                y2 = (radius + tick_len) * sin_t
                glVertex3f(x1, y1, 0.0)
                glVertex3f(x2, y2, 0.0)
            glEnd()

    def draw_celestial_bracket(self, radius=4.0, arc_degrees=45):
        """Draws an open sci-fi HUD bracket arc with corner accents."""
        segs = 16
        rad_start = -math.radians(arc_degrees / 2.0)
        rad_end = math.radians(arc_degrees / 2.0)
        step = (rad_end - rad_start) / segs

        glBegin(GL_LINE_STRIP)
        for i in range(segs + 1):
            theta = rad_start + i * step
            glVertex3f(radius * math.cos(theta), radius * math.sin(theta), 0.0)
        glEnd()

