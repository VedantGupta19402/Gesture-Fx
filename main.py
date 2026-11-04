#!/usr/bin/env python3
"""
====================================================================
PHANTOM // ORBITAL MODE
Autonomous Spatial Holographic Computing System
====================================================================
Art Direction: DARK SCIENTIFIC FUTURISM
Controls:
  [1] ORBITAL MODE      — Geometric structures orbit smoothly
  [2] CHAOS MODE        — Disintegration & turbulent instability
  [3] SINGULARITY MODE  — Gravitational vortex collapse & outward pulse
  [H] TOGGLE HUD        — Scientific telemetry heads-up display
  [R] RESET SIMULATION  — Re-align orbital bodies and particles
  [F] FULLSCREEN        — Toggle immersive fullscreen mode
  [SPACE] SHOCKWAVE     — Emit manual energy pulse
  [ESC] EXIT            — Terminate application
====================================================================
"""

import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.application import PhantomApplication

def main():
    print("""
    ==========================================================
    * PHANTOM // ORBITAL MODE
    * High-Precision Holographic Optical Research Interface
    ==========================================================
    """)
    app = PhantomApplication()
    app.run()

if __name__ == "__main__":
    main()

