import logging
import psutil

logger = logging.getLogger(__name__)


class AppControl:
    def __init__(self):
        self.policy = None
        self.running = False

    def apply_policy(self, policy: dict):
        self.policy = policy
        config = policy.get("config", {})
        mode = config.get("mode", "whitelist")
        logger.info(f"Application control active: {mode} mode")

    def check_process(self, process_name: str, process_path: str = None) -> bool:
        if not self.policy:
            return True

        config = self.policy.get("config", {})
        mode = config.get("mode", "whitelist")

        if mode == "whitelist":
            allowed = config.get("allowed_apps", [])
            for app in allowed:
                if app.get("name", "").lower() in process_name.lower():
                    return True
            return False
        elif mode == "blacklist":
            blocked = config.get("blocked_apps", [])
            for app in blocked:
                if app.get("name", "").lower() in process_name.lower():
                    return False
            return True

        return True

    def monitor_processes(self):
        if not self.policy:
            return

        config = self.policy.get("config", {})
        if not config.get("kill_on_detect", False):
            return

        for proc in psutil.process_iter(["name", "exe"]):
            try:
                name = proc.info["name"]
                exe = proc.info["exe"]
                if name and not self.check_process(name, exe):
                    logger.warning(f"Killing blocked process: {name}")
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
