import asyncio
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db, init_db
from app.routers import auth, computers, policies, commands, audit, reports, messages, monitoring, agent_updates
from app.websocket.manager import manager
from app.websocket.handlers import handle_agent_message
from app.services.monitor_service import monitor_service
from app.services.alert_service import alert_service

logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting EDU Control Pro server...")
    await init_db()
    cleanup_task = asyncio.create_task(periodic_cleanup())
    alert_task = asyncio.create_task(alert_monitor_loop())
    logger.info("Background tasks started")
    yield
    cleanup_task.cancel()
    alert_task.cancel()
    logger.info("Shutting down EDU Control Pro server...")


async def periodic_cleanup():
    while True:
        await asyncio.sleep(30)
        await manager.check_stale_connections(120)


async def alert_monitor_loop():
    while True:
        try:
            server = monitor_service.get_server_stats()
            metrics = {
                "cpu_percent": server.cpu_percent,
                "ram_percent": server.ram_percent,
                "disk_percent": server.disk_percent,
                "uptime_seconds": server.uptime_seconds,
                "agents_connected": manager.active_connections,
            }
            triggered = alert_service.check_rules(metrics)
            if triggered:
                logger.warning(f"{len(triggered)} alert(s) triggered")
        except Exception as e:
            logger.error(f"Alert monitoring error: {e}")
        await asyncio.sleep(30)


app = FastAPI(
    title="EDU Control Pro API",
    description="O'quv markazlari uchun kompyuterlarni markazlashtirilgan boshqarish tizimi",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(computers.router)
app.include_router(policies.router)
app.include_router(commands.router)
app.include_router(audit.router)
app.include_router(reports.router)
app.include_router(messages.router)
app.include_router(monitoring.router)
app.include_router(agent_updates.router)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "agents_connected": manager.active_connections,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.websocket("/ws/agent")
async def agent_websocket(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    await websocket.accept()
    agent_id = None
    try:
        while True:
            data = await websocket.receive_json()
            agent_id = data.get("agent_id", agent_id)
            await handle_agent_message(websocket, data, db)
    except WebSocketDisconnect:
        if agent_id:
            await manager.disconnect(agent_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if agent_id:
            await manager.disconnect(agent_id)
