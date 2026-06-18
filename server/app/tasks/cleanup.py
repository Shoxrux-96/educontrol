import os
import shutil
from datetime import datetime, timedelta, timezone
from app.tasks.celery_app import celery_app
from app.config import settings


@celery_app.task
def cleanup_old_screenshots():
    retention_days = settings.screenshots_retention_days
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    screenshots_path = settings.screenshots_path

    if not os.path.exists(screenshots_path):
        return {"deleted": 0, "message": "Screenshots directory not found"}

    deleted_count = 0
    for year_dir in os.listdir(screenshots_path):
        year_path = os.path.join(screenshots_path, year_dir)
        if not os.path.isdir(year_path):
            continue
        for month_dir in os.listdir(year_path):
            month_path = os.path.join(year_path, month_dir)
            if not os.path.isdir(month_path):
                continue
            for day_dir in os.listdir(month_path):
                day_path = os.path.join(month_path, day_dir)
                if not os.path.isdir(day_path):
                    continue
                try:
                    dir_date = datetime(
                        int(year_dir), int(month_dir), int(day_dir), tzinfo=timezone.utc
                    )
                    if dir_date < cutoff:
                        shutil.rmtree(day_path)
                        deleted_count += 1
                except (ValueError, OSError):
                    continue

    return {"deleted": deleted_count, "cutoff_date": cutoff.isoformat()}


@celery_app.task
def cleanup_old_commands():
    from sqlalchemy import create_engine, text

    db_url = settings.database_url.replace("+asyncpg", "")
    engine = create_engine(db_url)
    cutoff = datetime.now(timezone.utc) - timedelta(days=90)

    with engine.connect() as conn:
        result = conn.execute(
            text("DELETE FROM commands WHERE sent_at < :cutoff"),
            {"cutoff": cutoff},
        )
        conn.commit()
        return {"deleted_commands": result.rowcount}
