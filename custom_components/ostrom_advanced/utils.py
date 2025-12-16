from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.util import dt as dt_util

from .const import LOGGER


def calculate_next_update_time(interval_minutes: int, offset_seconds: int) -> datetime:
    """Calculate the next update time based on interval and offset."""
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
                next_time = now.replace(
                    hour=now.hour + 1,
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
        LOGGER.error("Time calculation error (DST transition?): %s, using fallback", err)
        return now + timedelta(minutes=interval_minutes, seconds=offset_seconds)
