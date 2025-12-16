"""Tests for sensor calculation functions."""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from custom_components.ostrom_advanced.sensor import (
    _get_avg_price,
    _get_cheapest_3h_block,
    _get_cheapest_hour,
    _get_max_price,
    _get_median_price,
    _get_min_price,
    _get_most_expensive_hour,
)


class TestGetMinPrice:
    """Tests for _get_min_price function."""

    def test_min_price_normal_case(self) -> None:
        """Test min price with normal price list."""
        slots = [
            {"total_price": 0.25},
            {"total_price": 0.15},
            {"total_price": 0.30},
            {"total_price": 0.20},
        ]
        result = _get_min_price(slots)
        assert result == 0.15

    def test_min_price_single_value(self) -> None:
        """Test min price with single value."""
        slots = [{"total_price": 0.25}]
        result = _get_min_price(slots)
        assert result == 0.25

    def test_min_price_empty_list(self) -> None:
        """Test min price with empty list."""
        slots: list[dict[str, float]] = []
        result = _get_min_price(slots)
        assert result is None

    def test_min_price_with_zero(self) -> None:
        """Test min price with zero value."""
        slots = [
            {"total_price": 0.25},
            {"total_price": 0.0},
            {"total_price": 0.30},
        ]
        result = _get_min_price(slots)
        assert result == 0.0

    def test_min_price_rounding(self) -> None:
        """Test that min price is rounded to 5 decimal places."""
        slots = [{"total_price": 0.123456789}]
        result = _get_min_price(slots)
        assert result == 0.12346  # Rounded to 5 decimals

    def test_min_price_missing_total_price(self) -> None:
        """Test min price with missing total_price field."""
        slots = [
            {"total_price": 0.25},
            {},  # Missing total_price
            {"total_price": 0.15},
        ]
        result = _get_min_price(slots)
        assert result == 0.0  # Default value is 0


class TestGetMaxPrice:
    """Tests for _get_max_price function."""

    def test_max_price_normal_case(self) -> None:
        """Test max price with normal price list."""
        slots = [
            {"total_price": 0.25},
            {"total_price": 0.15},
            {"total_price": 0.30},
            {"total_price": 0.20},
        ]
        result = _get_max_price(slots)
        assert result == 0.30

    def test_max_price_single_value(self) -> None:
        """Test max price with single value."""
        slots = [{"total_price": 0.25}]
        result = _get_max_price(slots)
        assert result == 0.25

    def test_max_price_empty_list(self) -> None:
        """Test max price with empty list."""
        slots: list[dict[str, float]] = []
        result = _get_max_price(slots)
        assert result is None

    def test_max_price_rounding(self) -> None:
        """Test that max price is rounded to 5 decimal places."""
        slots = [{"total_price": 0.987654321}]
        result = _get_max_price(slots)
        assert result == 0.98765  # Rounded to 5 decimals

    def test_max_price_missing_total_price(self) -> None:
        """Test max price with missing total_price field."""
        slots = [
            {"total_price": 0.25},
            {},  # Missing total_price
            {"total_price": 0.30},
        ]
        result = _get_max_price(slots)
        assert result == 0.30


class TestGetAvgPrice:
    """Tests for _get_avg_price function."""

    def test_avg_price_normal_case(self) -> None:
        """Test average price with normal price list."""
        slots = [
            {"total_price": 0.20},
            {"total_price": 0.30},
            {"total_price": 0.40},
        ]
        result = _get_avg_price(slots)
        assert result == 0.30  # (0.20 + 0.30 + 0.40) / 3 = 0.30

    def test_avg_price_single_value(self) -> None:
        """Test average price with single value."""
        slots = [{"total_price": 0.25}]
        result = _get_avg_price(slots)
        assert result == 0.25

    def test_avg_price_empty_list(self) -> None:
        """Test average price with empty list."""
        slots: list[dict[str, float]] = []
        result = _get_avg_price(slots)
        assert result is None

    def test_avg_price_rounding(self) -> None:
        """Test that average price is rounded to 5 decimal places."""
        slots = [
            {"total_price": 0.1},
            {"total_price": 0.2},
            {"total_price": 0.3},
        ]
        result = _get_avg_price(slots)
        assert result == 0.2  # Exactly 0.2, no rounding needed

    def test_avg_price_with_decimals(self) -> None:
        """Test average price with decimal result."""
        slots = [
            {"total_price": 0.1},
            {"total_price": 0.2},
        ]
        result = _get_avg_price(slots)
        assert result == 0.15  # (0.1 + 0.2) / 2 = 0.15


class TestGetMedianPrice:
    """Tests for _get_median_price function."""

    def test_median_price_odd_count(self) -> None:
        """Test median price with odd number of values."""
        slots = [
            {"total_price": 0.10},
            {"total_price": 0.20},
            {"total_price": 0.30},
            {"total_price": 0.40},
            {"total_price": 0.50},
        ]
        result = _get_median_price(slots)
        assert result == 0.30  # Middle value

    def test_median_price_even_count(self) -> None:
        """Test median price with even number of values."""
        slots = [
            {"total_price": 0.10},
            {"total_price": 0.20},
            {"total_price": 0.30},
            {"total_price": 0.40},
        ]
        result = _get_median_price(slots)
        assert result == 0.25  # Average of 0.20 and 0.30

    def test_median_price_single_value(self) -> None:
        """Test median price with single value."""
        slots = [{"total_price": 0.25}]
        result = _get_median_price(slots)
        assert result == 0.25

    def test_median_price_empty_list(self) -> None:
        """Test median price with empty list."""
        slots: list[dict[str, float]] = []
        result = _get_median_price(slots)
        assert result is None

    def test_median_price_unsorted(self) -> None:
        """Test median price with unsorted values."""
        slots = [
            {"total_price": 0.50},
            {"total_price": 0.10},
            {"total_price": 0.30},
            {"total_price": 0.20},
            {"total_price": 0.40},
        ]
        result = _get_median_price(slots)
        assert result == 0.30  # Should sort and find middle

    def test_median_price_rounding(self) -> None:
        """Test that median price is rounded to 5 decimal places."""
        slots = [
            {"total_price": 0.1},
            {"total_price": 0.2},
        ]
        result = _get_median_price(slots)
        assert result == 0.15  # Average of two middle values, rounded


