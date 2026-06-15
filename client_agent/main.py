import sys
import logging
from agent.service import AgentService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("agent.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def main():
    if len(sys.argv) > 1:
        action = sys.argv[1]
        service = AgentService()
        if action == "install":
            service.install()
        elif action == "start":
            service.start()
        elif action == "stop":
            service.stop()
        elif action == "remove":
            service.remove()
        else:
            print(f"Usage: {sys.argv[0]} [install|start|stop|remove]")
    else:
        logger.info("Starting Agent in console mode...")
        from agent.agent import Agent
        import asyncio
        agent = Agent()
        asyncio.run(agent.run())


if __name__ == "__main__":
    main()
