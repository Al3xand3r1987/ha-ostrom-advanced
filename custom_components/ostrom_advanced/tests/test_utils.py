from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from custom_components.ostrom_advanced.utils import calculate_next_update_time
from custom_components.ostrom_advanced import utils


def test_calculate_next_update_time_next_interval(monkeypatch) -> None:
    """Ensure the next update is aligned to the current interval with offset."""
    now = datetime(2024, 1, 1, 10, 7, 30, tzinfo=timezone.utc)
    monkeypatch.setattr(utils.dt_util, "now", lambda: now)

    result = calculate_next_update_time(interval_minutes=15, offset_seconds=15)

    expected = now.replace(minute=15, second=15, microsecond=0)
    assert result == expected


def test_calculate_next_update_time_fallback_invalid_offset(
    monkeypatch, caplog
) -> None:
    """Fallback is used when offset is invalid for datetime.replace."""
    now = datetime(2024, 1, 1, 10, 7, 30, tzinfo=timezone.utc)
    monkeypatch.setattr(utils.dt_util, "now", lambda: now)

    with caplog.at_level(logging.ERROR):
        result = calculate_next_update_time(interval_minutes=15, offset_seconds=75)

    expected = now + timedelta(minutes=15, seconds=75)
    assert result == expected
    assert "Time calculation error" in caplog.text
