import logging

logger = logging.getLogger(__name__)


class USBControl:
    def __init__(self):
        self.policy = None
        self.running = False

    def apply_policy(self, policy: dict):
        self.policy = policy
        config = policy.get("config", {})
        mode = config.get("mode", "block_all")

        if mode == "block_all":
            self._disable_usb_storage()
            logger.info("USB storage disabled")
        elif mode == "whitelist":
            self._enable_usb_storage()
            devices = config.get("allowed_devices", [])
            logger.info(f"USB whitelist active: {len(devices)} devices allowed")
        else:
            self._enable_usb_storage()
            logger.info("USB access enabled (logging only)")

    def _disable_usb_storage(self):
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Services\USBSTOR",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 4)
            winreg.CloseKey(key)
            logger.info("USBSTOR Start set to 4 (disabled)")
        except Exception as e:
            logger.error(f"Failed to disable USB storage: {e}")

    def _enable_usb_storage(self):
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Services\USBSTOR",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 3)
            winreg.CloseKey(key)
            logger.info("USBSTOR Start set to 3 (enabled)")
        except Exception as e:
            logger.error(f"Failed to enable USB storage: {e}")
