"""
PHANTOM: ORBITAL MODE — 3D Celestial Orbital Physics & Spatial Distortion Engine
Simulates tiered orbital bodies with independent inclination, eccentricity,
spin kinematics, gravitational curving, and pinch-and-release mechanics.
"""

import math
import random
import numpy as np
from config import settings

class OrbitalBody:
    def __init__(self, layer_name, geom_type, radius, speed, scale, inclination=(0.0, 0.0), color=settings.COLOR_CYAN):
        self.layer = layer_name
        self.geom_type = geom_type
        self.base_radius = radius
        self.current_radius = radius
        self.eccentricity = random.uniform(0.04, 0.18)
        self.orbital_speed = speed * random.choice([1, -1])
        self.base_scale = scale
        self.scale = scale
        self.inclination_x = inclination[0]  # Pitch tilt in radians
        self.inclination_z = inclination[1]  # Roll tilt in radians
        self.base_color = list(color)
        self.color = list(color)
        
        # Phase and Rotational Dynamics
        self.theta = random.uniform(0.0, 2.0 * math.pi)
        self.rot_angles = [random.uniform(0, 360), random.uniform(0, 360), random.uniform(0, 360)]
        self.rot_speeds = [
            random.uniform(30.0, 110.0) * random.choice([1, -1]),
            random.uniform(30.0, 110.0) * random.choice([1, -1]),
            random.uniform(20.0, 70.0) * random.choice([1, -1])
        ]
        
        # World Spatial Coordinates & Trails
        self.world_pos = np.zeros(3, dtype=np.float32)
        self.trail = []
        self.max_trail_len = 22 if layer_name == "INNER" else (28 if layer_name == "MIDDLE" else 36)
        
        # Pinch, Grab & Launch Kinetics
        self.is_grabbed = False
        self.grabbed_hand_label = None
        self.charge_level = 0.0
        self.linear_velocity = np.zeros(3, dtype=np.float32)
        self.is_flung = False
        self.fling_damping = 0.98

        # Disintegration & Organic perturbation state
        self.disintegration_offset = np.zeros(3, dtype=np.float32)
        self.disintegration_target = np.zeros(3, dtype=np.float32)
        self.wobble_seed = random.uniform(0.0, 100.0)

    def launch(self, release_velocity, center_pos):
        """
        Fling object along release vector and re-parameterize Keplerian orbit.
        """
        self.is_grabbed = False
        self.is_flung = True
        self.linear_velocity = release_velocity.copy() * settings.LAUNCH_SPEED_MULT
        
        # Compute new orbital distance & inclination from release point
        rel_pos = self.world_pos - center_pos
        new_radius = float(np.linalg.norm(rel_pos))
        self.base_radius = max(1.2, min(8.0, new_radius))
        self.current_radius = self.base_radius

        # Set phase angle
        self.theta = math.atan2(rel_pos[2], rel_pos[0])
        
        # Increase orbital speed based on fling kinetic energy
        fling_speed = float(np.linalg.norm(self.linear_velocity))
        if fling_speed > 0.8:
            self.orbital_speed = math.copysign(min(3.5, 1.2 + fling_speed * 0.4), self.orbital_speed)
            self.eccentricity = min(0.65, 0.15 + fling_speed * 0.12)

    def update(self, dt, center_pos, field_scale=1.0, mode=settings.MODE_ORBITAL,
               warp_fields=None, hand_gesture=settings.GESTURE_NONE):
        # 1. Update Self Rotation
        for i in range(3):
            self.rot_angles[i] = (self.rot_angles[i] + self.rot_speeds[i] * dt) % 360.0

        if self.is_grabbed:
            # Supercharged state while locked in user's fingers
            self.charge_level = min(1.0, self.charge_level + dt * 2.8)
            pulse = 1.0 + 0.3 * math.sin(self.charge_level * 18.0)
            self.scale = self.base_scale * (1.0 + 0.45 * self.charge_level) * pulse
            self.color = [0.92, 0.98, 1.0, 1.0] # Luminous energetic white
            self.trail.append(self.world_pos.copy())
            if len(self.trail) > self.max_trail_len:
                self.trail.pop(0)
            return

        # Decay charge when released
        if self.charge_level > 0.0:
            self.charge_level = max(0.0, self.charge_level - dt * 1.5)
            # Interpolate back to base color
            c_blend = self.charge_level
            self.color = [
                self.base_color[0] * (1.0 - c_blend) + 0.95 * c_blend,
                self.base_color[1] * (1.0 - c_blend) + 0.98 * c_blend,
                self.base_color[2] * (1.0 - c_blend) + 1.0 * c_blend,
                self.base_color[3]
            ]
            self.scale = self.base_scale * (1.0 + 0.3 * self.charge_level)
        else:
            self.color = list(self.base_color)
            self.scale = self.base_scale

        # 2. Orbital Phase & Speed Dynamics
        speed_mult = 1.0
        if mode == settings.MODE_CHAOS:
            speed_mult = 2.4
        elif mode == settings.MODE_SINGULARITY:
            speed_mult = 3.6

        self.theta = (self.theta + self.orbital_speed * speed_mult * dt) % (2.0 * math.pi)

        # 3. Dynamic Radius with Eccentricity & Gestural Scaling
        ecc = self.eccentricity
        if mode == settings.MODE_CHAOS:
            ecc = min(0.65, ecc * 2.5)

        r = (self.base_radius * field_scale) * (1.0 - ecc * ecc) / (1.0 + ecc * math.cos(self.theta))
        
        if mode == settings.MODE_SINGULARITY:
            # Gravitational collapse towards central focal point
            r = max(0.4, r * 0.28)

        # 4. Compute 3D Coordinates via Inclined Orbital Planes
        self.wobble_seed += dt * 0.8
        wobble_y = math.sin(self.wobble_seed + self.theta) * 0.12

        # Orbital plane coordinates before inclination
        x_plane = r * math.cos(self.theta)
        y_plane = wobble_y
        z_plane = r * math.sin(self.theta)

        # Apply pitch rotation (inclination_x around X axis)
        cos_ix, sin_ix = math.cos(self.inclination_x), math.sin(self.inclination_x)
        y_rot1 = y_plane * cos_ix - z_plane * sin_ix
        z_rot1 = y_plane * sin_ix + z_plane * cos_ix

        # Apply roll rotation (inclination_z around Z axis)
        cos_iz, sin_iz = math.cos(self.inclination_z), math.sin(self.inclination_z)
        x_rot2 = x_plane * cos_iz - y_rot1 * sin_iz
        y_rot2 = x_plane * sin_iz + y_rot1 * cos_iz
        z_rot2 = z_rot1

        raw_pos = center_pos + np.array([x_rot2, y_rot2, z_rot2], dtype=np.float32)

        # 5. Handle Gestural Perturbation & Interaction
        if hand_interact_pos is not None:
            dist_to_hand = np.linalg.norm(raw_pos - hand_interact_pos)

            # Fist Gesture: Gravitational suction
            if hand_gesture == settings.GESTURE_CLOSED_FIST:
                pull_vector = (hand_interact_pos - raw_pos)
                if dist_to_hand > 0.3:
                    pull_factor = min(1.0, 1.8 / (dist_to_hand + 0.1))
                    raw_pos += pull_vector * pull_factor * 0.45

            # Pinch Gesture: Grab nearest body
            elif hand_gesture == settings.GESTURE_PINCH:
                if dist_to_hand < 1.4 or self.grabbed:
                    self.grabbed = True
                    raw_pos = hand_interact_pos.copy()
            else:
                self.grabbed = False

        # 6. Disintegration / Reformation Kinematics
        if mode == settings.MODE_CHAOS:
            # Structures break apart into chaotic orbits
            if np.linalg.norm(self.disintegration_target) < 0.1:
                self.disintegration_target = np.random.uniform(-1.8, 1.8, size=3).astype(np.float32)
            self.disintegration_offset += (self.disintegration_target - self.disintegration_offset) * (dt * 2.0)
        else:
            # Smoothly reform back to pristine geometric equilibrium
            self.disintegration_offset *= max(0.0, 1.0 - dt * 3.5)
            self.disintegration_target *= 0.0

        self.world_pos = raw_pos + self.disintegration_offset

        # 7. Update Persistent Motion Trail
        self.trail.append(self.world_pos.copy())
        if len(self.trail) > self.max_trail_len:
            self.trail.pop(0)


