"""
PHANTOM: ORBITAL MODE — Scientific Telemetry HUD Overlay
Renders high-precision aerospace / quantum research interface overlay,
body-relative tracking coordinates, warp strain, and kinetic lock readouts.
"""

import math
import pygame
from OpenGL.GL import *
from config import settings

class TelemetryHUD:
    def __init__(self, width=settings.WINDOW_WIDTH, height=settings.WINDOW_HEIGHT):
        self.width = width
        self.height = height
        self.is_visible = True
        
        # Initialize technical typography
        pygame.font.init()
        font_names = ["consolas", "couriernew", "lucidaconsole", "dejavusansmono"]
        self.font_main = None
        for fn in font_names:
            try:
                self.font_main = pygame.font.SysFont(fn, 13, bold=False)
                self.font_header = pygame.font.SysFont(fn, 15, bold=True)
                self.font_title = pygame.font.SysFont(fn, 18, bold=True)
                break
            except:
                continue
        if self.font_main is None:
            self.font_main = pygame.font.Font(None, 16)
            self.font_header = pygame.font.Font(None, 18)
            self.font_title = pygame.font.Font(None, 22)

        # Pre-allocate GL Texture for text blitting
        self.tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)
        self.tex_allocated = False

        # 2D surface for HUD overlay
        self.hud_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def set_viewport(self, width, height):
        self.width = max(1, width)
        self.height = max(1, height)
        self.hud_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.tex_allocated = False

    def toggle_visibility(self):
        self.is_visible = not self.is_visible

    def render(self, fps, camera_status, hands_dict, orbital_system, particle_sys, origin_pos, origin_mode):
        if not self.is_visible:
            return

        # Setup 2D Orthographic Projection
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # 1. Draw Vector Frame Accents (Corner Brackets & Borders)
        self._draw_corner_brackets()

        # 2. Draw Hand Reticles & Tracking Targets
        self._draw_hand_reticles(hands_dict)

        # 3. Draw Telemetry Text & Meters onto 2D Surface
        self._draw_telemetry_surface(fps, camera_status, hands_dict, orbital_system, particle_sys, origin_pos, origin_mode)

        # 4. Upload & Render HUD Texture
        self._render_hud_texture()

        # Restore Matrix Modes
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def _draw_corner_brackets(self):
        glColor4f(settings.COLOR_CYAN[0], settings.COLOR_CYAN[1], settings.COLOR_CYAN[2], 0.45)
        glLineWidth(1.5)
        
        m = 24.0
        blen = 35.0
        w, h = float(self.width), float(self.height)

        glBegin(GL_LINES)
        # Top-Left
        glVertex2f(m, m); glVertex2f(m + blen, m)
        glVertex2f(m, m); glVertex2f(m, m + blen)
        # Top-Right
        glVertex2f(w - m, m); glVertex2f(w - m - blen, m)
        glVertex2f(w - m, m); glVertex2f(w - m, m + blen)
        # Bottom-Left
        glVertex2f(m, h - m); glVertex2f(m + blen, h - m)
        glVertex2f(m, h - m); glVertex2f(m, h - m - blen)
        # Bottom-Right
        glVertex2f(w - m, h - m); glVertex2f(w - m - blen, h - m)
        glVertex2f(w - m, h - m); glVertex2f(w - m, h - m - blen)
        glEnd()

    def _draw_hand_reticles(self, hands_dict):
        glColor4f(settings.COLOR_CYAN[0], settings.COLOR_CYAN[1], settings.COLOR_CYAN[2], 0.6)
        glLineWidth(1.2)

        for label, hand in hands_dict.items():
            if not hand.is_present or hand.raw_landmarks is None:
                continue

            wrist_norm = hand.raw_landmarks.landmark[0]
            sx = wrist_norm.x * self.width
            sy = wrist_norm.y * self.height
            
            r = 28.0
            glBegin(GL_LINE_LOOP)
            for i in range(16):
                ang = 2.0 * math.pi * i / 16.0
                glVertex2f(sx + r * math.cos(ang), sy + r * math.sin(ang))
            glEnd()

            t_len = 8.0
            glBegin(GL_LINES)
            glVertex2f(sx - r - t_len, sy); glVertex2f(sx - r + 2, sy)
            glVertex2f(sx + r - 2, sy); glVertex2f(sx + r + t_len, sy)
            glVertex2f(sx, sy - r - t_len); glVertex2f(sx, sy - r + 2)
            glVertex2f(sx, sy + r - 2); glVertex2f(sx, sy + r + t_len)
            glEnd()

    def _draw_telemetry_surface(self, fps, camera_status, hands_dict, orbital_system, particle_sys, origin_pos, origin_mode):
        self.hud_surface.fill((0, 0, 0, 0))

        cyan = (0, 240, 255)
        plasma = (60, 140, 255)
        violet = (180, 80, 255)
        white = (240, 245, 255)
        dim_gray = (120, 160, 180)
        amber = (255, 170, 40)

        mode_color = cyan if orbital_system.mode == settings.MODE_ORBITAL else (
            amber if orbital_system.mode == settings.MODE_CHAOS else (255, 60, 100)
        )

        # Header Block
        title_surf = self.font_title.render("PHANTOM // SPATIAL DISTORTION ENGINE", True, cyan)
        sub_surf = self.font_main.render("BODY-RELATIVE CELESTIAL METRIC — SYS v2.5", True, dim_gray)
        self.hud_surface.blit(title_surf, (36, 32))
        self.hud_surface.blit(sub_surf, (36, 56))

        # Mode Indicator Pill
        mode_text = f"[ SIM STATE: {orbital_system.mode} ]"
        mode_surf = self.font_header.render(mode_text, True, mode_color)
        self.hud_surface.blit(mode_surf, (36, 80))

        # Primary Telemetry Metrics Block (Top-Left)
        y = 112
        grab_status = "LOCKED [PINCH FLING READY]" if orbital_system.grabbed_body else "STANDBY"
        grab_color = white if orbital_system.grabbed_body else dim_gray

        left_metrics = [
            ("OPTICAL SENSOR", f"{settings.CAMERA_WIDTH}x{settings.CAMERA_HEIGHT} ({'ONLINE' if camera_status else 'SYNTH'})"),
            ("RENDER ENGINE", f"{fps:.1f} FPS (GL DUAL-PASS)"),
            ("SPATIAL ANCHOR", f"{origin_mode}"),
            ("ORIGIN XYZ", f"[{origin_pos[0]:+.2f}, {origin_pos[1]:+.2f}, {origin_pos[2]:+.2f}]"),
            ("GRAV. LENSING", f"ACTIVE (Rs: {settings.EVENT_HORIZON_RADIUS:.2f})"),
            ("KINETIC GRAB", f"{grab_status}"),
            ("ACTIVE PARTICLES", f"{particle_sys.total_count:,} (ORB+ACC+JET)"),
            ("FIELD EXPANSION", f"{orbital_system.field_scale:.2f}x"),
        ]

        for label, val in left_metrics:
            lbl_surf = self.font_main.render(f"{label:<18} : ", True, dim_gray)
            val_surf = self.font_main.render(val, True, white if label != "KINETIC GRAB" else (cyan if orbital_system.grabbed_body else white))
            self.hud_surface.blit(lbl_surf, (36, y))
            self.hud_surface.blit(val_surf, (190, y))
            y += 19

        # Field Intensity Meter Bar
        bar_x = 36
        bar_y = y + 4
        bar_w = 200
        bar_h = 7
        pygame.draw.rect(self.hud_surface, (20, 40, 60), (bar_x, bar_y, bar_w, bar_h), 1)
        fill_w = int(bar_w * max(0.0, min(1.0, orbital_system.field_intensity)))
        pygame.draw.rect(self.hud_surface, cyan, (bar_x + 1, bar_y + 1, fill_w, bar_h - 2))

        # Hand Tracking Telemetry (Top-Right)
        right_x = self.width - 340
        y_r = 35
        head_r = self.font_header.render("// BIOMETRIC SPATIAL TELEMETRY", True, plasma)
        self.hud_surface.blit(head_r, (right_x, y_r))
        y_r += 26

        any_hand = False
        for lbl in ["Right", "Left"]:
            hand = hands_dict.get(lbl)
            if hand and hand.is_present:
                any_hand = True
                status_color = cyan if lbl == "Right" else plasma
                h_name = f"HAND: {lbl.upper()}"
                h_gest = f"GESTURE: {hand.gesture}"
                h_pos = f"XYZ: [{hand.palm_center_world[0]:+.2f}, {hand.palm_center_world[1]:+.2f}, {hand.palm_center_world[2]:+.2f}]"
                h_vel = f"VELOCITY: {hand.velocity_mag:.2f} u/s"
                h_conf = f"CONFIDENCE: {hand.confidence * 100:.1f}%"

                for text_line in [h_name, h_gest, h_pos, h_vel, h_conf]:
                    txt_surf = self.font_main.render(text_line, True, status_color if "HAND" in text_line else white)
                    self.hud_surface.blit(txt_surf, (right_x, y_r))
                    y_r += 18
                y_r += 8

        if not any_hand:
            no_hand_surf = self.font_main.render("NO HANDS DETECTED — STAND BEFORE CAMERA", True, (160, 100, 100))
            self.hud_surface.blit(no_hand_surf, (right_x, y_r))

        # Bottom Instructions & Keyboard Bindings
        bottom_y = self.height - 48
        cmd_text = "[1] ORBITAL   [2] CHAOS   [3] SINGULARITY   [H] TOGGLE HUD   [R] RESET   [F] FULLSCREEN   [ESC] EXIT"
        cmd_surf = self.font_main.render(cmd_text, True, dim_gray)
        self.hud_surface.blit(cmd_surf, (36, bottom_y))

    def _render_hud_texture(self):
        """Blits the 2D surface to the screen via an OpenGL texture quad."""
        tex_data = pygame.image.tostring(self.hud_surface, "RGBA", True)
        
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.tex_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex_data)

        glColor4f(1.0, 1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0); glVertex2f(0.0, float(self.height))
        glTexCoord2f(1.0, 0.0); glVertex2f(float(self.width), float(self.height))
        glTexCoord2f(1.0, 1.0); glVertex2f(float(self.width), 0.0)
        glTexCoord2f(0.0, 1.0); glVertex2f(0.0, 0.0)
        glEnd()

        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)

