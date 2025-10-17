from back.eye_control import EyeControl
from back.voice_control import VoiceControl
import threading

class Controller:
    def __init__(self):
        self.eye = EyeControl()
        self.voice = VoiceControl(controller=self)
        self.eye_thread = None
        self.voice_thread = None

    def start_eye(self):
        if self.eye_thread is None or not self.eye_thread.is_alive():
            self.eye_thread = threading.Thread(target=self.eye.run, daemon=True)
            self.eye_thread.start()
            print("👁 EyeControl 실행됨")

    def stop_eye(self):
        self.eye.stop()

    def start_voice(self):
        if self.voice_thread is None or not self.voice_thread.is_alive():
            self.voice_thread = threading.Thread(target=self.voice.run, daemon=True)
            self.voice_thread.start()
            print("🎤 VoiceControl 실행됨")

    def stop_voice(self):
        self.voice.stop()

    def set_sensitivity(self, x, y):
        self.eye.set_sensitivity(x, y)

    def set_swap_lr(self, enabled: bool):
        self.eye.set_swap_lr(enabled)
