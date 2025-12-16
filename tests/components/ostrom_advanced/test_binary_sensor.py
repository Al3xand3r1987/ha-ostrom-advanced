"""Tests for binary sensor functions."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from homeassistant.util import dt as dt_util

from custom_components.ostrom_advanced.binary_sensor import (
    _get_cheapest_3h_block,
    _get_cheapest_4h_block,
    _is_cheapest_3h_block_active,
    _is_cheapest_4h_block_active,
    _is_today_cheapest_3h_block_active,
    _is_today_cheapest_4h_block_active,
    _is_tomorrow_cheapest_3h_block_active,
)


class TestGetCheapest3hBlock:
    """Tests for _get_cheapest_3h_block function."""

    def test_cheapest_3h_block_normal_case(self) -> None:
        """Test cheapest 3h block with normal price list."""
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        slots = [
            {"total_price": 0.30, "start": start_time},  # Block 1: avg 0.25
            {"total_price": 0.20, "start": start_time.replace(hour=11)},
            {"total_price": 0.25, "start": start_time.replace(hour=12)},
            {"total_price": 0.10, "start": start_time.replace(hour=13)},  # Block 2: avg 0.15 (cheapest)
            {"total_price": 0.15, "start": start_time.replace(hour=14)},
            {"total_price": 0.20, "start": start_time.replace(hour=15)},
        ]
        result = _get_cheapest_3h_block(slots)
        assert result == start_time.replace(hour=13)

    def test_cheapest_3h_block_less_than_3_slots(self) -> None:
        """Test cheapest 3h block with less than 3 slots."""
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        slots = [
            {"total_price": 0.30, "start": start_time},
            {"total_price": 0.20, "start": start_time.replace(hour=11)},
        ]
        result = _get_cheapest_3h_block(slots)
        assert result is None

    def test_cheapest_3h_block_exactly_3_slots(self) -> None:
        """Test cheapest 3h block with exactly 3 slots."""
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        slots = [
            {"total_price": 0.30, "start": start_time},
            {"total_price": 0.20, "start": start_time.replace(hour=11)},
            {"total_price": 0.25, "start": start_time.replace(hour=12)},
        ]
        result = _get_cheapest_3h_block(slots)
        assert result == start_time


class TestGetCheapest4hBlock:
    """Tests for _get_cheapest_4h_block function."""

    def test_cheapest_4h_block_normal_case(self) -> None:
        """Test cheapest 4h block with normal price list."""
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        slots = [
            {"total_price": 0.30, "start": start_time},  # Block 1: avg 0.25
            {"total_price": 0.20, "start": start_time.replace(hour=11)},
            {"total_price": 0.25, "start": start_time.replace(hour=12)},
            {"total_price": 0.25, "start": start_time.replace(hour=13)},
            {"total_price": 0.10, "start": start_time.replace(hour=14)},  # Block 2: avg 0.15 (cheapest)
            {"total_price": 0.15, "start": start_time.replace(hour=15)},
            {"total_price": 0.20, "start": start_time.replace(hour=16)},
            {"total_price": 0.15, "start": start_time.replace(hour=17)},
        ]
        result = _get_cheapest_4h_block(slots)
        assert result == start_time.replace(hour=14)

    def test_cheapest_4h_block_less_than_4_slots(self) -> None:
        """Test cheapest 4h block with less than 4 slots."""
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        slots = [
            {"total_price": 0.30, "start": start_time},
            {"total_price": 0.20, "start": start_time.replace(hour=11)},
            {"total_price": 0.25, "start": start_time.replace(hour=12)},
        ]
        result = _get_cheapest_4h_block(slots)
        assert result is None


class TestIsCheapest3hBlockActive:
    """Tests for _is_cheapest_3h_block_active function."""

    def test_block_active_current_time_in_block(self) -> None:
        """Test when current time is within the cheapest block."""
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        now = start_time + timedelta(hours=1)  # Within block
        slots = [
            {"total_price": 0.10, "start": start_time},  # Cheapest block
            {"total_price": 0.20, "start": start_time.replace(hour=11)},
            {"total_price": 0.15, "start": start_time.replace(hour=12)},
        ]
        is_active, block_start, block_end = _is_cheapest_3h_block_active(slots, now)
        assert is_active is True
        assert block_start == start_time
        assert block_end == start_time + timedelta(hours=3)

    def test_block_active_current_time_before_block(self) -> None:
        """Test when current time is before the cheapest block."""
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        now = start_time - timedelta(hours=1)  # Before block
        slots = [
            {"total_price": 0.10, "start": start_time},  # Cheapest block
            {"total_price": 0.20, "start": start_time.replace(hour=11)},
            {"total_price": 0.15, "start": start_time.replace(hour=12)},
        ]
        is_active, block_start, block_end = _is_cheapest_3h_block_active(slots, now)
        assert is_active is False
        assert block_start == start_time

    def test_block_active_current_time_after_block(self) -> None:
        """Test when current time is after the cheapest block."""
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        now = start_time + timedelta(hours=4)  # After block
        slots = [
            {"total_price": 0.10, "start": start_time},  # Cheapest block
            {"total_price": 0.20, "start": start_time.replace(hour=11)},
            {"total_price": 0.15, "start": start_time.replace(hour=12)},
        ]
        is_active, block_start, block_end = _is_cheapest_3h_block_active(slots, now)
        assert is_active is False
        assert block_start == start_time

    def test_block_active_no_blocks_available(self) -> None:
        """Test when no blocks are available."""
        now = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        slots = [
            {"total_price": 0.10, "start": now},
            {"total_price": 0.20, "start": now.replace(hour=11)},
        ]  # Less than 3 slots
        is_active, block_start, block_end = _is_cheapest_3h_block_active(slots, now)
        assert is_active is False
        assert block_start is None
        assert block_end is None


class TestIsCheapest4hBlockActive:
    """Tests for _is_cheapest_4h_block_active function."""

    def test_block_active_current_time_in_block(self) -> None:
        """Test when current time is within the cheapest 4h block."""
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        now = start_time + timedelta(hours=2)  # Within block
        slots = [
            {"total_price": 0.10, "start": start_time},  # Cheapest block
            {"total_price": 0.20, "start": start_time.replace(hour=11)},
            {"total_price": 0.15, "start": start_time.replace(hour=12)},
            {"total_price": 0.12, "start": start_time.replace(hour=13)},
        ]
        is_active, block_start, block_end = _is_cheapest_4h_block_active(slots, now)
        assert is_active is True
        assert block_start == start_time
        assert block_end == start_time + timedelta(hours=4)


class TestIsTodayCheapest3hBlockActive:
    """Tests for _is_today_cheapest_3h_block_active function."""

    def test_today_block_active(self) -> None:
        """Test today's cheapest 3h block active check."""
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        now = start_time + timedelta(hours=1)

        with patch("custom_components.ostrom_advanced.binary_sensor.dt_util.now", return_value=now):
            data = {
                "today_slots": [
                    {"total_price": 0.10, "start": start_time},
                    {"total_price": 0.20, "start": start_time.replace(hour=11)},
                    {"total_price": 0.15, "start": start_time.replace(hour=12)},
                ]
            }
            is_active, attrs = _is_today_cheapest_3h_block_active(data)
            assert is_active is True
            assert attrs is not None
            assert "block_start" in attrs
            assert "block_end" in attrs

    def test_today_block_inactive(self) -> None:
        """Test today's cheapest 3h block inactive check."""
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        now = start_time - timedelta(hours=1)  # Before block

        with patch("custom_components.ostrom_advanced.binary_sensor.dt_util.now", return_value=now):
            data = {
                "today_slots": [
                    {"total_price": 0.10, "start": start_time},
                    {"total_price": 0.20, "start": start_time.replace(hour=11)},
                    {"total_price": 0.15, "start": start_time.replace(hour=12)},
                ]
            }
            is_active, attrs = _is_today_cheapest_3h_block_active(data)
            assert is_active is False
            assert attrs is not None  # Attributes should still be returned


