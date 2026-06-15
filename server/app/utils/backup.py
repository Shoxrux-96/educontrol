import os
import shutil
import subprocess
import logging
from datetime import datetime, timezone
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


def create_backup() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(settings.backup_path) / f"backup_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    db_url = settings.database_url
    db_name = db_url.split("/")[-1]
    db_user = db_url.split("://")[1].split(":")[0]
    db_pass = db_url.split(":")[2].split("@")[0]
    db_host = db_url.split("@")[1].split(":")[0]
    db_port = db_url.split("@")[1].split(":")[1].split("/")[0]

    dump_file = backup_dir / "database.sql"
    env = os.environ.copy()
    env["PGPASSWORD"] = db_pass
    subprocess.run(
        ["pg_dump", "-h", db_host, "-p", db_port, "-U", db_user, "-d", db_name, "-f", str(dump_file)],
        env=env,
        check=True,
    )
    logger.info(f"Database backup: {dump_file}")

    screenshots = Path(settings.screenshots_path)
    if screenshots.exists():
        shutil.copytree(screenshots, backup_dir / "screenshots")
        logger.info(f"Screenshots backed up")

    backup_size = sum(
        f.stat().st_size for f in backup_dir.rglob("*") if f.is_file()
    )
    logger.info(f"Backup complete: {backup_dir} ({backup_size / 1024 / 1024:.1f} MB)")

    return str(backup_dir)


def cleanup_old_backups(retention_days: int = 7):
    backup_path = Path(settings.backup_path)
    if not backup_path.exists():
        return
    cutoff = datetime.now(timezone.utc).timestamp() - retention_days * 86400
    for item in backup_path.iterdir():
        if item.is_dir() and item.name.startswith("backup_"):
            ctime = item.stat().st_ctime
            if ctime < cutoff:
                shutil.rmtree(item)
                logger.info(f"Removed old backup: {item}")
