from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QLineEdit, QTextEdit, QComboBox, QDialogButtonBox,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class PolicyDialog(QDialog):
    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.api = api
        self.setWindowTitle("Yangi siyosat")
        self.setMinimumWidth(500)
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()
        self.name_input = QLineEdit()
        layout.addRow("Nomi:", self.name_input)

        self.desc_input = QTextEdit()
        layout.addRow("Tavsif:", self.desc_input)

        self.type_input = QComboBox()
        self.type_input.addItems(["internet", "application", "usb", "print_screen"])
        layout.addRow("Turi:", self.type_input)

        self.config_input = QTextEdit()
        self.config_input.setPlaceholderText('{"mode": "whitelist", "allowed_domains": ["example.com"]}')
        layout.addRow("Konfiguratsiya (JSON):", self.config_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        self.setLayout(layout)

    def get_data(self):
        import json
        return {
            "name": self.name_input.text(),
            "description": self.desc_input.toPlainText(),
            "policy_type": self.type_input.currentText(),
            "config": json.loads(self.config_input.toPlainText() or "{}"),
        }


class PolicyWidget(QWidget):
    def __init__(self, api, user):
        super().__init__()
        self.api = api
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Siyosatlar boshqaruvi")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)

        toolbar = QHBoxLayout()
        add_btn = QPushButton("+ Yangi siyosat")
        add_btn.clicked.connect(self.add_policy)
        toolbar.addWidget(add_btn)
        refresh_btn = QPushButton("Yangilash")
        refresh_btn.clicked.connect(self.refresh)
        toolbar.addWidget(refresh_btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Nomi", "Turi", "Holat", "Yaratilgan", "Amallar"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.refresh()

    def refresh(self):
        try:
            data = self.api.get("policies") or []
            self.table.setRowCount(len(data))
            for row, policy in enumerate(data):
                self.table.setItem(row, 0, QTableWidgetItem(policy.get("name", "")))
                self.table.setItem(row, 1, QTableWidgetItem(policy.get("policy_type", "")))
                self.table.setItem(row, 2, QTableWidgetItem(
                    "Aktiv" if policy.get("is_active") else "Noaktiv"
                ))
                created = policy.get("created_at", "")
                self.table.setItem(row, 3, QTableWidgetItem(str(created)[:19]))
                delete_btn = QPushButton("O'chirish")
                delete_btn.clicked.connect(lambda checked, pid=policy["id"]: self.delete_policy(pid))
                self.table.setCellWidget(row, 4, delete_btn)
        except Exception as e:
            print(f"Error loading policies: {e}")

    def add_policy(self):
        dialog = PolicyDialog(self.api, self)
        if dialog.exec():
            try:
                data = dialog.get_data()
                self.api.post("policies", data)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Xatolik", str(e))

    def delete_policy(self, policy_id):
        reply = QMessageBox.question(self, "Tasdiqlash",
                                     "Bu siyosatni o'chirishni xohlaysizmi?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.api.delete(f"policies/{policy_id}")
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Xatolik", str(e))
