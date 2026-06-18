import logging
import threading

logger = logging.getLogger(__name__)


class InternetControl:
    def __init__(self):
        self.policy = None
        self.running = False
        self._proxy_thread = None

    def apply_policy(self, policy: dict):
        self.policy = policy
        config = policy.get("config", {})
        mode = config.get("mode", "whitelist")

        if mode == "whitelist":
            allowed = config.get("allowed_domains", [])
            logger.info(f"Internet whitelist active: {len(allowed)} domains allowed")
            self._setup_proxy()
        elif mode == "blacklist":
            blocked = config.get("blocked_domains", [])
            logger.info(f"Internet blacklist active: {len(blocked)} domains blocked")
            self._setup_proxy()
        elif mode == "block_all":
            logger.info("Internet access blocked")
            self._disable_network()

    def _setup_proxy(self):
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, "127.0.0.1:8877")
            winreg.CloseKey(key)
            logger.info("HTTP proxy configured on port 8877")
        except Exception as e:
            logger.error(f"Failed to setup proxy: {e}")

    def _disable_network(self):
        try:
            import subprocess
            subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "disable"],
                         capture_output=True)
            logger.info("Network interface disabled")
        except Exception as e:
            logger.error(f"Failed to disable network: {e}")

    def stop(self):
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
        except Exception:
            pass
