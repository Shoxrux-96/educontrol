from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QLabel, QStatusBar,
    QListWidget, QListWidgetItem, QSplitter,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon

from app.widgets.dashboard_widget import DashboardWidget
from app.widgets.computer_list_widget import ComputerListWidget
from app.widgets.screen_monitor_widget import ScreenMonitorWidget
from app.widgets.policy_widget import PolicyWidget
from app.widgets.audit_widget import AuditWidget
from app.widgets.report_widget import ReportWidget
from app.services.api_client import ApiClient


class MainWindow(QMainWindow):
    def __init__(self, token: str, user: dict):
        super().__init__()
        self.token = token
        self.user = user
        self.api = ApiClient(token)
        self.setWindowTitle(f"EDU Control Pro - {user.get('full_name', user['username'])}")
        self.setMinimumSize(1280, 800)
        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        self.nav_list = QListWidget()
        self.nav_list.setFixedWidth(200)
        self.nav_list.setFont(QFont("Arial", 12))

        nav_items = [
            ("Dashboard", "dashboard"),
            ("Kompyuterlar", "computers"),
            ("Screen Monitor", "screen"),
            ("Siyosatlar", "policies"),
            ("Audit Log", "audit"),
            ("Hisobotlar", "reports"),
        ]

        for label, key in nav_items:
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, key)
            item.setSizeHint(QSize(0, 50))
            self.nav_list.addItem(item)

        self.nav_list.currentItemChanged.connect(self.on_nav_change)

        self.stack = QStackedWidget()
        self.widgets = {}
        self.widgets["dashboard"] = DashboardWidget(self.api)
        self.widgets["computers"] = ComputerListWidget(self.api)
        self.widgets["screen"] = ScreenMonitorWidget(self.api)
        self.widgets["policies"] = PolicyWidget(self.api, self.user)
        self.widgets["audit"] = AuditWidget(self.api)
        self.widgets["reports"] = ReportWidget(self.api)

        for w in self.widgets.values():
            self.stack.addWidget(w)

        main_layout.addWidget(self.nav_list)
        main_layout.addWidget(self.stack, 1)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Tizimga ulandi")

        if self.nav_list.count() > 0:
            self.nav_list.setCurrentRow(0)

    def on_nav_change(self, current, previous):
        if current:
            key = current.data(Qt.UserRole)
            widget = self.widgets.get(key)
            if widget:
                self.stack.setCurrentWidget(widget)
                widget.refresh()
