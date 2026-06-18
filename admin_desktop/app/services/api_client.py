import httpx
import hashlib
import logging
import os
import subprocess
import sys
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ApiClient:
    def __init__(self, token: str = None):
        self.base_url = os.environ.get("API_URL", "http://localhost:8000/api/v1")
        self.token = token
        self.client = httpx.Client(timeout=30)

    def _headers(self) -> dict:
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def login(self, username: str, password: str) -> dict:
        resp = self.client.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password},
        )
        resp.raise_for_status()
        return resp.json()

    def get(self, endpoint: str, params: dict = None) -> Any:
        resp = self.client.get(
            f"{self.base_url}/{endpoint}",
            headers=self._headers(),
            params=params,
        )
        resp.raise_for_status()
        if resp.status_code == 204:
            return None
        return resp.json()

    def post(self, endpoint: str, data: dict = None) -> Any:
        resp = self.client.post(
            f"{self.base_url}/{endpoint}",
            headers=self._headers(),
            json=data or {},
        )
        resp.raise_for_status()
        if resp.status_code == 204:
            return None
        return resp.json()

    def put(self, endpoint: str, data: dict = None) -> Any:
        resp = self.client.put(
            f"{self.base_url}/{endpoint}",
            headers=self._headers(),
            json=data or {},
        )
        resp.raise_for_status()
        if resp.status_code == 204:
            return None
        return resp.json()

    def delete(self, endpoint: str) -> None:
        resp = self.client.delete(
            f"{self.base_url}/{endpoint}",
            headers=self._headers(),
        )
        resp.raise_for_status()

    def check_update(self, current_version: str) -> Optional[dict]:
        try:
            resp = self.client.get(
                f"{self.base_url}/agent-updates/check",
                params={"current_version": current_version, "platform": "windows", "arch": "x86_64"},
                timeout=10,
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            if data.get("update_available"):
                return data["build"]
        except Exception as e:
            logger.warning(f"Update check failed: {e}")
        return None

    def download_update(self, build: dict, dest_path: str) -> bool:
        try:
            resp = self.client.get(
                f"{self.base_url}/agent-updates/download/{build['id']}",
                timeout=120,
            )
            if resp.status_code != 200:
                logger.error(f"Download failed: {resp.status_code}")
                return False
            actual = hashlib.sha256(resp.content).hexdigest()
            expected = build["checksum_sha256"]
            if actual != expected:
                logger.error(f"Checksum mismatch")
                return False
            with open(dest_path, "wb") as f:
                f.write(resp.content)
            logger.info(f"Update downloaded to {dest_path}")
            return True
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False

    def apply_update(self, update_path: str, current_exe: str):
        if getattr(sys, 'frozen', False):
            updater = (
                f'@timeout /t 2 /nobreak >nul\n'
                f'@copy /Y "{update_path}" "{current_exe}"\n'
                f'@start "" "{current_exe}"\n'
                f'@del "{update_path}"\n'
            )
            updater_path = os.path.join(os.path.dirname(current_exe), "update_admin.bat")
            with open(updater_path, "w") as f:
                f.write(updater)
            subprocess.Popen(["cmd", "/c", updater_path], shell=True)
            sys.exit(0)
