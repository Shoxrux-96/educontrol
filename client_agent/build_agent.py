import PyInstaller.__main__
import os
import sys

agent_dir = os.path.dirname(os.path.abspath(__file__))
venv_site = os.path.join(agent_dir, "venv", "Lib", "site-packages")

PyInstaller.__main__.run([
    "--name=educontrol_agent",
    "--onefile",
    "--console",
    "--clean",
    "--add-data", f"{agent_dir}/agent{os.pathsep}agent",
    "--paths", agent_dir,
    "--paths", venv_site,
    "--hidden-import", "agent.modules.internet_control",
    "--hidden-import", "agent.modules.app_control",
    "--hidden-import", "agent.modules.usb_control",
    "--hidden-import", "agent.modules.screen_monitor",
    "--hidden-import", "agent.modules.system_monitor",
    "--hidden-import", "agent.modules.print_monitor",
    "--hidden-import", "agent.policy_engine",
    "--hidden-import", "agent.service",
    "--hidden-import", "agent.config",
    "--hidden-import", "websockets",
    "--hidden-import", "httpx",
    "--hidden-import", "psutil",
    "--hidden-import", "mss",
    os.path.join(agent_dir, "main.py"),
])
