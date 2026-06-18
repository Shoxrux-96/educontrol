import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

config = context.config

# Override sqlalchemy.url with DATABASE_URL env var if set
db_url = os.environ.get("DATABASE_URL")
if db_url:
    # Use sync driver for migrations
    sync_url = db_url.replace("+asyncpg", "+psycopg2").replace("+asyncpg", "")
    config.set_main_option("sqlalchemy.url", sync_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.base import Base
from app.models import *

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    cfg_section = dict(config.get_section(config.config_ini_section, {}))
    # Override URL in section if set via env var
    overridden_url = config.get_main_option("sqlalchemy.url")
    if overridden_url:
        cfg_section["sqlalchemy.url"] = overridden_url
    connectable = engine_from_config(
        cfg_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
