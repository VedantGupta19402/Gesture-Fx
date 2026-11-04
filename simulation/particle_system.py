"""
PHANTOM: ORBITAL MODE — Vectorized High-Performance Particle Engine
Executes SIMD-accelerated particle dynamics (attraction, shockwave repulsion,
turbulent curl drift, disintegration, reformation) via NumPy.
"""

import math
import numpy as np
from config import settings

class ParticleSystem:
    def __init__(self, max_particles=settings.MAX_PARTICLES):
        self.count = max_particles
        
        # Pre-allocated Vector Buffers (Avoid garbage collection in render loop)
        self.positions = np.zeros((self.count, 3), dtype=np.float32)
        self.velocities = np.zeros((self.count, 3), dtype=np.float32)
        self.colors = np.zeros((self.count, 4), dtype=np.float32)
        
        # Orbital Reference Data for Reformation
        self.orbit_radii = np.random.uniform(1.0, 7.5, size=self.count).astype(np.float32)
        self.orbit_speeds = np.random.uniform(0.3, 2.2, size=self.count).astype(np.float32) * np.random.choice([-1.0, 1.0], size=self.count).astype(np.float32)
        self.orbit_angles = np.random.uniform(0.0, 2.0 * math.pi, size=self.count).astype(np.float32)
        self.orbit_tilt_x = np.random.uniform(-0.6, 0.6, size=self.count).astype(np.float32)
        self.orbit_tilt_z = np.random.uniform(-0.6, 0.6, size=self.count).astype(np.float32)
        self.orbit_wobble_freq = np.random.uniform(0.8, 3.2, size=self.count).astype(np.float32)
        
        # Lifetimes & Alphas
        self.lifetimes = np.random.uniform(1.0, 5.0, size=self.count).astype(np.float32)
        self.max_lifetimes = self.lifetimes.copy()

        # Initialize Colors (Art Direction: Electric Cyan, Plasma Blue, Ultraviolet highlights)
        for i in range(self.count):
            r_val = np.random.rand()
            if r_val < 0.50:
                # Electric Cyan
                self.colors[i] = [0.0, 0.94, 1.0, np.random.uniform(0.4, 0.85)]
            elif r_val < 0.85:
                # Plasma Blue
                self.colors[i] = [0.15, 0.45, 1.0, np.random.uniform(0.3, 0.75)]
            else:
                # Ultraviolet / White
                self.colors[i] = [0.72, 0.22, 1.0, np.random.uniform(0.5, 0.95)]

        self.time = 0.0
        self._init_initial_positions()

    def _init_initial_positions(self):
        cos_t = np.cos(self.orbit_angles)
        sin_t = np.sin(self.orbit_angles)
        self.positions[:, 0] = self.orbit_radii * cos_t
        self.positions[:, 1] = np.sin(self.orbit_angles * 2.0) * 0.4
        self.positions[:, 2] = -8.0 + self.orbit_radii * sin_t

    def update(self, dt, center_pos, hand_pos=None, gesture=settings.GESTURE_NONE,
               shockwaves=None, mode=settings.MODE_ORBITAL, field_scale=1.0):
        self.time += dt
        
        # 1. Update Base Orbital Angles
        speed_multiplier = 1.0
        if mode == settings.MODE_CHAOS:
            speed_multiplier = 3.0
        elif mode == settings.MODE_SINGULARITY:
            speed_multiplier = 4.5

        self.orbit_angles = (self.orbit_angles + self.orbit_speeds * speed_multiplier * dt) % (2.0 * math.pi)

        # 2. Compute Target Ideal Orbital Positions for all particles
        radii = self.orbit_radii * field_scale
        if mode == settings.MODE_SINGULARITY:
            # Collapse inward into hyper-dense core
            radii = radii * 0.18 + np.sin(self.time * 6.0 + self.orbit_angles) * 0.15

        x_plane = radii * np.cos(self.orbit_angles)
        y_plane = np.sin(self.orbit_angles * self.orbit_wobble_freq + self.time) * 0.35
        z_plane = radii * np.sin(self.orbit_angles)

        # Apply inclinations
        cos_x = np.cos(self.orbit_tilt_x)
        sin_x = np.sin(self.orbit_tilt_x)
        y1 = y_plane * cos_x - z_plane * sin_x
        z1 = y_plane * sin_x + z_plane * cos_x

        cos_z = np.cos(self.orbit_tilt_z)
        sin_z = np.sin(self.orbit_tilt_z)
        target_x = center_pos[0] + (x_plane * cos_z - y1 * sin_z)
        target_y = center_pos[1] + (x_plane * sin_z + y1 * cos_z)
        target_z = center_pos[2] + z1

        targets = np.stack([target_x, target_y, target_z], axis=1)

        # 3. Mode Physics Dynamics
        if mode == settings.MODE_ORBITAL:
            # Particles smoothly converge towards their orbital equilibrium
            to_target = targets - self.positions
            self.velocities += to_target * (dt * 4.2)
            self.velocities *= 0.88  # High damping for elegant orbital stability
            self.positions += self.velocities * dt

        elif mode == settings.MODE_CHAOS:
            # Disintegration: High turbulent curl noise and centrifugal expansion
            noise_x = np.sin(self.positions[:, 1] * 1.5 + self.time * 2.0)
            noise_y = np.cos(self.positions[:, 2] * 1.5 + self.time * 2.0)
            noise_z = np.sin(self.positions[:, 0] * 1.5 + self.time * 2.0)
            curl_noise = np.stack([noise_x, noise_y, noise_z], axis=1) * 3.5
            
            # Repel from center outwards
            diff_from_center = self.positions - center_pos
            dist_c = np.linalg.norm(diff_from_center, axis=1, keepdims=True) + 0.1
            outward_force = (diff_from_center / dist_c) * 4.0

            self.velocities += (curl_noise + outward_force) * dt
            self.velocities *= 0.94
            self.positions += self.velocities * dt

        elif mode == settings.MODE_SINGULARITY:
            # Gravitational vortex towards interaction center
            diff_from_focal = center_pos - self.positions
            dist_f = np.linalg.norm(diff_from_focal, axis=1, keepdims=True) + 0.05
            vortex_tangent = np.cross(diff_from_focal, np.array([0, 1, 0]))
            
            grav_force = (diff_from_focal / dist_f) * (18.0 / np.clip(dist_f, 0.4, 10.0))
            self.velocities += (grav_force + vortex_tangent * 2.5) * dt
            self.velocities *= 0.85
            self.positions += self.velocities * dt

        # 4. Hand Proximity & Gestural Forces
        if hand_pos is not None:
            disp_hand = self.positions - hand_pos
            dist_hand = np.linalg.norm(disp_hand, axis=1, keepdims=True) + 0.01

            # Closed Fist: Gravitational black hole suction towards fist
            if gesture == settings.GESTURE_CLOSED_FIST:
                fist_pull = (-disp_hand / dist_hand) * (12.0 / np.clip(dist_hand, 0.2, 8.0))
                self.velocities += fist_pull * dt

            # Pinch: Compress particles into a tight quantum singularity at fingers
            elif gesture == settings.GESTURE_PINCH:
                pinch_pull = (-disp_hand / dist_hand) * (16.0 / np.clip(dist_hand, 0.1, 5.0))
                self.velocities += pinch_pull * dt

            # Open Palm: Gentle interactive repulsion field
            elif gesture == settings.GESTURE_OPEN_PALM:
                mask = (dist_hand < 2.5).flatten()
                if np.any(mask):
                    repel = (disp_hand[mask] / dist_hand[mask]) * (4.5 / dist_hand[mask])
                    self.velocities[mask] += repel * dt

        # 5. Energy Shockwave Repulsion Waves
        if shockwaves:
            for sw in shockwaves:
                disp_sw = self.positions - sw.origin
                dist_sw = np.linalg.norm(disp_sw, axis=1, keepdims=True) + 0.001
                # Find particles near the expanding shockwave front
                wave_dist = np.abs(dist_sw.flatten() - sw.radius)
                wave_mask = wave_dist < 0.65
                if np.any(wave_mask):
                    push_dir = disp_sw[wave_mask] / dist_sw[wave_mask]
                    impulse = push_dir * (sw.alpha * 14.0)
                    self.velocities[wave_mask] += impulse * dt

        # Limit maximum particle velocity to prevent teleportation
        speed = np.linalg.norm(self.velocities, axis=1, keepdims=True)
        max_speed = 15.0
        overspeed = speed > max_speed
        if np.any(overspeed):
            self.velocities = np.where(overspeed, (self.velocities / speed) * max_speed, self.velocities)

