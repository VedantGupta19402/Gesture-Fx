# PHANTOM — ORBITAL MODE 🌌🖐️
### Autonomous Spatial Holographic Computing System & Scientific Telemetry Interface

[![Python 3.10](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![OpenGL](https://img.shields.io/badge/Graphics-PyOpenGL-cyan.svg)](https://pyopengl.sourceforge.net/)
[![MediaPipe](https://img.shields.io/badge/Tracking-MediaPipe-green.svg)](https://developers.google.com/mediapipe)

**PHANTOM: ORBITAL MODE** transforms standard optical video capture into an interactive 3D holographic research environment. Powered by real-time computer vision and dual-pass OpenGL rendering, the system spawns tiered celestial orbits, responsive particle physics, and energy shockwaves calibrated to natural human hand dynamics.

- **PHANTOM // ORBITAL MODE** — the full modular application (`main.py`) with orbital mechanics, particle physics, energy shockwaves, and a telemetry HUD.
- **The-Sci-Fi** — the original single-file prototype (`The-Sci-Fi/mini.py`) that started it all.

---

## Features

- **Hand tracking** via MediaPipe — up to two hands, 21 landmarks per hand.
- **Gesture recognition** with temporal hysteresis:
  - Pinch (thumb + index) to scale / manipulate the field
  - Two-finger gesture to lock and rotate the camera
  - Closed fist, open palm, spread / compress
  - Fast swipe to emit an energy shockwave
- **Three simulation modes** — Orbital, Chaos, and Singularity.
- **GPU-friendly rendering** — additive blending, glow materials, and vectorized particle updates.
- **Motion smoothing** — exponential moving average on landmarks plus lerp-based interpolation.
- **Scientific telemetry HUD** — FPS, camera status, hand state, and simulation diagnostics.

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
