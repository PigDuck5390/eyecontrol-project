import queue
import sounddevice as sd
import vosk
import json
import pyautogui
import time
import pyperclip

class VoiceControl:
    def __init__(self, controller=None, vosk_model=None):
        self.q = queue.Queue()
        self.model = vosk_model
        self.recognizer = None
        self.running = False
        self.controller = controller

    def _ensure_model(self):
        if self.model and self.recognizer is None:
            try:
                self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
            except Exception as e:
                print("VOSK 초기화 오류:", e)
                self.running = False
        elif not self.model:
            print("음성 모델이 로드되지 않았습니다. run() 실행 중지")
            self.running = False

    def _callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.q.put(bytes(indata))

    def _process_command(self, text):
        text = text.strip().lower()
        if not text:
            return

        print("[음성 인식]", text)

        try:
            if "멈춰" in text or "중지" in text:
                if self.controller:
                    self.controller.stop_eye()
                    self.controller.stop_voice()
                return

            if "클릭" in text:
                pyautogui.click()
                print("클릭 실행")
                return

            if "엔터" in text:
                pyautogui.press("enter")
                print("엔터 실행")
                return

            if "위" in text or "올려" in text:
                pyautogui.scroll(500)
                print("스크롤 위")
                return

            if "아래" in text or "내려" in text:
                pyautogui.scroll(-500)
                print("스크롤 아래")
                return

            pyperclip.copy(text)
            pyautogui.hotkey("ctrl", "v")
            pyautogui.press("space")
            print("입력됨:", text)

        except Exception as e:
            print("PyAutoGUI 오류:", e)

    def run(self):
        print("VoiceControl 시작 — 명령(클릭/엔터/스크롤/멈춰) 지원")

        self._ensure_model()
        if not self.model:
            return

        self.running = True

        try:
            with sd.RawInputStream(
                samplerate=16000,
                blocksize=4000,
                dtype="int16",
                channels=1,
                callback=self._callback,
                device=1   # USB 마이크 인덱스
            ):
                while self.running:
                    try:
                        data = self.q.get(timeout=0.1)
                    except queue.Empty:
                        continue

                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get("text", "")
                        if text:
                            self._process_command(text)

                    time.sleep(0.01)

        except Exception as e:
            print("음성 인식 오류:", e)

    def stop(self):
        self.running = False
        print("VoiceControl 종료")
