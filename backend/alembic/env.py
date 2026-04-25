import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Make sure `app` package is importable when running alembic from backend/.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Set SECRET_KEY so pydantic-settings doesn't fail on import.
os.environ.setdefault("SECRET_KEY", "alembic-placeholder-not-used-for-signing")

from app.config import settings
from app.database import Base

# Import all models so Alembic can detect them for autogenerate.
import app.models.user       # noqa: F401
import app.models.partner    # noqa: F401
import app.models.package    # noqa: F401
import app.models.booking    # noqa: F401
import app.models.trip       # noqa: F401
import app.models.social     # noqa: F401
import app.models.travel_request  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Override sqlalchemy.url with the value from .env (avoids hardcoding in alembic.ini).
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
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
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
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
