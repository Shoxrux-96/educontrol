from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QLineEdit, QHeaderView,
    QComboBox, QSpacerItem, QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor


class ComputerListWidget(QWidget):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self.setup_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(10000)

    def setup_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Kompyuterlar ro'yxati")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)

        toolbar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Qidirish...")
        self.search_input.setMinimumHeight(35)
        self.search_input.textChanged.connect(self.refresh)
        toolbar.addWidget(self.search_input)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["Barchasi", "Online", "Offline", "Busy", "Locked"])
        self.status_filter.currentTextChanged.connect(self.refresh)
        toolbar.addWidget(self.status_filter)

        refresh_btn = QPushButton("Yangilash")
        refresh_btn.clicked.connect(self.refresh)
        toolbar.addWidget(refresh_btn)
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Nomi", "IP Manzil", "Status", "CPU%", "RAM%",
            "Disk%", "Foydalanuvchi", "Oxirgi ko'rilgan"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def refresh(self):
        try:
            params = {"page": 1, "page_size": 100}
            search = self.search_input.text().strip()
            if search:
                params["search"] = search
            status = self.status_filter.currentText()
            if status != "Barchasi":
                params["status"] = status.lower()

            data = self.api.get("computers", params=params) or {"items": [], "total": 0}
            items = data.get("items", [])
            self.table.setRowCount(len(items))

            status_colors = {
                "online": QColor("#2ecc71"),
                "offline": QColor("#e74c3c"),
                "busy": QColor("#f39c12"),
                "locked": QColor("#3498db"),
            }

            for row, comp in enumerate(items):
                self.table.setItem(row, 0, QTableWidgetItem(comp.get("name", "")))
                self.table.setItem(row, 1, QTableWidgetItem(comp.get("ip_address", "")))
                status = comp.get("status", "offline")
                status_item = QTableWidgetItem(status)
                status_item.setBackground(status_colors.get(status, QColor("gray")))
                status_item.setForeground(QColor("white"))
                self.table.setItem(row, 2, status_item)
                self.table.setItem(row, 3, QTableWidgetItem(str(comp.get("cpu_usage", 0))))
                self.table.setItem(row, 4, QTableWidgetItem(str(comp.get("ram_usage", 0))))
                self.table.setItem(row, 5, QTableWidgetItem(str(comp.get("disk_usage", 0))))
                self.table.setItem(row, 6, QTableWidgetItem(comp.get("current_user", "")))
                last_seen = comp.get("last_seen", "")
                if last_seen:
                    last_seen = str(last_seen)[:19]
                self.table.setItem(row, 7, QTableWidgetItem(last_seen))
        except Exception as e:
            print(f"Error refreshing computers: {e}")
