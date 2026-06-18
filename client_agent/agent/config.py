import os


class AgentConfig:
    server_url: str = os.environ.get("SERVER_URL", "wss://localhost:8000/ws/agent")
    api_url: str = os.environ.get("API_URL", "http://localhost:8000")
    api_key: str = os.environ.get("API_KEY", "")
    agent_version: str = os.environ.get("AGENT_VERSION", "1.0.0")
    heartbeat_interval: int = 10
    reconnect_delays: list = [5, 10, 30, 60, 120]
    screenshot_interval: int = 30
    screenshot_quality: int = 70
    max_screenshot_size: tuple = (1920, 1080)
    policy_cache_file: str = "policy_cache.json"
    update_check_interval: int = 3600
    update_download_path: str = os.environ.get("UPDATE_DOWNLOAD_PATH", "educontrol_agent_update.exe")


config = AgentConfig()
