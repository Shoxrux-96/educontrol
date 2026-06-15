import sys
import logging
from PySide6.QtWidgets import QApplication
from app.windows.login_window import LoginWindow
from app.windows.main_window import MainWindow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EduControlApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("EDU Control Pro")
        self.app.setApplicationVersion("1.0.0")
        self.login_window = None
        self.main_window = None

    def run(self):
        self.login_window = LoginWindow(self.on_login_success)
        self.login_window.show()
        sys.exit(self.app.exec())

    def on_login_success(self, token: str, user: dict):
        self.login_window.close()
        self.main_window = MainWindow(token, user)
        self.main_window.show()


if __name__ == "__main__":
    app = EduControlApp()
    app.run()
