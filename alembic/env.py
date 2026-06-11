from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from app.database import Base
from app.settings import get_settings

app_settings = get_settings()

config = context.config

DB_USER = app_settings.db_user
DB_PASS = app_settings.db_password
DB_HOST = app_settings.db_host
DB_PORT = app_settings.db_port
DB_NAME = app_settings.db_name

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASS}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

config.set_main_option("sqlalchemy.url", DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table":
        return object in target_metadata.tables.values()
    return True

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_object=include_object
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()