class OrbitalSystem:
    def __init__(self):
        self.bodies = []
        self.field_scale = 1.0
        self.target_field_scale = 1.0
        self.center_focal_pos = np.array([0.0, 0.0, -8.0], dtype=np.float32)
        self.smoothed_center = np.array([0.0, 0.0, -8.0], dtype=np.float32)
        self.mode = settings.MODE_ORBITAL
        self.field_intensity = 0.65
        self.core_pulse_time = 0.0
        self._build_orbital_layers()

    def _build_orbital_layers(self):
        self.bodies.clear()
        
        # --- INNER LAYER: Fast, concentrated, agile geometric cores ---
        inner_cfg = settings.INNER_LAYER
        for i in range(inner_cfg["count"]):
            radius = inner_cfg["radius_min"] + (inner_cfg["radius_max"] - inner_cfg["radius_min"]) * (i / max(1, inner_cfg["count"] - 1))
            speed = random.uniform(inner_cfg["speed_min"], inner_cfg["speed_max"])
            scale = random.uniform(inner_cfg["scale_range"][0], inner_cfg["scale_range"][1])
            inc = (random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4))
            geom = inner_cfg["types"][i % len(inner_cfg["types"])]
            color = settings.COLOR_CYAN
            self.bodies.append(OrbitalBody("INNER", geom, radius, speed, scale, inc, color))

        # --- MIDDLE LAYER: Diverse scientific structures & rotating prisms ---
        mid_cfg = settings.MIDDLE_LAYER
        for i in range(mid_cfg["count"]):
            radius = mid_cfg["radius_min"] + (mid_cfg["radius_max"] - mid_cfg["radius_min"]) * (i / max(1, mid_cfg["count"] - 1))
            speed = random.uniform(mid_cfg["speed_min"], mid_cfg["speed_max"])
            scale = random.uniform(mid_cfg["scale_range"][0], mid_cfg["scale_range"][1])
            inc = (random.uniform(-0.65, 0.65), random.uniform(-0.65, 0.65))
            geom = mid_cfg["types"][i % len(mid_cfg["types"])]
            color = settings.COLOR_PLASMA
            self.bodies.append(OrbitalBody("MIDDLE", geom, radius, speed, scale, inc, color))

        # --- OUTER LAYER: Broad orbital rings, wireframe cages & brackets ---
        outer_cfg = settings.OUTER_LAYER
        for i in range(outer_cfg["count"]):
            radius = outer_cfg["radius_min"] + (outer_cfg["radius_max"] - outer_cfg["radius_min"]) * (i / max(1, outer_cfg["count"] - 1))
            speed = random.uniform(outer_cfg["speed_min"], outer_cfg["speed_max"])
            scale = random.uniform(outer_cfg["scale_range"][0], outer_cfg["scale_range"][1])
            inc = (random.uniform(-0.25, 0.25), random.uniform(-0.25, 0.25))
            geom = outer_cfg["types"][i % len(outer_cfg["types"])]
            color = settings.COLOR_VIOLET
            self.bodies.append(OrbitalBody("OUTER", geom, radius, speed, scale, inc, color))

    def set_mode(self, new_mode):
        if new_mode in [settings.MODE_ORBITAL, settings.MODE_CHAOS, settings.MODE_SINGULARITY]:
            self.mode = new_mode

    def update(self, dt, primary_hand_pos=None, gesture=settings.GESTURE_NONE, dual_gesture=settings.GESTURE_NONE):
        self.core_pulse_time += dt * settings.CORE_PULSE_SPEED

        # 1. Update Central Anchor Point
        if primary_hand_pos is not None:
            self.target_field_scale = 1.0
            # Lerp center towards hand for fluid motion
            self.smoothed_center += (primary_hand_pos - self.smoothed_center) * (dt * 4.5)
        else:
            default_center = np.array([0.0, 0.0, -8.0], dtype=np.float32)
            self.smoothed_center += (default_center - self.smoothed_center) * (dt * 2.0)

        # 2. Dual-Hand Expansion / Compression Handling
        if dual_gesture == settings.GESTURE_SPREAD:
            self.target_field_scale = min(1.85, self.target_field_scale + dt * 0.9)
        elif dual_gesture == settings.GESTURE_COMPRESS:
            self.target_field_scale = max(0.45, self.target_field_scale - dt * 0.9)

        # 3. Open Palm Field Activation: Increases speed and field intensity
        if gesture == settings.GESTURE_OPEN_PALM:
            self.field_intensity = min(1.0, self.field_intensity + dt * 1.5)
            self.target_field_scale = min(1.35, self.target_field_scale + dt * 0.3)
        else:
            self.field_intensity = max(0.4, self.field_intensity - dt * 0.6)

        # Smooth field scale
        self.field_scale += (self.target_field_scale - self.field_scale) * (dt * 3.0)

        # 4. Update Each Orbital Body
        for body in self.bodies:
            body.update(
                dt=dt,
                center_pos=self.smoothed_center,
                field_scale=self.field_scale,
                mode=self.mode,
                hand_interact_pos=primary_hand_pos,
                hand_gesture=gesture
            )

