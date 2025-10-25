import queue
import sounddevice as sd
import vosk
import json
import pyautogui

class VoiceControl:
    def __init__(self, model_path="model/vosk-model-small-ko-0.22", controller=None):
        self.q = queue.Queue()
        self.model_path = model_path
        self.model = None
        self.recognizer = None
        self.running = False
        self.controller = controller  # 전체 제어를 위해 Controller 객체 참조

    def _ensure_model(self):
        if self.model is None:
            self.model = vosk.Model(self.model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, 16000)

    def _callback(self, indata, frames, time, status):
        if status:
            print(status, flush=True)
        self.q.put(bytes(indata))

    def _process_command(self, text):
        """음성 명령어 처리"""
        text = text.strip().lower()
        if not text:
            return

        print(f"인식된 명령: {text}")

        # ====== 종료 명령 ======
        if "멈춰" in text or "중지" in text or "정지" in text or "stop" in text:
            if self.controller:
                print("음성 명령으로 시스템 종료")
                self.controller.stop_eye()
                self.controller.stop_voice()
            return

        # ====== 클릭 관련 ======
        if "클릭" in text or "click" in text:
            if "더블" in text or "double" in text:
                pyautogui.doubleClick()
                print("음성 명령: 더블클릭 실행")
            else:
                pyautogui.click()
                print("음성 명령: 클릭 실행")

        # ====== 엔터 ======
        elif "엔터" in text or "enter" in text:
            pyautogui.press("enter")
            print("음성 명령: 엔터 실행")

        # ====== 스크롤 ======
        elif "위" in text or "올려" in text:
            pyautogui.scroll(500)
            print("스크롤 위로")
        elif "아래" in text or "내려" in text:
            pyautogui.scroll(-500)
            print("스크롤 아래로")

        # ====== 기타 텍스트 입력 ======
        else:
            pyautogui.typewrite(text + " ")
            print(f"입력된 음성 텍스트: {text}")

    def run(self):
        print("음성 인식 시작 — 클릭, 엔터, 스크롤, 멈춰 명령 지원")
        self._ensure_model()
        self.running = True
        try:
            with sd.RawInputStream(
                samplerate=16000,
                blocksize=8000,
                dtype="int16",
                channels=1,
                callback=self._callback,
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
        except Exception as e:
            print(f"Voice stream error: {e}")

    def stop(self):
        self.running = False
        print("🛑 Voice Control 중지됨")
