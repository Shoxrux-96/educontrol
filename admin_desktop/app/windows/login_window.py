from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QSpacerItem, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from app.services.api_client import ApiClient


class LoginWindow(QWidget):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.api = ApiClient()
        self.setWindowTitle("EDU Control Pro - Login")
        self.setFixedSize(400, 500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("EDU Control Pro")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("O'quv markazlari uchun boshqaruv tizimi")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Foydalanuvchi nomi")
        self.username_input.setMinimumHeight(40)
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Parol")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        layout.addWidget(self.password_input)

        self.login_btn = QPushButton("Kirish")
        self.login_btn.setMinimumHeight(45)
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Xatolik", "Iltimos, foydalanuvchi nomi va parolni kiriting")
            return

        self.login_btn.setEnabled(False)
        self.status_label.setText("Kirish amalga oshirilmoqda...")

        try:
            result = self.api.login(username, password)
            self.on_success(result["access_token"], result["user"])
        except Exception as e:
            self.status_label.setText("")
            QMessageBox.critical(self, "Xatolik", f"Kirish muvaffaqiyatsiz: {str(e)}")
        finally:
            self.login_btn.setEnabled(True)
