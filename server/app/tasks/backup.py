import logging
from datetime import timezone, datetime

from app.tasks.celery_app import celery_app
from app.utils.backup import create_backup, cleanup_old_backups

logger = logging.getLogger(__name__)


@celery_app.task
def run_backup():
    logger.info("Scheduled backup starting...")
    try:
        path = create_backup()
        logger.info(f"Backup saved to {path}")
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        raise


@celery_app.task
def cleanup_backups():
    logger.info("Old backup cleanup starting...")
    try:
        cleanup_old_backups(retention_days=7)
        logger.info("Cleanup complete")
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
