from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout,
    QPushButton, QScrollArea, QComboBox,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap
import base64


class ScreenMonitorWidget(QWidget):
    def __init__(self, api):
        super().__init__()
        self.api = api
        self.setup_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(15000)

    def setup_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Screen Monitoring")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)

        toolbar = QHBoxLayout()
        self.group_filter = QComboBox()
        self.group_filter.addItem("Barcha kompyuterlar")
        toolbar.addWidget(self.group_filter)
        refresh_btn = QPushButton("Yangilash")
        refresh_btn.clicked.connect(self.refresh)
        toolbar.addWidget(refresh_btn)
        layout.addLayout(toolbar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        scroll.setWidget(self.grid_widget)
        layout.addWidget(scroll)
        self.setLayout(layout)

    def refresh(self):
        try:
            data = self.api.get("computers", params={"page": 1, "page_size": 50, "status": "online"})
            items = data.get("items", [])

            for i in reversed(range(self.grid_layout.count())):
                widget = self.grid_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            row, col = 0, 0
            for comp in items:
                frame = QWidget()
                frame_layout = QVBoxLayout(frame)
                name = QLabel(comp.get("name", "Unknown"))
                name.setAlignment(Qt.AlignCenter)
                frame_layout.addWidget(name)
                preview = QLabel(f"CPU: {comp.get('cpu_usage', 0)}% | RAM: {comp.get('ram_usage', 0)}%")
                preview.setAlignment(Qt.AlignCenter)
                frame_layout.addWidget(preview)
                self.grid_layout.addWidget(frame, row, col)
                col += 1
                if col >= 5:
                    col = 0
                    row += 1
        except Exception as e:
            print(f"Error refreshing screens: {e}")
