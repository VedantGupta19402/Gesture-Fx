# Gesture-Controlled 3D Particle System 🖐️✨

An interactive **Spatial Computing** project that bridges Computer Vision and 3D Graphics. This application uses a standard webcam to track hand landmarks, allowing for real-time manipulation of a "Neon" particle grid in 3D space.

## ✨ Features
* **Pinch-to-Scale:** Dynamically resize the particle grid using the distance between the right-hand thumb and index finger.
* **Gesture-Locked Rotation:** Rotate the cube along the X and Y axes using left-hand movement. Includes a gesture filter (Two-Finger Up) to prevent accidental rotations.
* **Neon Aesthetics:** Rendered with PyOpenGL using additive blending and depth testing for a high-fidelity glow effect.
* **Motion Smoothing:** Implements **Linear Interpolation (Lerp)** to ensure transitions between hand movements feel fluid and organic.

## 🛠️ Technical Stack
* **MediaPipe:** AI-powered hand landmark detection.
* **PyOpenGL:** Low-level 3D graphics rendering.
* **Pygame:** Management of the OpenGL context and window events.
* **OpenCV:** Video stream capture and BGR-to-RGB processing.
* **NumPy:** Efficient coordinate and vector math.

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Mrez2/Gesture-Controlled-3D-Manipulation.git](https://github.com/Mrez2/Gesture-Controlled-3D-Manipulation.git)
   cd Gesture-Controlled-3D-Manipulation
Install dependencies:Bashpip install opencv-python mediapipe pygame PyOpenGL numpy
Run the application:Bashpython main.py
🎮 ControlsHandActionResultRightPinch (Thumb + Index)Scale Cube (Zoom In/Out)LeftTwo Fingers Up (Index + Middle)Enable Rotation ModeLeftMove Wrist/PalmRotate Grid in 3D Space📝 DescriptionInteractive 3D neon particle system built with Python, MediaPipe, and PyOpenGL. This project enables touchless spatial manipulation: use your right hand to pinch-and-scale the grid, and a two-finger gesture on your left hand to trigger smooth 3D rotation. Features real-time landmark tracking, additive glow effects, and fluid Lerp-based motion.
