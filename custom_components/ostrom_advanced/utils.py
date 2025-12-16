from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from homeassistant.util import dt as dt_util

from .const import LOGGER


def calculate_next_update_time(interval_minutes: int, offset_seconds: int) -> datetime:
    """Calculate the next update time based on interval and offset.

    Args:
        interval_minutes: Polling interval in minutes
        offset_seconds: Seconds after full interval to trigger update (0-59)

    Returns:
        Next update time as datetime
    """
    # Cap offset_seconds to valid range (0-59) to prevent ValueError
    offset_seconds = min(max(0, offset_seconds), 59)

    now = dt_util.now()
    try:
        minutes_past_hour = now.minute

        # Determine the current interval start time with the offset applied
        interval_count = minutes_past_hour // interval_minutes
        interval_start_minute = interval_count * interval_minutes
        interval_start_time = now.replace(
            minute=interval_start_minute, second=offset_seconds, microsecond=0
        )

        if now < interval_start_time:
            next_time = interval_start_time
        else:
            next_minute = interval_start_minute + interval_minutes
            if next_minute >= 60:
                # Handle hour rollover explicitly
                next_hour = now.hour + 1
                if next_hour >= 24:
                    # Handle day rollover: add one day and reset to midnight
                    next_time = now.replace(
                        hour=0, minute=0, second=offset_seconds, microsecond=0
                    ) + timedelta(days=1)
                else:
                    next_time = now.replace(
                        hour=next_hour,
                        minute=0,
                        second=offset_seconds,
                        microsecond=0,
                    )
            else:
                next_time = now.replace(
                    minute=next_minute, second=offset_seconds, microsecond=0
                )

        # Ensure we never schedule in the past (DST edge cases)
        if next_time <= now:
            next_time = next_time + timedelta(minutes=interval_minutes)

        return next_time
    except (ValueError, OverflowError) as err:
        LOGGER.error(
            "Time calculation error (DST transition?): %s, using fallback", err
        )
        return now + timedelta(minutes=interval_minutes, seconds=offset_seconds)


def get_cheapest_3h_block(slots: list[dict[str, Any]]) -> datetime | None:
    """Get start time of cheapest 3-hour block from slots.

    Args:
        slots: List of price slots with 'start' and 'total_price' keys

    Returns:
        Start datetime of cheapest 3-hour block, or None if not enough slots
    """
    if len(slots) < 3:
        return None

    # Find the 3-hour block with lowest average price
    min_avg = float("inf")
    best_start = None

    for i in range(len(slots) - 2):
        block = slots[i : i + 3]
        avg_price = sum(s.get("total_price", 0) for s in block) / 3
        if avg_price < min_avg:
            min_avg = avg_price
            best_start = block[0].get("start")

    return best_start


def get_cheapest_4h_block(slots: list[dict[str, Any]]) -> datetime | None:
    """Get start time of cheapest 4-hour block from slots.

    Args:
        slots: List of price slots with 'start' and 'total_price' keys

    Returns:
        Start datetime of cheapest 4-hour block, or None if not enough slots
    """
    if len(slots) < 4:
        return None

    # Find the 4-hour block with lowest average price
    min_avg = float("inf")
    best_start = None

    for i in range(len(slots) - 3):
        block = slots[i : i + 4]
        avg_price = sum(s.get("total_price", 0) for s in block) / 4
        if avg_price < min_avg:
            min_avg = avg_price
            best_start = block[0].get("start")

    return best_start
