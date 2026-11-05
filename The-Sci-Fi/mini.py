import cv2
import mediapipe as mp
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math

# ------------------ MEDIAPIPE ------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
cap = cv2.VideoCapture(0)

# ------------------ OPENGL ------------------
pygame.init()
display = (900, 700)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

gluPerspective(60, display[0]/display[1], 0.1, 100)
glTranslatef(0, 0, -8)

glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # neon glow

# ------------------ PARTICLE CUBE ------------------
GRID = 4
BASE_POS = []

for x in range(GRID):
    for y in range(GRID):
        for z in range(GRID):
            BASE_POS.append(np.array([
                (x - GRID/2) * 2,
                (y - GRID/2) * 1.5,
                (z - GRID/2) * 1.5
            ]))

# ------------------ STATE ------------------
scale_target = 1.0
scale = 1.0
rot_x_target = 0
rot_y_target = 0
rot_x = 0
rot_y = 0

# ------------------ HELPERS ------------------
def distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)

def lerp(a, b, t=0.1):
    return a + (b - a) * t

def draw_sphere(pos, r=0.25):
    glPushMatrix()
    glTranslatef(pos[0], pos[1], pos[2])
    quad = gluNewQuadric()
    gluSphere(quad, r, 10, 10)
    glPopMatrix()

def two_fingers_up(hand):
    """
    Returns True if exactly index + middle fingers are up,
    and ring + pinky are down
    """
    index_up = hand.landmark[8].y < hand.landmark[6].y
    middle_up = hand.landmark[12].y < hand.landmark[10].y
    ring_down = hand.landmark[16].y > hand.landmark[14].y
    pinky_down = hand.landmark[20].y > hand.landmark[18].y
    return index_up and middle_up and ring_down and pinky_down

# ------------------ LOOP ------------------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            cap.release()
            quit()

    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks and result.multi_handedness:
        for hand, handed in zip(result.multi_hand_landmarks, result.multi_handedness):
            label = handed.classification[0].label

            # ----- RIGHT HAND → SCALE (UNCHANGED) -----
            if label == "Right":
                d = distance(hand.landmark[4], hand.landmark[8])
                scale_target = max(0.8, min(d * 8, 4))

            # ----- LEFT HAND → ROTATION (ONLY 2 FINGERS) -----
            if label == "Left":
                if two_fingers_up(hand):
                    wrist = hand.landmark[0]
                    mid = hand.landmark[9]
                    rot_x_target = (mid.y - wrist.y) * 300
                    rot_y_target = (mid.x - wrist.x) * 300
                # else → do nothing, rotation freezes

    # ---------- SMOOTHING ----------
    scale = lerp(scale, scale_target)
    rot_x = lerp(rot_x, rot_x_target)
    rot_y = lerp(rot_y, rot_y_target)

    particles = [p * scale for p in BASE_POS]

    # ---------- RENDER ----------
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glPushMatrix()

    glRotatef(rot_x, 1, 0, 0)
    glRotatef(rot_y, 0, 1, 0)

    # ----- CONNECTING LINES -----
    glColor4f(0.0, 1.0, 0.6, 0.15)
    glBegin(GL_LINES)
    for i in range(len(particles)):
        for j in range(i + 1, len(particles)):
            if np.linalg.norm(particles[i] - particles[j]) < 2.2:
                glVertex3fv(particles[i])
                glVertex3fv(particles[j])
    glEnd()

    # ----- PARTICLES -----
    glColor4f(0.0, 1.0, 0.6, 0.8)
    for p in particles:
        draw_sphere(p)

    glPopMatrix()
    pygame.display.flip()
    pygame.time.wait(10)

    cv2.imshow("Hand Control", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
pygame.quit()
