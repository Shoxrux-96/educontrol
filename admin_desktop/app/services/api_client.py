import httpx
from typing import Optional, Dict, Any


class ApiClient:
    def __init__(self, token: str = None):
        import os
        self.base_url = os.environ.get("API_URL", "http://localhost:8002/api/v1")
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
