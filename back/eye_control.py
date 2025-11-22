import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

pyautogui.FAILSAFE = False

class EyeControl:
    def __init__(self):
        self.mp_face = mp.solutions.face_mesh
        self.face_mesh = self.mp_face.FaceMesh(max_num_faces=1, refine_landmarks=True)
        self.screen_w, self.screen_h = pyautogui.size()
        self.running = False

        self.sensitivity_x = 900
        self.sensitivity_y = 900
        self.smoothening = 8
        self.deadzone = 0.004

        self.cx, self.cy = self.screen_w // 2, self.screen_h // 2
        self.pcX, self.pcY = self.cx, self.cy
        self.ref_x = None
        self.ref_y = None
        self.calibrated = False

        self.blink_threshold = 0.018
        self.blink_start_time = None
        self.blink_count = 0
        self.blink_interval = 0.45
        self.clicked = False

        self.prev_points = []
        self.overlay = None

    def set_sensitivity(self, sx, sy):
        self.sensitivity_x = sx * 300
        self.sensitivity_y = sy * 300

    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self.running = True
        start = time.time()

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = self.face_mesh.process(rgb)

            if result.multi_face_landmarks:
                face = result.multi_face_landmarks[0].landmark
                nose = np.array([face[1].x * w, face[1].y * h])

                if not self.calibrated:
                    if time.time() - start >= 1.5:
                        self.ref_x = nose[0]
                        self.ref_y = nose[1]
                        self.calibrated = True
                    continue

                nx = nose[0] - self.ref_x
                ny = nose[1] - self.ref_y

                gx = (nx)
                gy = (ny)

                if abs(gx) < self.deadzone: gx = 0
                if abs(gy) < self.deadzone: gy = 0

                dx = gx * self.sensitivity_x
                dy = gy * self.sensitivity_y

                tx = np.clip(self.cx + dx, 0, self.screen_w)
                ty = np.clip(self.cy + dy, 0, self.screen_h)

                fx = self.pcX + (tx - self.pcX) / self.smoothening
                fy = self.pcY + (ty - self.pcY) / self.smoothening

                self.prev_points.append((fx, fy))
                if len(self.prev_points) > 5:
                    self.prev_points.pop(0)

                fx = np.mean([p[0] for p in self.prev_points])
                fy = np.mean([p[1] for p in self.prev_points])

                pyautogui.moveTo(fx, fy)
                self.pcX, self.pcY = fx, fy

                eye_height = face[159].y * h - face[145].y * h
                now = time.time()

                if eye_height < self.blink_threshold:
                    if self.blink_start_time is None:
                        self.blink_start_time = now
                        self.blink_count = 1
                    elif now - self.blink_start_time <= self.blink_interval:
                        self.blink_count += 1
                else:
                    if self.blink_count >= 2 and not self.clicked:
                        pyautogui.click()
                        self.clicked = True
                        if self.overlay:
                            self.overlay.trigger_click_effect()
                    elif eye_height >= self.blink_threshold:
                        self.clicked = False

                    if self.blink_start_time and now - self.blink_start_time > self.blink_interval:
                        self.blink_count = 0
                        self.blink_start_time = None

        cap.release()
        cv2.destroyAllWindows()

    def stop(self):
        self.running = False
