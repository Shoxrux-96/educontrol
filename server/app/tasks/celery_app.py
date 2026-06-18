from celery import Celery
from app.config import settings

celery_app = Celery(
    "educontrol",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.reports", "app.tasks.cleanup", "app.tasks.backup"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    beat_schedule={
        "backup-daily": {
            "task": "app.tasks.backup.run_backup",
            "schedule": 86400.0,
            "args": (),
        },
        "cleanup-old-backups": {
            "task": "app.tasks.backup.cleanup_backups",
            "schedule": 86400.0,
            "args": (),
        },
    },
)
