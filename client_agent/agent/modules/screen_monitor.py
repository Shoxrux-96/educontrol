import logging
import io
import base64

from agent.config import config

logger = logging.getLogger(__name__)


class ScreenMonitor:
    def __init__(self):
        self.policy = None
        self.screenshot_enabled = True

    def apply_policy(self, policy: dict):
        self.policy = policy
        config_data = policy.get("config", {})
        self.screenshot_enabled = config_data.get("enabled", True)

    def capture(self) -> str:
        if not self.screenshot_enabled:
            return None
        try:
            import mss
            from PIL import Image

            with mss.mss() as sct:
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

                max_w, max_h = config.max_screenshot_size
                if img.width > max_w or img.height > max_h:
                    img.thumbnail((max_w, max_h), Image.LANCZOS)

                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=config.screenshot_quality)
                buffer.seek(0)
                return base64.b64encode(buffer.getvalue()).decode("utf-8")
        except ImportError:
            try:
                from PIL import ImageGrab
                img = ImageGrab.grab()
                max_w, max_h = config.max_screenshot_size
                if img.width > max_w or img.height > max_h:
                    img.thumbnail((max_w, max_h), Image.LANCZOS)
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=config.screenshot_quality)
                buffer.seek(0)
                return base64.b64encode(buffer.getvalue()).decode("utf-8")
            except Exception as e:
                logger.error(f"Screenshot failed: {e}")
                return None
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None
