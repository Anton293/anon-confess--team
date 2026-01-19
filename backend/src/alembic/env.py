"""
Alembic migration environment setup file.
This file is responsible for configuring the Alembic context.

Includes:
- Setting up the database connection using SQLAlchemy.
- Importing the ORM models' metadata for migrations.
"""

from logging.config import fileConfig
import sys
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context


# Path setup to include src module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


from src.db.postgres import Base  # ORM DDL.
from src.core.config import settings # Application settings
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

config.set_main_option("sqlalchemy.url", settings.database_url.replace("postgresql+psycopg_async", "postgresql+psycopg"))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    
    # Створюємо engine, використовуючи конфігурацію
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()