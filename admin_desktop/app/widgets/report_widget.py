import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QDateEdit, QProgressBar, QMessageBox,
    QSpacerItem, QSizePolicy,
)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QFont


class ReportWidget(QWidget):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Hisobotlar")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)

        form = QVBoxLayout()

        self.report_type = QComboBox()
        self.report_type.addItems(["daily", "weekly", "monthly", "custom"])
        form.addWidget(QLabel("Hisobot turi:"))
        form.addWidget(self.report_type)

        date_layout = QHBoxLayout()
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.start_date.setCalendarPopup(True)
        date_layout.addWidget(QLabel("Boshlanish:"))
        date_layout.addWidget(self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        date_layout.addWidget(QLabel("Tugash:"))
        date_layout.addWidget(self.end_date)
        form.addLayout(date_layout)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["pdf", "excel", "csv"])
        form.addWidget(QLabel("Format:"))
        form.addWidget(self.format_combo)

        generate_btn = QPushButton("Hisobot yaratish")
        generate_btn.setMinimumHeight(40)
        generate_btn.clicked.connect(self.generate_report)
        form.addWidget(generate_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        form.addWidget(self.progress_bar)

        form.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addLayout(form)
        self.setLayout(layout)

    def generate_report(self):
        try:
            data = {
                "report_type": self.report_type.currentText(),
                "start_date": self.start_date.date().toString("yyyy-MM-dd"),
                "end_date": self.end_date.date().toString("yyyy-MM-dd"),
                "scope": "all",
                "format": self.format_combo.currentText(),
                "include": ["internet", "applications", "usb", "print"],
            }

            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(10)

            result = self.api.post("reports/generate", data)
            task_id = result.get("task_id", "")

            if task_id:
                self.progress_bar.setValue(50)
                QMessageBox.information(
                    self, "Muvaffaqiyat",
                    f"Hisobot yaratish boshlandi. Task ID: {task_id}\n"
                    f"Yuklab olish: /reports/{task_id}/download"
                )
            self.progress_bar.setValue(100)
        except Exception as e:
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, "Xatolik", str(e))
