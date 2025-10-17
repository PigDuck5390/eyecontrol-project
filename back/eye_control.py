import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
from collections import deque

pyautogui.FAILSAFE = False  # (0,0) 가도 중단 안 되게

class EyeControl:
    def __init__(self):
        self.mp_face = mp.solutions.face_mesh
        self.face_mesh = self.mp_face.FaceMesh(max_num_faces=1)
        self.screen_w, self.screen_h = pyautogui.size()
        self.running = False

        # 감도
        self.sensitivity_x = 3.0
        self.sensitivity_y = 2.5

        # 기준점 / 이동평균
        self.ref_x = None
        self.ref_y = None
        self.positions = deque(maxlen=5)

        # dwell 클릭
        self.last_pos = None
        self.last_time = time.time()
        self.dwell_threshold = 1.0
        self.dwell_tolerance = 30

        # 기본 좌우 반전 ON
        self.lr_sign = 1

    def set_sensitivity(self, sx, sy):
        self.sensitivity_x = sx
        self.sensitivity_y = sy

    def _check_dwell_click(self, x, y):
        now = time.time()
        if self.last_pos is None:
            self.last_pos = (x, y)
            self.last_time = now
            return
        dist = np.hypot(x - self.last_pos[0], y - self.last_pos[1])
        if dist < self.dwell_tolerance:
            if now - self.last_time > self.dwell_threshold:
                pyautogui.click()
                print("🖱 Dwell Click!")
                self.last_time = now
        else:
            self.last_pos = (x, y)
            self.last_time = now

    def run(self):
        cap = cv2.VideoCapture(0)
        self.running = True
        print("Eye Tracking 시작 — 2초간 중앙을 바라봐 주세요 (자동 보정 중)")

        start = time.time()
        calibrated_center = False

        while self.running:
            ok, frame = cap.read()
            if not ok:
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb)
            frame_h, frame_w, _ = frame.shape

            if results.multi_face_landmarks:
                face = results.multi_face_landmarks[0].landmark
                nose = face[1]
                x = int(nose.x * frame_w)
                y = int(nose.y * frame_h)

                if not calibrated_center and time.time() - start >= 2.0:
                    self.ref_x, self.ref_y = x, y
                    calibrated_center = True
                    print("✅ 중앙 보정 완료")
                    continue

                if calibrated_center:
                    dx = self.lr_sign * (x - self.ref_x) * self.sensitivity_x
                    dy = (y - self.ref_y) * self.sensitivity_y

                    move_x = self.screen_w / 2 + dx
                    move_y = self.screen_h / 2 + dy

                    move_x = np.clip(move_x, 5, self.screen_w - 5)
                    move_y = np.clip(move_y, 5, self.screen_h - 5)

                    self.positions.append((move_x, move_y))
                    avg_x, avg_y = np.mean(self.positions, axis=0)

                    pyautogui.moveTo(avg_x, avg_y)
                    self._check_dwell_click(avg_x, avg_y)

        cap.release()
        cv2.destroyAllWindows()

    def stop(self):
        self.running = False
        print("Eye Tracking 중지됨")
