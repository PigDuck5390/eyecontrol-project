from PyQt5.QtWidgets import QApplication
from back.controller import Controller
from front.main_window import MainWindow
import vosk
import sys, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "vosk-model-small-ko-0.22")

if __name__ == "__main__":
    try:
        vosk_model = vosk.Model(MODEL_PATH)
    except Exception as e:
        print("VOSK 모델 로드 오류:", e)
        vosk_model = None

    app = QApplication(sys.argv)
    controller = Controller(vosk_model=vosk_model)
    window = MainWindow(controller)
    window.show()
    sys.exit(app.exec_())
