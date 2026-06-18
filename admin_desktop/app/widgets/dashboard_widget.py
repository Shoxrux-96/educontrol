from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QSpacerItem, QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont


class StatCard(QFrame):
    def __init__(self, title, value="0", color="#3498db"):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 10px;
                padding: 20px;
                color: white;
            }}
            QLabel {{ color: white; }}
        """)
        layout = QVBoxLayout()
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Arial", 12))
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Arial", 28, QFont.Bold))
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        self.setLayout(layout)

    def update_value(self, value):
        self.value_label.setText(str(value))


class DashboardWidget(QWidget):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self.setup_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(5000)

    def setup_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Dashboard")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)

        grid = QGridLayout()
        self.online_card = StatCard("Online", "0", "#2ecc71")
        self.offline_card = StatCard("Offline", "0", "#e74c3c")
        self.total_card = StatCard("Jami kompyuterlar", "0", "#3498db")
        self.alerts_card = StatCard("Ogohlantirishlar", "0", "#f39c12")

        grid.addWidget(self.total_card, 0, 0)
        grid.addWidget(self.online_card, 0, 1)
        grid.addWidget(self.offline_card, 1, 0)
        grid.addWidget(self.alerts_card, 1, 1)

        layout.addLayout(grid)
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.setLayout(layout)

    def refresh(self):
        try:
            data = self.api.get("computers") or {"items": [], "total": 0}
            items = data.get("items", [])
            online = sum(1 for c in items if c.get("status") == "online")
            offline = sum(1 for c in items if c.get("status") == "offline")
            self.online_card.update_value(online)
            self.offline_card.update_value(offline)
            self.total_card.update_value(data.get("total", 0))
        except Exception:
            pass
