import sys
from PyQt5.QtWidgets import QApplication
from back.controller import Controller
from front.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = Controller()
    window = MainWindow(controller)
    window.show()
    sys.exit(app.exec_())
