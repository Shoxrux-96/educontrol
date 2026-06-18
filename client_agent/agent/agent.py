import asyncio
import json
import uuid
import logging
import platform
import socket
import os
import hashlib

import httpx
import websockets
import psutil

from agent.config import config
from agent.modules.internet_control import InternetControl
from agent.modules.app_control import AppControl
from agent.modules.usb_control import USBControl
from agent.modules.screen_monitor import ScreenMonitor
from agent.modules.system_monitor import SystemMonitor
from agent.policy_engine import PolicyEngine

logger = logging.getLogger(__name__)


class Agent:
    def __init__(self):
        self.agent_id = str(uuid.uuid4())
        self.ws = None
        self.running = True
        self.modules = {}
        self.policy_engine = PolicyEngine()
        self.system_monitor = SystemMonitor()
        self._init_modules()

    def _init_modules(self):
        self.modules["internet"] = InternetControl()
        self.modules["app_control"] = AppControl()
        self.modules["usb"] = USBControl()
        self.modules["screen"] = ScreenMonitor()

    def _get_system_info(self) -> dict:
        hostname = socket.gethostname()
        try:
            ip = socket.gethostbyname(hostname)
        except Exception:
            ip = "0.0.0.0"
        try:
            import uuid as uuid_mod
            mac = ":".join(
                f"{(uuid_mod.getnode() >> bits) & 0xFF:02x}"
                for bits in range(0, 48, 8)
            )
        except Exception:
            mac = "00:00:00:00:00:00"

        return {
            "agent_id": self.agent_id,
            "hostname": hostname,
            "ip": ip,
            "mac": mac,
            "os": platform.platform(),
            "agent_version": config.agent_version,
        }

    async def connect(self):
        reconnect_idx = 0
        while self.running:
            try:
                logger.info(f"Connecting to {config.server_url}...")
                self.ws = await websockets.connect(config.server_url)
                logger.info("Connected to server")

                system_info = self._get_system_info()
                await self.ws.send(json.dumps({"type": "register", **system_info}))

                reconnect_idx = 0
                await self._handle_messages()
            except (websockets.ConnectionClosed, ConnectionRefusedError, OSError) as e:
                logger.warning(f"Connection failed: {e}")
                delay = config.reconnect_delays[
                    min(reconnect_idx, len(config.reconnect_delays) - 1)
                ]
                logger.info(f"Reconnecting in {delay}s...")
                await asyncio.sleep(delay)
                reconnect_idx += 1

    async def _handle_messages(self):
        async def heartbeat():
            while self.running:
                await asyncio.sleep(config.heartbeat_interval)
                if self.ws and self.ws.open:
                    stats = self.system_monitor.get_stats()
                    try:
                        await self.ws.send(json.dumps({
                            "type": "heartbeat",
                            "agent_id": self.agent_id,
                            **stats,
                        }))
                    except Exception:
                        break

        async def screenshot_loop():
            while self.running:
                await asyncio.sleep(config.screenshot_interval)
                if self.ws and self.ws.open:
                    screen = self.modules["screen"]
                    try:
                        img_data = screen.capture()
                        if img_data:
                            await self.ws.send(json.dumps({
                                "type": "screenshot",
                                "agent_id": self.agent_id,
                                "image": img_data,
                            }))
                    except Exception:
                        pass

        asyncio.create_task(heartbeat())
        asyncio.create_task(screenshot_loop())

        async for message in self.ws:
            try:
                data = json.loads(message)
                await self._process_server_message(data)
            except json.JSONDecodeError:
                logger.error(f"Invalid message from server: {message}")

    async def _process_server_message(self, data: dict):
        msg_type = data.get("type")

        if msg_type == "command":
            await self._execute_command(data)
        elif msg_type == "policy_update":
            policies = data.get("policies", [])
            self.policy_engine.update(policies)
            for p in policies:
                module = self.modules.get(p.get("type"))
                if module:
                    module.apply_policy(p)
            await self._send_event("policy_updated", {"count": len(policies)})
        elif msg_type == "message":
            logger.info(f"Message from server: {data.get('title', '')} - {data.get('body', '')}")
            self._show_notification(data)

    async def _execute_command(self, command: dict):
        command_id = command.get("command_id")
        action = command.get("action")
        payload = command.get("payload", {})

        try:
            if action == "lock_screen":
                self._lock_screen()
                result = {"success": True}
            elif action == "unlock_screen":
                self._unlock_screen()
                result = {"success": True}
            elif action == "take_screenshot":
                img = self.modules["screen"].capture()
                result = {"success": True, "image": img}
            elif action == "send_message":
                self._show_notification(command)
                result = {"success": True}
            elif action == "restart":
                import os
                os.system("shutdown /r /t 10")
                result = {"success": True}
            elif action == "shutdown":
                import os
                os.system("shutdown /s /t 10")
                result = {"success": True}
            elif action == "kill_process":
                result = self._kill_process(payload.get("process_name"))
            elif action == "open_app":
                result = self._open_app(payload.get("exe_path"))
            else:
                result = {"success": False, "error": f"Unknown action: {action}"}

            if self.ws and self.ws.open:
                await self.ws.send(json.dumps({
                    "type": "command_result",
                    "agent_id": self.agent_id,
                    "command_id": command_id,
                    **result,
                }))
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            if self.ws and self.ws.open:
                await self.ws.send(json.dumps({
                    "type": "command_result",
                    "agent_id": self.agent_id,
                    "command_id": command_id,
                    "success": False,
                    "error": str(e),
                }))

    async def _send_event(self, event: str, details: dict = None):
        if self.ws and self.ws.open:
            await self.ws.send(json.dumps({
                "type": "event",
                "agent_id": self.agent_id,
                "event": event,
                "details": details or {},
            }))

    def _lock_screen(self):
        try:
            import ctypes
            ctypes.windll.user32.LockWorkStation()
        except Exception as e:
            logger.error(f"Lock screen failed: {e}")

    def _unlock_screen(self):
        logger.info("Unlock screen requested (requires Windows API)")

    def _show_notification(self, data: dict):
        title = data.get("title", "Notification")
        body = data.get("body", "")
        severity = data.get("severity", "info")
        logger.info(f"[{severity.upper()}] {title}: {body}")

    def _kill_process(self, process_name: str):
        if not process_name:
            return {"success": False, "error": "process_name required"}
        try:
            for proc in psutil.process_iter(["pid", "name"]):
                if proc.info["name"] and process_name.lower() in proc.info["name"].lower():
                    proc.kill()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _open_app(self, exe_path: str):
        if not exe_path:
            return {"success": False, "error": "exe_path required"}
        try:
            import subprocess
            subprocess.Popen(exe_path)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def check_for_updates(self):
        while self.running:
            try:
                url = f"{config.api_url}/api/v1/agent-updates/check"
                params = {
                    "current_version": config.agent_version,
                    "platform": "windows",
                    "arch": "x86_64",
                }
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.get(url, params=params)
                    if resp.status_code != 200:
                        await asyncio.sleep(config.update_check_interval)
                        continue
                    data = resp.json()
                    if data.get("update_available"):
                        build = data["build"]
                        logger.info(
                            f"Update available: v{build['version']} "
                            f"(current: v{config.agent_version})"
                        )
                        await self.download_update(build)
            except Exception as e:
                logger.debug(f"Update check failed: {e}")
            await asyncio.sleep(config.update_check_interval)

    async def download_update(self, build: dict):
        try:
            url = f"{config.api_url}/api/v1/agent-updates/download/{build['id']}"
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.get(url)
                if resp.status_code != 200:
                    logger.error(f"Download failed: {resp.status_code}")
                    return
                content = resp.content

            actual = hashlib.sha256(content).hexdigest()
            expected = build["checksum_sha256"]
            if actual != expected:
                logger.error(f"Checksum mismatch: expected {expected}, got {actual}")
                return

            with open(config.update_download_path, "wb") as f:
                f.write(content)
            logger.info(
                f"Update downloaded to {config.update_download_path} "
                f"({len(content)} bytes)"
            )

            self._apply_update()
        except Exception as e:
            logger.error(f"Update download failed: {e}")

    def _apply_update(self):
        logger.info("Update ready: restart agent to apply")
        if os.name == "nt":
            updater_script = (
                '@echo off\n'
                'timeout /t 3 /nobreak >nul\n'
                f'copy /Y "{config.update_download_path}" "%~dp0educontrol_agent.exe"\n'
                'start "" "%~dp0educontrol_agent.exe"\n'
                'del "%~dp0educontrol_agent.exe.update"\n'
            )
            updater_path = "update_agent.bat"
            with open(updater_path, "w") as f:
                f.write(updater_script)
            logger.info(f"Updater script created: {updater_path}")

    async def run(self):
        asyncio.create_task(self.check_for_updates())
        await self.connect()
