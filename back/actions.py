import pyautogui
import time

class Actions:
    def __init__(self):
        self.last_x = None
        self.last_y = None
        self.last_time = time.time()

    def dwell_click(self, x, y, threshold=1.0, tolerance=15):
        """
        시선이 threshold초 동안 거의 움직이지 않으면 자동 클릭
        tolerance: 픽셀 허용치
        """
        if self.last_x is None:
            self.last_x, self.last_y = x, y
            self.last_time = time.time()
            return

        distance = ((x - self.last_x) ** 2 + (y - self.last_y) ** 2) ** 0.5
        now = time.time()

        if distance < tolerance:
            if now - self.last_time > threshold:
                pyautogui.click()
                print("Dwell Click!")
                self.last_time = now
        else:
            self.last_x, self.last_y = x, y
            self.last_time = now
