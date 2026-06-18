import json
import asyncio
import logging
from typing import Dict, Optional
from fastapi import WebSocket
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ConnectionInfo:
    def __init__(self, websocket: WebSocket, agent_id: str, computer_id: str):
        self.websocket = websocket
        self.agent_id = agent_id
        self.computer_id = computer_id
        self.connected_at = datetime.now(timezone.utc)
        self.last_heartbeat = datetime.now(timezone.utc)


class WebSocketManager:
    def __init__(self):
        self.connections: Dict[str, ConnectionInfo] = {}  # agent_id -> ConnectionInfo
        self.computer_connections: Dict[str, str] = {}  # computer_id -> agent_id

    async def connect(self, websocket: WebSocket, agent_id: str, computer_id: str):
        await websocket.accept()
        self.connections[agent_id] = ConnectionInfo(websocket, agent_id, computer_id)
        self.computer_connections[computer_id] = agent_id
        logger.info(f"Agent {agent_id} (computer {computer_id}) connected. Total: {len(self.connections)}")

    async def disconnect(self, agent_id: str):
        info = self.connections.pop(agent_id, None)
        if info:
            self.computer_connections.pop(info.computer_id, None)
            logger.info(f"Agent {agent_id} disconnected. Total: {len(self.connections)}")

    def get_connection(self, agent_id: str) -> Optional[ConnectionInfo]:
        return self.connections.get(agent_id)

    def get_connection_by_computer(self, computer_id: str) -> Optional[ConnectionInfo]:
        agent_id = self.computer_connections.get(computer_id)
        if agent_id:
            return self.connections.get(agent_id)
        return None

    async def send_to_agent(self, agent_id: str, message: dict):
        info = self.connections.get(agent_id)
        if info:
            try:
                await info.websocket.send_json(message)
                return True
            except Exception as e:
                logger.error(f"Error sending to agent {agent_id}: {e}")
                await self.disconnect(agent_id)
        return False

    async def send_to_computer(self, computer_id: str, message: dict) -> bool:
        info = self.get_connection_by_computer(computer_id)
        if info:
            return await self.send_to_agent(info.agent_id, message)
        return False

    async def send_to_group(self, group_computer_ids: list, message: dict):
        results = []
        for cid in group_computer_ids:
            result = await self.send_to_computer(cid, message)
            results.append(result)
        return results

    async def broadcast(self, message: dict):
        disconnected = []
        for agent_id, info in self.connections.items():
            try:
                await info.websocket.send_json(message)
            except Exception:
                disconnected.append(agent_id)
        for agent_id in disconnected:
            await self.disconnect(agent_id)

    def update_heartbeat(self, agent_id: str):
        info = self.connections.get(agent_id)
        if info:
            info.last_heartbeat = datetime.now(timezone.utc)

    async def check_stale_connections(self, timeout_seconds: int = 60):
        now = datetime.now(timezone.utc)
        stale = [
            agent_id
            for agent_id, info in self.connections.items()
            if (now - info.last_heartbeat).total_seconds() > timeout_seconds
        ]
        for agent_id in stale:
            logger.warning(f"Agent {agent_id} stale, disconnecting")
            await self.disconnect(agent_id)

    @property
    def active_connections(self) -> int:
        return len(self.connections)


manager = WebSocketManager()
