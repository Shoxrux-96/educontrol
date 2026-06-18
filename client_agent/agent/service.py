import logging

logger = logging.getLogger(__name__)


class AgentService:
    def install(self):
        logger.info("Installing agent as Windows service...")
        try:
            import win32serviceutil
            import win32service
            import servicemanager

            win32serviceutil.InstallService(
                None,
                "EDUControlAgent",
                "EDU Control Pro Agent",
                "O'quv kompyuterlarini boshqarish agenti",
            )
            logger.info("Service installed successfully")
        except ImportError:
            logger.warning("pywin32 not available. Install on Windows only.")

    def start(self):
        logger.info("Starting agent service...")
        try:
            import win32serviceutil
            win32serviceutil.StartService("EDUControlAgent")
            logger.info("Service started")
        except ImportError:
            logger.warning("pywin32 not available.")

    def stop(self):
        logger.info("Stopping agent service...")
        try:
            import win32serviceutil
            win32serviceutil.StopService("EDUControlAgent")
            logger.info("Service stopped")
        except ImportError:
            logger.warning("pywin32 not available.")

    def remove(self):
        logger.info("Removing agent service...")
        try:
            import win32serviceutil
            win32serviceutil.RemoveService("EDUControlAgent")
            logger.info("Service removed")
        except ImportError:
            logger.warning("pywin32 not available.")
