# user-service/alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# Add the project's parent directory (user-service) to the Python path
# This allows importing modules from 'src' like 'src.models' and 'src.config'
# os.path.dirname(__file__) gives 'user-service/alembic'
# os.path.dirname(os.path.dirname(__file__)) gives 'user-service'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Use abspath for robustness

# Import your SQLAlchemy Base from your models and settings from your config
from src.models import Base
from src.config import settings # Assuming settings.DATABASE_URL is defined here

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here
# for 'autogenerate' support from Alembic.
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata # This should point to your application's Base.metadata

# Other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def get_url():
    """
    Returns the database URL from the application settings.
    This function allows dynamic configuration of the database URL,
    rather than hardcoding it in alembic.ini.
    """
    return settings.DATABASE_URL

def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    In this scenario, we don't need to connect to a database directly,
    but instead, we generate SQL scripts.
    """
    url = get_url() # Get the database URL from settings
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True, # Render SQL types directly, useful for SQL script generation
        dialect_opts={"paramstyle": "named"}, # Dialect-specific options
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    In this scenario, we need to connect to the database.
    """
    # Get the Alembic configuration section for database settings
    # and override the sqlalchemy.url with the one from our application settings.
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url() # Use the dynamic URL from settings

    # Create a SQLAlchemy engine from the configuration
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.", # Prefix for SQLAlchemy related config keys in alembic.ini
        poolclass=pool.NullPool, # Use NullPool for Alembic operations as it's short-lived
    )

    # Establish a connection and run migrations within that connection's context
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata # Point to your application's Base.metadata
        )

        # Run migrations within a transaction
        with context.begin_transaction():
            context.run_migrations()

# Determine whether to run in offline or online mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()