from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pyautogui

class MainWindow(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("시선·음성 기반 핸즈프리 컴퓨터 제어 프로그램")
        self.setFixedSize(480, 500)

        self.overlay_circle = None  # overlay 제거

        self.setStyleSheet("""
            QWidget { background-color: #e8f1ff; font-family: 'Malgun Gothic'; }
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4facfe, stop:1 #00f2fe);
                color: white; padding: 12px; font-size: 17px;
                border-radius: 14px; font-weight: bold; letter-spacing: 1px;
            }
            QPushButton:hover { background-color: #3ea7ff; }
            QLabel { color: #1d3557; }
        """)

        sw, sh = pyautogui.size()
        self.move(sw - self.width() - 120, sh - self.height() - 120)

        title = QLabel("Eye Control")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Malgun Gothic", 26, QFont.Bold))

        subtitle = QLabel("시선·음성 기반 핸즈프리 컴퓨터 제어")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #457b9d; margin-bottom: 10px;")

        self.status_label = QLabel("시스템 대기 중")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("background:white; border-radius:14px; border:2px solid #4facfe; padding:12px; font-size:18px; font-weight:bold;")

        self.eye_btn = QPushButton("시선 추적 시작")
        self.eye_btn.clicked.connect(self.toggle_eye)

        self.voice_btn = QPushButton("음성 인식 시작")
        self.voice_btn.clicked.connect(self.toggle_voice)

        self.quit_btn = QPushButton("종료")
        self.quit_btn.setStyleSheet("QPushButton { background-color:#e63946; color:white; font-size:17px; border-radius:14px; font-weight:bold; } QPushButton:hover { background-color:#cc2b36; }")
        self.quit_btn.clicked.connect(self.close_app)

        btn_box = QHBoxLayout()
        btn_box.addWidget(self.eye_btn)
        btn_box.addWidget(self.voice_btn)
        btn_box.addWidget(self.quit_btn)

        self.sx = 3.0
        self.sy = 3.0

        self.x_label = QLabel(f"커서 반응 속도 (좌우): {self.sx:.1f}")
        self.x_label.setAlignment(Qt.AlignCenter)
        self.x_label.setFont(QFont("Malgun Gothic", 15, QFont.Bold))

        self.y_label = QLabel(f"커서 반응 속도 (상하): {self.sy:.1f}")
        self.y_label.setAlignment(Qt.AlignCenter)
        self.y_label.setFont(QFont("Malgun Gothic", 15, QFont.Bold))

        self.x_minus = QPushButton("-")
        self.x_plus = QPushButton("+")
        self.y_minus = QPushButton("-")
        self.y_plus = QPushButton("+")

        for b in (self.x_minus, self.x_plus, self.y_minus, self.y_plus):
            b.setFixedSize(45, 38)
            b.setStyleSheet("QPushButton { background-color:#1d3557; color:white; border-radius:10px; font-size:18px; } QPushButton:hover { background-color:#27496d; }")

        self.x_minus.clicked.connect(self.dec_x)
        self.x_plus.clicked.connect(self.inc_x)
        self.y_minus.clicked.connect(self.dec_y)
        self.y_plus.clicked.connect(self.inc_y)

        x_box = QHBoxLayout()
        x_box.addWidget(self.x_minus)
        x_box.addWidget(self.x_label)
        x_box.addWidget(self.x_plus)

        y_box = QHBoxLayout()
        y_box.addWidget(self.y_minus)
        y_box.addWidget(self.y_label)
        y_box.addWidget(self.y_plus)

        self.cmd_label = QLabel("현재 명령: 대기 중")
        self.cmd_label.setAlignment(Qt.AlignCenter)
        self.cmd_label.setStyleSheet("background-color:white; border-radius:14px; border:2px solid #4facfe; padding:12px; font-size:18px; margin-top:8px; font-weight:bold;")

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.status_label)
        layout.addSpacing(12)
        layout.addLayout(btn_box)
        layout.addSpacing(12)
        layout.addLayout(x_box)
        layout.addLayout(y_box)
        layout.addSpacing(12)
        layout.addWidget(self.cmd_label)
        layout.addStretch()
        self.setLayout(layout)

        self.controller.ui = self
        self.eye_active = False
        self.voice_active = False

    def dec_x(self):
        self.sx = max(0.2, self.sx - 0.1)
        self.x_label.setText(f"커서 반응 속도 (좌우): {self.sx:.1f}")
        self.controller.set_sensitivity(self.sx, self.sy)

    def inc_x(self):
        self.sx = min(6.0, self.sx + 0.1)
        self.x_label.setText(f"커서 반응 속도 (좌우): {self.sx:.1f}")
        self.controller.set_sensitivity(self.sx, self.sy)

    def dec_y(self):
        self.sy = max(0.2, self.sy - 0.1)
        self.y_label.setText(f"커서 반응 속도 (상하): {self.sy:.1f}")
        self.controller.set_sensitivity(self.sx, self.sy)

    def inc_y(self):
        self.sy = min(6.0, self.sy + 0.1)
        self.y_label.setText(f"커서 반응 속도 (상하): {self.sy:.1f}")
        self.controller.set_sensitivity(self.sx, self.sy)

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