class TestGetCheapestHour:
    """Tests for _get_cheapest_hour function."""

    def test_cheapest_hour_normal_case(self) -> None:
        """Test cheapest hour with normal price list."""
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=ZoneInfo("Europe/Berlin"))
        slots = [
            {"total_price": 0.30, "start": start_time},
            {"total_price": 0.15, "start": start_time.replace(hour=11)},
            {"total_price": 0.25, "start": start_time.replace(hour=12)},
        ]
        result = _get_cheapest_hour(slots)
        assert result == start_time.replace(hour=11)

    def test_cheapest_hour_single_value(self) -> None:
        """Test cheapest hour with single value."""
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=ZoneInfo("Europe/Berlin"))
        slots = [{"total_price": 0.25, "start": start_time}]
        result = _get_cheapest_hour(slots)
        assert result == start_time

    def test_cheapest_hour_empty_list(self) -> None:
        """Test cheapest hour with empty list."""
        slots: list[dict[str, float | datetime]] = []
        result = _get_cheapest_hour(slots)
        assert result is None

    def test_cheapest_hour_missing_start(self) -> None:
        """Test cheapest hour with missing start field."""
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=ZoneInfo("Europe/Berlin"))
        slots = [
            {"total_price": 0.25, "start": start_time},
            {"total_price": 0.15},  # Missing start
        ]
        result = _get_cheapest_hour(slots)
        # Should return the cheapest one that has a start time
        assert result == start_time


class TestGetMostExpensiveHour:
    """Tests for _get_most_expensive_hour function."""

    def test_most_expensive_hour_normal_case(self) -> None:
        """Test most expensive hour with normal price list."""
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=ZoneInfo("Europe/Berlin"))
        slots = [
            {"total_price": 0.30, "start": start_time},
            {"total_price": 0.15, "start": start_time.replace(hour=11)},
            {"total_price": 0.25, "start": start_time.replace(hour=12)},
        ]
        result = _get_most_expensive_hour(slots)
        assert result == start_time

    def test_most_expensive_hour_single_value(self) -> None:
        """Test most expensive hour with single value."""
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=ZoneInfo("Europe/Berlin"))
        slots = [{"total_price": 0.25, "start": start_time}]
        result = _get_most_expensive_hour(slots)
        assert result == start_time

    def test_most_expensive_hour_empty_list(self) -> None:
        """Test most expensive hour with empty list."""
        slots: list[dict[str, float | datetime]] = []
        result = _get_most_expensive_hour(slots)
        assert result is None


class TestGetCheapest3hBlock:
    """Tests for _get_cheapest_3h_block function."""

    def test_cheapest_3h_block_normal_case(self) -> None:
        """Test cheapest 3h block with normal price list."""
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=ZoneInfo("Europe/Berlin"))
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
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=ZoneInfo("Europe/Berlin"))
        slots = [
            {"total_price": 0.30, "start": start_time},
            {"total_price": 0.20, "start": start_time.replace(hour=11)},
        ]
        result = _get_cheapest_3h_block(slots)
        assert result is None

    def test_cheapest_3h_block_exactly_3_slots(self) -> None:
        """Test cheapest 3h block with exactly 3 slots."""
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=ZoneInfo("Europe/Berlin"))
        slots = [
            {"total_price": 0.30, "start": start_time},
            {"total_price": 0.20, "start": start_time.replace(hour=11)},
            {"total_price": 0.25, "start": start_time.replace(hour=12)},
        ]
        result = _get_cheapest_3h_block(slots)
        assert result == start_time

    def test_cheapest_3h_block_empty_list(self) -> None:
        """Test cheapest 3h block with empty list."""
        slots: list[dict[str, float | datetime]] = []
        result = _get_cheapest_3h_block(slots)
        assert result is None

    def test_cheapest_3h_block_tie(self) -> None:
        """Test cheapest 3h block with multiple blocks having same average."""
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=ZoneInfo("Europe/Berlin"))
        slots = [
            {"total_price": 0.20, "start": start_time},  # Block 1: avg 0.20
            {"total_price": 0.20, "start": start_time.replace(hour=11)},
            {"total_price": 0.20, "start": start_time.replace(hour=12)},
            {"total_price": 0.20, "start": start_time.replace(hour=13)},  # Block 2: avg 0.20 (tie)
            {"total_price": 0.20, "start": start_time.replace(hour=14)},
            {"total_price": 0.20, "start": start_time.replace(hour=15)},
        ]
        result = _get_cheapest_3h_block(slots)
        # Should return the first block with the lowest average
        assert result == start_time

    def test_cheapest_3h_block_missing_start(self) -> None:
        """Test cheapest 3h block with missing start field."""
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=ZoneInfo("Europe/Berlin"))
        slots = [
            {"total_price": 0.20, "start": start_time},
            {"total_price": 0.20, "start": start_time.replace(hour=11)},
            {"total_price": 0.20},  # Missing start
        ]
        result = _get_cheapest_3h_block(slots)
        # Should still work, but might return None if the best block has missing start
        # In this case, it should return the first block's start
        assert result == start_time

