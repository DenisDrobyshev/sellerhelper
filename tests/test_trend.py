"""Tests for demand trend classification."""

from datetime import datetime, timedelta, timezone

from core.engine.demand import compute_trend


def _snaps(values):
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return [(base + timedelta(days=i), v) for i, v in enumerate(values)]


def test_growing():
    assert compute_trend(_snaps([1000, 2000])) == "growing"


def test_declining():
    assert compute_trend(_snaps([2000, 1000])) == "declining"


def test_flat():
    assert compute_trend(_snaps([1000, 1020])) == "flat"


def test_unknown_with_single_snapshot():
    assert compute_trend(_snaps([1000])) == "unknown"
