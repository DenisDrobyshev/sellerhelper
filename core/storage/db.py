"""Database engine + schema bootstrap."""

from functools import lru_cache

from sqlalchemy import Engine, create_engine

from core.config import get_settings
from core.storage.models import Base


@lru_cache
def get_engine() -> Engine:
    """Return the process-wide engine, creating tables on first use."""
    engine = create_engine(get_settings().database_url, future=True)
    Base.metadata.create_all(engine)
    return engine
