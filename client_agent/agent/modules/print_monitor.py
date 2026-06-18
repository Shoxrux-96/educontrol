import logging

logger = logging.getLogger(__name__)


class PrintMonitor:
    def __init__(self):
        self.policy = None
        self.running = False

    def apply_policy(self, policy: dict):
        self.policy = policy
        config = policy.get("config", {})
        if config.get("mode") == "block_all":
            logger.info("Printing disabled")
        else:
            logger.info("Print monitoring active")

    def stop(self):
        pass