class TestIsTomorrowCheapest3hBlockActive:
    """Tests for _is_tomorrow_cheapest_3h_block_active function."""

    def test_tomorrow_block_not_active_before_midnight(self) -> None:
        """Test tomorrow's block when still today."""
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        now = start_time  # Still today

        with patch("custom_components.ostrom_advanced.binary_sensor.dt_util.now", return_value=now):
            with patch(
                "custom_components.ostrom_advanced.binary_sensor.dt_util.start_of_local_day",
                return_value=start_time.replace(hour=0, minute=0, second=0, microsecond=0),
            ):
                data = {
                    "tomorrow_slots": [
                        {"total_price": 0.10, "start": start_time + timedelta(days=1)},
                        {"total_price": 0.20, "start": start_time.replace(hour=11) + timedelta(days=1)},
                        {"total_price": 0.15, "start": start_time.replace(hour=12) + timedelta(days=1)},
                    ]
                }
                is_active, attrs = _is_tomorrow_cheapest_3h_block_active(data)
                assert is_active is False  # Not tomorrow yet
                assert attrs is not None  # Attributes should still be returned

    def test_tomorrow_block_no_slots(self) -> None:
        """Test tomorrow's block when no slots available."""
        now = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)

        with patch("custom_components.ostrom_advanced.binary_sensor.dt_util.now", return_value=now):
            data = {"tomorrow_slots": []}
            is_active, attrs = _is_tomorrow_cheapest_3h_block_active(data)
            assert is_active is False
            assert attrs is None

