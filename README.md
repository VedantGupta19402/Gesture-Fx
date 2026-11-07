# PHANTOM — ORBITAL MODE 🌌🖐️
### Autonomous Spatial Holographic Computing System & Scientific Telemetry Interface

[![Python 3.10](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![OpenGL](https://img.shields.io/badge/Graphics-PyOpenGL-cyan.svg)](https://pyopengl.sourceforge.net/)
[![MediaPipe](https://img.shields.io/badge/Tracking-MediaPipe-green.svg)](https://developers.google.com/mediapipe)

**PHANTOM: ORBITAL MODE** transforms standard optical video capture into an interactive 3D holographic research environment. Powered by real-time computer vision and dual-pass OpenGL rendering, the system spawns tiered celestial orbits, responsive particle physics, and energy shockwaves calibrated to natural human hand dynamics.

---

## 🔬 System Capabilities & Visual Architecture

### 1. Three-Tiered Orbital Mechanics
* **Inner Orbit**: Agile, high-velocity geometric cores (octahedrons, tetrahedrons, cubes) closely tethered to the interaction focus.
* **Middle Orbit**: Independent multi-axis rotating structures (nested icosahedrons, parametric wireframe cubes, torus rings).
* **Outer Orbit**: Large celestial rings, orbital track markers, and resonant brackets with organic eccentricity and inclination tilt.

### 2. High-Performance Vectorized Particle Physics
* Over **1,600+ active particles** simulated via SIMD NumPy array buffers without per-frame Python memory allocation.
* Supports **gravitational attraction**, **shockwave repulsion**, **turbulent curl noise**, **disintegration**, and **structural reformation**.

### 3. Energy Shockwave Engine
* Rapid gestures or manual triggers generate expanding 3D spherical wavefronts that push particles and radiate outward.
* Central pulsating multi-layered energy core that dynamically breathes and flares based on field intensity.

### 4. Scientific Telemetry HUD
* High-precision aerospace overlay featuring real-time FPS, optical sensor resolution, active hand joint tracking, confidence scores, field intensity bar meter, and 3D coordinate readouts $(X, Y, Z)$.
* Can be toggled on/off instantly with `[H]`.

---

## 🖐️ Gesture Control Mapping

| Physical Gesture | Target Interaction | Visual Behavior |
|:---|:---|:---|
| **Open Palm** | Activate Orbital Field | Orbits accelerate, field intensity increases, core glows |
| **Closed Fist** | Gravitational Singularity | Nearby bodies & particles collapse into the fist |
| **Pinch (Thumb + Index)** | Grab & Manipulate | Locks and drags the nearest orbital body or focal node |
| **Two Fingers Extended** | Camera Orbital Rotation | Rotates the 3D perspective along pitch and yaw |
| **Spread Dual Hands** | Field Expansion | Increases orbital semi-major axes and layer separation |
| **Bring Hands Together**| Field Compression | Tightens orbital radius into a dense formation |
| **Fast Hand Swipe** | Energy Shockwave | Emits a high-velocity 3D expanding wave-front |

---

## Tech Stack

| Layer | Technology |
| --- | --- |
| Computer vision | OpenCV, MediaPipe |
| 3D rendering | PyOpenGL, GLU |
| Windowing / input | Pygame |
| Math / vectors | NumPy |

---

## Project Structure

```
hand gestures/
├── main.py                  # PHANTOM entry point
├── requirements.txt
├── config/
│   └── settings.py          # Global configuration & design system
├── core/
│   ├── application.py       # Application lifecycle controller
│   └── camera.py            # Webcam capture wrapper
├── tracking/
│   ├── hand_tracker.py      # Landmark tracking & smoothing
│   └── gesture_recognizer.py# Gesture classification engine
├── simulation/
│   ├── orbital_system.py    # Orbital mechanics
│   ├── particle_system.py   # Vectorized particle physics
│   └── energy_effects.py    # Shockwaves & core effects
├── rendering/
│   ├── geometry.py          # Primitive builders
│   ├── materials.py         # Neon / glow materials
│   └── renderer.py          # Master renderer
├── interface/
│   └── telemetry_hud.py     # Heads-up display
└── The-Sci-Fi/
    ├── mini.py              # Original prototype
    └── mini.ipynb           # Notebook version
```

---

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> A working webcam is required. On Windows, allow camera access for the terminal/app running Python.

---

## Running

### PHANTOM // Orbital Mode

```bash
python main.py
```

### Original prototype

```bash
python The-Sci-Fi/mini.py
```

---

## Controls

### PHANTOM

| Key | Action |
| --- | --- |
| `1` | Orbital mode |
| `2` | Chaos mode |
| `3` | Singularity mode |
| `H` | Toggle HUD |
| `R` | Reset simulation |
| `F` | Toggle fullscreen |
| `Space` | Manual shockwave |
| `Esc` | Exit |

### Gestures

| Hand | Gesture | Action |
| --- | --- | --- |
| Right | Pinch (thumb + index) | Scale / zoom the particle field |
| Left | Two fingers up | Enable camera rotation |
| Left | Move wrist / palm | Rotate the 3D scene |
| Any | Fast swipe | Emit an energy shockwave |

### The-Sci-Fi prototype

| Hand | Action |
| --- | --- |
| Right | Pinch to scale the particle cube |
| Left | Two fingers up + move to rotate |
| Any | Fast motion for shockwave / glow |

---

## Notes

- The application is designed for a dark environment; strong backlighting reduces landmark confidence.
- Keep your hand inside the camera frame, roughly 40–80 cm away.
- If the camera fails to open, change `CAMERA_INDEX` in `config/settings.py`.

---

## License

Educational / experimental project. See the repository for details.

## Credits

- Original prototype: [The-Sci-Fi](https://github.com/Mrez2/The-Sci-Fi)
- Extended PHANTOM implementation: Vedant Gupta
