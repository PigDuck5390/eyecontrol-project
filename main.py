from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QSlider, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from back.controller import Controller
import sys, pyautogui

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = Controller()
        self.setWindowTitle("시선·음성 기반 핸즈프리 컴퓨터 제어 프로그램")
        self.setFixedSize(420, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f4f8;
                font-family: 'Malgun Gothic';
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                font-size: 16px;
                border-radius: 12px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #005fa3;
            }
            QLabel {
                color: #333;
                font-size: 15px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                height: 8px;
                background: #e0e0e0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0078d7;
                border: none;
                width: 20px;
                margin: -5px 0;
                border-radius: 10px;
            }
        """)

        # 창 위치: 화면 오른쪽 아래
        sw, sh = pyautogui.size()
        self.move(sw - self.width() - 120, sh - self.height() - 120)

        # ================= 상단 로고/타이틀 =================
        title = QLabel("Eye Control")
        title.setFont(QFont("Malgun Gothic", 22, QFont.Bold))
        subtitle = QLabel("시선·음성 기반 핸즈프리 컴퓨터 제어 프로그램")
        subtitle.setStyleSheet("color: #555; font-size: 12px; margin-bottom: 12px;")

        title_frame = QVBoxLayout()
        title_frame.addWidget(title, alignment=Qt.AlignCenter)
        title_frame.addWidget(subtitle, alignment=Qt.AlignCenter)

        # ================= 상태 영역 =================
        self.status_label = QLabel("시스템 대기 중")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            background-color: white;
            border: 2px solid #0078d7;
            border-radius: 10px;
            padding: 10px;
            font-size: 16px;
        """)

        # ================= 버튼 영역 =================
        self.eye_btn = QPushButton("시선 추적 시작")
        self.eye_btn.clicked.connect(self.toggle_eye)

        self.voice_btn = QPushButton("음성 인식 시작")
        self.voice_btn.clicked.connect(self.toggle_voice)

        self.quit_btn = QPushButton("종료")
        self.quit_btn.clicked.connect(self.close_app)
        self.quit_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
            }
            QPushButton:hover {
                background-color: #b52b27;
            }
        """)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.eye_btn)
        btn_layout.addWidget(self.voice_btn)
        btn_layout.addWidget(self.quit_btn)

        # ================= 감도 조절 =================
        self.x_slider = QSlider(Qt.Horizontal)
        self.x_slider.setRange(10, 60)
        self.x_slider.setValue(30)
        self.x_slider.valueChanged.connect(self.update_sensitivity)
        self.y_slider = QSlider(Qt.Horizontal)
        self.y_slider.setRange(10, 60)
        self.y_slider.setValue(25)
        self.y_slider.valueChanged.connect(self.update_sensitivity)

        self.x_label = QLabel("X 감도: 4.5")
        self.y_label = QLabel("Y 감도: 4.5")

        sensitivity_box = QVBoxLayout()
        sensitivity_box.addWidget(self.x_label)
        sensitivity_box.addWidget(self.x_slider)
        sensitivity_box.addWidget(self.y_label)
        sensitivity_box.addWidget(self.y_slider)

        # ================= 전체 레이아웃 =================
        layout = QVBoxLayout()
        layout.addLayout(title_frame)
        layout.addWidget(self.status_label)
        layout.addLayout(btn_layout)
        layout.addSpacing(10)
        layout.addLayout(sensitivity_box)
        layout.addStretch()
        self.setLayout(layout)

        # ================= 내부 상태 =================
        self.eye_active = False
        self.voice_active = False

        # 실시간 시계나 애니메이션 추가 가능
        self.timer = QTimer()
        self.timer.timeout.connect(self.blink_status)
        self.timer.start(800)
        self.status_blink = True

    def blink_status(self):
        if not (self.eye_active or self.voice_active):
            color = "#0078d7" if self.status_blink else "#005fa3"
            self.status_label.setStyleSheet(
                f"background-color: white; border: 2px solid {color}; "
                "border-radius: 10px; padding: 10px; font-size: 16px;"
            )
            self.status_blink = not self.status_blink

    def update_sensitivity(self):
        sx = self.x_slider.value() / 10
        sy = self.y_slider.value() / 10
        self.x_label.setText(f"X 감도: {sx:.1f}")
        self.y_label.setText(f"Y 감도: {sy:.1f}")
        self.controller.set_sensitivity(sx, sy)

    def toggle_eye(self):
        if not self.eye_active:
            self.controller.start_eye()
            self.eye_btn.setText("시선 추적 중지")
            self.status_label.setText("시선 추적 활성화됨")
            self.eye_active = True
        else:
            self.controller.stop_eye()
            self.eye_btn.setText("시선 추적 시작")
            self.status_label.setText("시스템 대기 중")
            self.eye_active = False

    def toggle_voice(self):
        if not self.voice_active:
            self.controller.start_voice()
            self.voice_btn.setText("음성 인식 중지")
            self.status_label.setText("음성 인식 활성화됨")
            self.voice_active = True
        else:
            self.controller.stop_voice()
            self.voice_btn.setText("음성 인식 시작")
            self.status_label.setText("시스템 대기 중")
            self.voice_active = False

    def close_app(self):
        self.controller.stop_eye()
        self.controller.stop_voice()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
