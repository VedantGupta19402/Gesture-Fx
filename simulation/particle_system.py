"""
PHANTOM: ORBITAL MODE — Vectorized High-Performance Particle Engine
Executes SIMD-accelerated particle dynamics, gravitational lensing,
relativistic accretion disk kinematics, polar jets, and dual-hand spatial warps.
"""

import math
import numpy as np
from config import settings

class ParticleSystem:
    def __init__(self, max_particles=settings.MAX_PARTICLES):
        self.total_count = max_particles
        self.accretion_count = settings.ACCRETION_PARTICLE_COUNT
        self.jet_count = settings.JET_PARTICLE_COUNT
        self.orbital_count = self.total_count - (self.accretion_count + self.jet_count)

        # Pre-allocated Unified Buffers (Avoid GC allocations in render loop)
        self.positions = np.zeros((self.total_count, 3), dtype=np.float32)
        self.velocities = np.zeros((self.total_count, 3), dtype=np.float32)
        self.colors = np.zeros((self.total_count, 4), dtype=np.float32)
        
        # Partition 1: Orbital Cloud Data
        self.orb_radii = np.random.uniform(1.2, 7.8, size=self.orbital_count).astype(np.float32)
        self.orb_speeds = np.random.uniform(0.3, 2.2, size=self.orbital_count).astype(np.float32) * np.random.choice([-1.0, 1.0], size=self.orbital_count).astype(np.float32)
        self.orb_angles = np.random.uniform(0.0, 2.0 * math.pi, size=self.orbital_count).astype(np.float32)
        self.orb_tilt_x = np.random.uniform(-0.6, 0.6, size=self.orbital_count).astype(np.float32)
        self.orb_tilt_z = np.random.uniform(-0.6, 0.6, size=self.orbital_count).astype(np.float32)
        self.orb_wobble_freq = np.random.uniform(0.8, 3.2, size=self.orbital_count).astype(np.float32)

        # Partition 2: Relativistic Accretion Disk Data
        self.acc_radii = np.random.uniform(settings.ACCRETION_DISK_INNER, settings.ACCRETION_DISK_OUTER, size=self.accretion_count).astype(np.float32)
        self.acc_angles = np.random.uniform(0.0, 2.0 * math.pi, size=self.accretion_count).astype(np.float32)
        # Keplerian differential speeds: v ~ r^(-1.5)
        self.acc_speeds = (1.8 / np.power(self.acc_radii / settings.ACCRETION_DISK_INNER, 1.5)).astype(np.float32)

        # Partition 3: Polar Astrophysical Jet Data
        self.jet_dist = np.random.uniform(0.2, 4.5, size=self.jet_count).astype(np.float32)
        self.jet_polar_dir = np.random.choice([-1.0, 1.0], size=self.jet_count).astype(np.float32) # North vs South
        self.jet_angles = np.random.uniform(0.0, 2.0 * math.pi, size=self.jet_count).astype(np.float32)
        self.jet_speeds = np.random.uniform(3.5, 7.0, size=self.jet_count).astype(np.float32)

        self.time = 0.0
        self._init_particle_colors()
        self._init_initial_positions()

    def _init_particle_colors(self):
        # 1. Orbital Cloud Colors: Cyan / Plasma / Violet
        for i in range(self.orbital_count):
            r = np.random.rand()
            if r < 0.50:
                self.colors[i] = [0.0, 0.94, 1.0, np.random.uniform(0.35, 0.85)]
            elif r < 0.82:
                self.colors[i] = [0.12, 0.45, 1.0, np.random.uniform(0.30, 0.75)]
            else:
                self.colors[i] = [0.68, 0.18, 0.98, np.random.uniform(0.40, 0.90)]

        # 2. Accretion Disk Colors: Doppler beaming initialized
        acc_start = self.orbital_count
        acc_end = acc_start + self.accretion_count
        for i in range(acc_start, acc_end):
            self.colors[i] = [0.4, 0.85, 1.0, 0.80]

        # 3. Polar Jets: Supercharged White-Cyan
        jet_start = acc_end
        for i in range(jet_start, self.total_count):
            self.colors[i] = [0.94, 0.98, 1.0, np.random.uniform(0.65, 0.95)]

    def _init_initial_positions(self):
        c_pos = np.array(settings.RESTING_ORIGIN, dtype=np.float32)
        
        # Orbital
        cos_t = np.cos(self.orb_angles)
        sin_t = np.sin(self.orb_angles)
        self.positions[:self.orbital_count, 0] = c_pos[0] + self.orb_radii * cos_t
        self.positions[:self.orbital_count, 1] = c_pos[1] + np.sin(self.orb_angles * 2.0) * 0.4
        self.positions[:self.orbital_count, 2] = c_pos[2] + self.orb_radii * sin_t

        # Accretion
        a_start = self.orbital_count
        a_end = a_start + self.accretion_count
        self.positions[a_start:a_end, 0] = c_pos[0] + self.acc_radii * np.cos(self.acc_angles)
        self.positions[a_start:a_end, 1] = c_pos[1] + np.sin(self.acc_angles) * 0.12
        self.positions[a_start:a_end, 2] = c_pos[2] + self.acc_radii * np.sin(self.acc_angles)

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

