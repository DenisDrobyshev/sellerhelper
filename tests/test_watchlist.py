"""Tests for the collection watchlist and scheduler — no network."""

from sqlalchemy import create_engine

from core.scheduler import collect_once
from core.storage.models import Base
from core.storage.repo import add_watch, list_watch, remove_watch


def _engine(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'w.db'}")
    Base.metadata.create_all(engine)
    return engine


def test_add_list_remove(tmp_path):
    engine = _engine(tmp_path)
    assert add_watch("термокружка", engine=engine) is True
    assert add_watch("термокружка", engine=engine) is False   # duplicate ignored
    assert add_watch("ланчбокс", engine=engine) is True
    assert list_watch(engine=engine) == ["ланчбокс", "термокружка"]  # sorted
    assert remove_watch("ланчбокс", engine=engine) is True
    assert remove_watch("ланчбокс", engine=engine) is False
    assert list_watch(engine=engine) == ["термокружка"]


def test_collect_once_with_empty_list_does_nothing():
    assert collect_once([]) == {}
