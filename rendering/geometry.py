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

    def _init_icosahedron_data(self):
        phi = (1.0 + math.sqrt(5.0)) / 2.0
        # 12 vertices of an icosahedron normalized
        raw_v = [
            (-1,  phi, 0), ( 1,  phi, 0), (-1, -phi, 0), ( 1, -phi, 0),
            (0, -1,  phi), (0,  1,  phi), (0, -1, -phi), (0,  1, -phi),
            ( phi, 0, -1), ( phi, 0,  1), (-phi, 0, -1), (-phi, 0,  1)
        ]
        self.ico_verts = [np.array(v, dtype=np.float32) / math.sqrt(1 + phi*phi) for v in raw_v]
        self.ico_faces = [
            (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
            (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
            (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
            (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)
        ]
        # Unique edges for wireframe rendering
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

    def draw_sphere(self, radius=0.25, slices=14, stacks=14, wireframe=False):
        if wireframe:
            gluQuadricDrawStyle(self.quadric, GLU_LINE)
        else:
            gluQuadricDrawStyle(self.quadric, GLU_FILL)
        gluSphere(self.quadric, radius, slices, stacks)

    def draw_cube(self, scale=1.0, inner_cross=True):
        glBegin(GL_LINES)
        for i1, i2 in self.cube_edges:
            v1 = self.cube_verts[i1] * scale
            v2 = self.cube_verts[i2] * scale
            glVertex3f(v1[0], v1[1], v1[2])
            glVertex3f(v2[0], v2[1], v2[2])
        if inner_cross:
            # Subtle internal scientific diagnostic diagonals
            d = 0.25 * scale
            glVertex3f(-d, 0, 0); glVertex3f(d, 0, 0)
            glVertex3f(0, -d, 0); glVertex3f(0, d, 0)
            glVertex3f(0, 0, -d); glVertex3f(0, 0, d)
        glEnd()

    def draw_icosahedron(self, scale=1.0, show_faces=True):
        if show_faces:
            # Translucent structural faces
            glBegin(GL_TRIANGLES)
            for f in self.ico_faces:
                v0 = self.ico_verts[f[0]] * scale
                v1 = self.ico_verts[f[1]] * scale
                v2 = self.ico_verts[f[2]] * scale
                glVertex3f(v0[0], v0[1], v0[2])
                glVertex3f(v1[0], v1[1], v1[2])
                glVertex3f(v2[0], v2[1], v2[2])
            glEnd()
        
        # High-contrast neon edges
        glBegin(GL_LINES)
        for i1, i2 in self.ico_edges:
            v1 = self.ico_verts[i1] * scale
            v2 = self.ico_verts[i2] * scale
            glVertex3f(v1[0], v1[1], v1[2])
            glVertex3f(v2[0], v2[1], v2[2])
        glEnd()

    def draw_octahedron(self, scale=1.0):
        glBegin(GL_LINES)
        for i1, i2 in self.octa_edges:
            v1 = self.octa_verts[i1] * scale
            v2 = self.octa_verts[i2] * scale
            glVertex3f(v1[0], v1[1], v1[2])
            glVertex3f(v2[0], v2[1], v2[2])
        glEnd()

    def draw_torus(self, major_radius=1.0, minor_radius=0.12, rings=28, sides=10):
        """Renders a parametric 3D torus ring with glowing wireframe segments."""
        glBegin(GL_LINES)
        for i in range(rings):
            u1 = 2.0 * math.pi * i / rings
            u2 = 2.0 * math.pi * (i + 1) / rings
            cos_u1, sin_u1 = math.cos(u1), math.sin(u1)
            cos_u2, sin_u2 = math.cos(u2), math.sin(u2)

            for j in range(sides):
                v1 = 2.0 * math.pi * j / sides
                v2 = 2.0 * math.pi * (j + 1) / sides
                cos_v1, sin_v1 = math.cos(v1), math.sin(v1)
                cos_v2, sin_v2 = math.cos(v2), math.sin(v2)

                # Point (i, j)
                p0 = np.array([
                    (major_radius + minor_radius * cos_v1) * cos_u1,
                    (major_radius + minor_radius * cos_v1) * sin_u1,
                    minor_radius * sin_v1
                ], dtype=np.float32)

                # Point (i+1, j)
                p1 = np.array([
                    (major_radius + minor_radius * cos_v1) * cos_u2,
                    (major_radius + minor_radius * cos_v1) * sin_u2,
                    minor_radius * sin_v1
                ], dtype=np.float32)

                # Point (i, j+1)
                p2 = np.array([
                    (major_radius + minor_radius * cos_v2) * cos_u1,
                    (major_radius + minor_radius * cos_v2) * sin_u1,
                    minor_radius * sin_v2
                ], dtype=np.float32)

                glVertex3f(p0[0], p0[1], p0[2])
                glVertex3f(p1[0], p1[1], p1[2])
                glVertex3f(p0[0], p0[1], p0[2])
                glVertex3f(p2[0], p2[1], p2[2])
        glEnd()

    def draw_orbital_ring(self, radius=5.0, segments=64, tick_count=16):
        """Draws a smooth circular orbital track with scientific calibration tick marks."""
        # Ring loop
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            theta = 2.0 * math.pi * i / segments
            x = radius * math.cos(theta)
            y = radius * math.sin(theta)
            glVertex3f(x, y, 0.0)
        glEnd()

        # Calibration tick marks
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

