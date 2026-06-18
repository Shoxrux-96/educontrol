import PyInstaller.__main__
import os

admin_dir = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    "--name=EduControlAdmin",
    "--onefile",
    "--windowed",
    "--clean",
    "--add-data", f"{admin_dir}/app{os.pathsep}app",
    "--paths", admin_dir,
    "--hidden-import", "app.services.api_client",
    "--hidden-import", "app.services.ws_client",
    "--hidden-import", "app.windows.login_window",
    "--hidden-import", "app.windows.main_window",
    "--hidden-import", "app.widgets.dashboard_widget",
    "--hidden-import", "app.widgets.computer_list_widget",
    "--hidden-import", "app.widgets.screen_monitor_widget",
    "--hidden-import", "app.widgets.policy_widget",
    "--hidden-import", "app.widgets.audit_widget",
    "--hidden-import", "app.widgets.report_widget",
    "--hidden-import", "PySide6",
    "--hidden-import", "httpx",
    "--hidden-import", "websocket",
    "--hidden-import", "Pillow",
    os.path.join(admin_dir, "main.py"),
])
