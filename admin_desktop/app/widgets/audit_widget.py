from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QComboBox,
    QLineEdit, QSpacerItem, QSizePolicy,
)
from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont, QColor


class AuditWidget(QWidget):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self.setup_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(30000)

    def setup_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Audit Log")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)

        toolbar = QHBoxLayout()
        self.event_filter = QComboBox()
        self.event_filter.addItems(["Barcha hodisalar", "login", "app_blocked",
                                     "web_blocked", "usb_connected", "policy_changed"])
        self.event_filter.currentTextChanged.connect(self.refresh)
        toolbar.addWidget(self.event_filter)

        self.severity_filter = QComboBox()
        self.severity_filter.addItems(["Barcha", "info", "warning", "critical"])
        self.severity_filter.currentTextChanged.connect(self.refresh)
        toolbar.addWidget(self.severity_filter)

        refresh_btn = QPushButton("Yangilash")
        refresh_btn.clicked.connect(self.refresh)
        toolbar.addWidget(refresh_btn)
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Vaqt", "Hodisa", "Muhimlik", "Kompyuter", "Foydalanuvchi", "Tavsif"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def refresh(self):
        try:
            params = {"page": 1, "page_size": 200}
            event = self.event_filter.currentText()
            if event != "Barcha hodisalar":
                params["event_type"] = event
            severity = self.severity_filter.currentText()
            if severity != "Barcha":
                params["severity"] = severity

            data = self.api.get("audit", params=params) or {"items": [], "total": 0}
            items = data.get("items", [])
            self.table.setRowCount(len(items))

            severity_colors = {
                "critical": QColor("#e74c3c"),
                "warning": QColor("#f39c12"),
                "info": QColor("#3498db"),
            }

            for row, log in enumerate(items):
                created = str(log.get("created_at", ""))[:19]
                self.table.setItem(row, 0, QTableWidgetItem(created))
                self.table.setItem(row, 1, QTableWidgetItem(log.get("event_type", "")))
                sev = log.get("severity", "info")
                sev_item = QTableWidgetItem(sev)
                sev_item.setBackground(severity_colors.get(sev, QColor("white")))
                sev_item.setForeground(QColor("white"))
                self.table.setItem(row, 2, sev_item)
                self.table.setItem(row, 3, QTableWidgetItem(str(log.get("computer_id", ""))[:8]))
                self.table.setItem(row, 4, QTableWidgetItem(str(log.get("user_id", ""))[:8]))
                self.table.setItem(row, 5, QTableWidgetItem(log.get("description", "")))
        except Exception as e:
            print(f"Error loading audit logs: {e}")
