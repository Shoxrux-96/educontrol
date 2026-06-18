import json
import threading
import logging
import websocket

logger = logging.getLogger(__name__)


class WebSocketClient:
    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token
        self.ws = None
        self.running = False
        self.on_message_callback = None

    def connect(self):
        self.running = True
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def _run(self):
        while self.running:
            try:
                self.ws = websocket.WebSocketApp(
                    self.url,
                    header={"Authorization": f"Bearer {self.token}"},
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close,
                )
                self.ws.on_open = self._on_open
                self.ws.run_forever()
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
            import time
            time.sleep(5)

    def _on_open(self, ws):
        logger.info("WebSocket connected")

    def _on_message(self, ws, message):
        try:
            data = json.loads(message)
            if self.on_message_callback:
                self.on_message_callback(data)
        except json.JSONDecodeError:
            logger.error(f"Invalid WebSocket message: {message}")

    def _on_error(self, ws, error):
        logger.error(f"WebSocket error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        logger.info("WebSocket closed")

    def disconnect(self):
        self.running = False
        if self.ws:
            self.ws.close()
