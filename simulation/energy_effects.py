"""
PHANTOM: ORBITAL MODE — Energy Shockwaves & Advanced Core Dynamics
Controls multi-shell pulsation, accretion precession, and counter-rotating gimbals.
"""

import math
import numpy as np
from config import settings

class Shockwave:
    def __init__(self, origin, normal=(0, 0, 1), max_radius=8.5, speed=7.5, color=settings.COLOR_CYAN):
        self.origin = np.array(origin, dtype=np.float32)
        self.normal = np.array(normal, dtype=np.float32)
        norm = np.linalg.norm(self.normal)
        if norm > 0.001:
            self.normal /= norm
        else:
            self.normal = np.array([0.0, 0.0, 1.0], dtype=np.float32)
            
        self.radius = 0.2
        self.max_radius = max_radius
        self.speed = speed
        self.lifetime = 0.0
        self.max_lifetime = max_radius / speed
        self.color = list(color)
        self.is_alive = True
        self.thickness = 0.25

    def update(self, dt):
        self.lifetime += dt
        self.radius += self.speed * dt
        if self.radius >= self.max_radius or self.lifetime >= self.max_lifetime:
            self.is_alive = False

    @property
    def alpha(self):
        progress = self.lifetime / max(0.001, self.max_lifetime)
        return max(0.0, (1.0 - progress) ** 1.8)


class EnergyEffectsManager:
    def __init__(self):
        self.shockwaves = []
        self.last_shockwave_time = 0.0
        
        # Core Kinematic Rotations
        self.core_rot_ico_1 = 0.0
        self.core_rot_ico_2 = 0.0
        self.gimbal_torus_1 = 0.0
        self.gimbal_torus_2 = 0.0
        
        # Pulsating Waves & Accretion Timing
        self.pulse_phase = 0.0
        self.shell_phases = [0.0, 1.2, 2.4]
        self.accretion_time = 0.0

    def trigger_shockwave(self, origin, normal=(0, 0, 1), color=settings.COLOR_CYAN):
        self.shockwaves.append(Shockwave(origin=origin, normal=normal, color=color))

    def update(self, dt, core_pos, hand_velocity, is_fast_swipe, field_intensity=0.5):
        speed_factor = 1.0 + field_intensity * 1.5
        self.pulse_phase += dt * (3.0 * speed_factor)
        self.accretion_time += dt

        # Update counter-rotating icosahedrons
        self.core_rot_ico_1 = (self.core_rot_ico_1 + dt * 42.0 * speed_factor) % 360.0
        self.core_rot_ico_2 = (self.core_rot_ico_2 - dt * 68.0 * speed_factor) % 360.0

        # Update orthogonal gimbal torus rings
        self.gimbal_torus_1 = (self.gimbal_torus_1 + dt * 30.0 * speed_factor) % 360.0
        self.gimbal_torus_2 = (self.gimbal_torus_2 - dt * 48.0 * speed_factor) % 360.0

        # Update pulsating energy shells
        for i in range(len(self.shell_phases)):
            self.shell_phases[i] = (self.shell_phases[i] + dt * 1.8 * speed_factor) % (math.pi * 2.0)

        # Trigger shockwave on sudden high velocity gesture
        if is_fast_swipe and (len(self.shockwaves) == 0 or self.shockwaves[-1].radius > 1.8):
            v_dir = hand_velocity.copy()
            v_norm = np.linalg.norm(v_dir)
            if v_norm > 0.001:
                v_dir /= v_norm
            else:
                v_dir = np.array([0.0, 0.0, 1.0], dtype=np.float32)
            self.trigger_shockwave(origin=core_pos, normal=v_dir, color=settings.COLOR_WHITE)

        # Update active shockwaves
        for sw in self.shockwaves:
            sw.update(dt)
        self.shockwaves = [sw for sw in self.shockwaves if sw.is_alive]
