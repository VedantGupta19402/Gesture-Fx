"""
PHANTOM: ORBITAL MODE — Materials & OpenGL State Management
Provides additive glow states, alpha blending, and scientific color lookups.
"""

from OpenGL.GL import *
from config import settings

class MaterialManager:
    @staticmethod
    def set_additive_glow():
        """Configures OpenGL for cinematic neon sci-fi additive blending."""
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glDepthMask(GL_FALSE)  # Avoid depth-occluding glowing particles

    @staticmethod
    def set_standard_alpha():
        """Configures OpenGL for clean HUD and structural transparency."""
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(GL_TRUE)

    @staticmethod
    def enable_antialiased_lines():
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_POINT_SMOOTH)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

    @staticmethod
    def set_color(color, alpha_mult=1.0):
        if len(color) == 4:
            glColor4f(color[0], color[1], color[2], color[3] * alpha_mult)
        else:
            glColor4f(color[0], color[1], color[2], alpha_mult)

