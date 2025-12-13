"""Data coordinators for the Ostrom Advanced integration."""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import OstromApiClient, OstromApiError, OstromAuthError
from .const import (
    DEFAULT_CONSUMPTION_INTERVAL_MINUTES,
    DEFAULT_POLL_INTERVAL_MINUTES,
    DEFAULT_UPDATE_OFFSET_SECONDS,
    DOMAIN,
    LOGGER,
    RESOLUTION_HOUR,
)


class OstromPriceCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for fetching Ostrom spot price data.

    Fetches a 48-hour window (today and tomorrow) and organizes data into:
    - today_slots: List of price slots for today
    - tomorrow_slots: List of price slots for tomorrow
    - current_slot: The slot covering the current time
    """

    def __init__(
        self,
        hass: HomeAssistant,
        client: OstromApiClient,
        poll_interval_minutes: int = DEFAULT_POLL_INTERVAL_MINUTES,
        update_offset_seconds: int = DEFAULT_UPDATE_OFFSET_SECONDS,
    ) -> None:
        """Initialize the price coordinator.

        Args:
            hass: Home Assistant instance
            client: Ostrom API client
            poll_interval_minutes: Polling interval in minutes
            update_offset_seconds: Seconds after full interval to trigger update
        """
        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}_price",
            update_interval=None,  # We handle scheduling manually
        )
        self._client = client
        self._poll_interval_minutes = poll_interval_minutes
        self._update_offset_seconds = update_offset_seconds
        self._update_timer: asyncio.TimerHandle | None = None

    def _calculate_next_update_time(
        self, interval_minutes: int, offset_seconds: int
    ) -> datetime:
        """Calculate the next update time based on interval and offset.

        Example: With 15-minute interval and 15-second offset:
        - Currently 10:07:30 → Next update: 10:15:15
        - Currently 10:15:20 → Next update: 10:30:15
        - Currently 10:00:00 → Next update: 10:00:15
        - Currently 10:00:20 → Next update: 10:15:15

        Args:
            interval_minutes: Update interval in minutes
            offset_seconds: Seconds after full interval to trigger update

        Returns:
            Next update datetime
        """
        now = dt_util.now()
        try:
            # Calculate minutes past the hour
            minutes_past_hour = now.minute

            # Find which interval we're in
            interval_count = minutes_past_hour // interval_minutes
            interval_start_minute = interval_count * interval_minutes
            interval_start_time = now.replace(
                minute=interval_start_minute, second=offset_seconds, microsecond=0
            )

            # If we're before the offset time of the current interval, use current interval
            if now < interval_start_time:
                next_time = interval_start_time
            else:
                # Otherwise, use next interval
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

            # Validate that next_time is in the future (handles DST edge cases)
            if next_time <= now:
                # If calculated time is in the past, add one interval
                next_time = next_time + timedelta(minutes=interval_minutes)

            return next_time
        except (ValueError, OverflowError) as err:
            # Fallback for DST transitions or other time calculation errors
            LOGGER.error(
                "Time calculation error (DST transition?): %s, using fallback", err
            )
            # Simple fallback: schedule for next interval from now
            fallback_time = now + timedelta(minutes=interval_minutes, seconds=offset_seconds)
            return fallback_time

    @callback
    def _schedule_next_update(self) -> None:
        """Schedule the next update based on interval and offset."""
        # Cancel existing timer if any
        if self._update_timer:
            self._update_timer.cancel()

        # Calculate next update time
        next_update = self._calculate_next_update_time(
            self._poll_interval_minutes, self._update_offset_seconds
        )
        now = dt_util.now()
        delay_seconds = (next_update - now).total_seconds()

        # If delay is negative or very small, schedule for next interval
        if delay_seconds < 1:
            # Add one interval to get the next one
            next_update = next_update + timedelta(minutes=self._poll_interval_minutes)
            delay_seconds = (next_update - now).total_seconds()

        LOGGER.debug(
            "Scheduling next price update at %s (in %.1f seconds)",
            next_update,
            delay_seconds,
        )

        # Safe callback wrapper that ensures timer is always rescheduled on errors
        def _safe_schedule_callback():
            """Safe callback wrapper that ensures timer is always rescheduled."""
            try:
                self.hass.async_create_task(self.async_request_refresh())
            except Exception as err:
                LOGGER.error(
                    "Failed to schedule price update: %s, rescheduling with fallback", err
                )
                # Reschedule with fallback delay (next interval) to keep loop running
                fallback_delay = self._poll_interval_minutes * 60
                self._update_timer = self.hass.loop.call_later(
                    fallback_delay, _safe_schedule_callback
                )

        # Schedule the update
        self._update_timer = self.hass.loop.call_later(
            delay_seconds, _safe_schedule_callback
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch price data from the API.

        Returns:
            Dictionary with today_slots, tomorrow_slots, and current_slot
        """
        try:
            # Get current time in local timezone
            now = dt_util.now()
            local_tz = now.tzinfo

            # Calculate start (midnight today) and end (midnight day after tomorrow)
            # Use dt_util.start_of_local_day() for DST-safe midnight calculation
            today_start = dt_util.start_of_local_day()
            # Request 48+ hours to ensure we have tomorrow's data
            end_date = today_start + timedelta(days=2)

            # Convert to UTC for API call
            start_utc = today_start.astimezone(dt_util.UTC).replace(tzinfo=None)
            end_utc = end_date.astimezone(dt_util.UTC).replace(tzinfo=None)

            LOGGER.debug(
                "Fetching prices from %s to %s (UTC)", start_utc, end_utc
            )

            raw_data = await self._client.async_get_spot_prices(start_utc, end_utc)

            # Process and organize the data
            today_slots: list[dict[str, Any]] = []
            tomorrow_slots: list[dict[str, Any]] = []
            current_slot: dict[str, Any] | None = None

            tomorrow_start = today_start + timedelta(days=1)

            for entry in raw_data:
                # Parse the date from API response
                slot_start_str = entry.get("date", "")
                try:
                    # API returns UTC time
                    slot_start_utc = datetime.fromisoformat(
                        slot_start_str.replace("Z", "+00:00")
                    )
                    # Convert to local time
                    slot_start = slot_start_utc.astimezone(local_tz)
                except (ValueError, TypeError) as err:
                    LOGGER.warning("Could not parse date %s: %s", slot_start_str, err)
                    continue

                slot_end = slot_start + timedelta(hours=1)

                # Create a clean slot object
                slot = {
                    "start": slot_start,
                    "end": slot_end,
                    "net_price": entry.get("net_price", 0),
                    "taxes_price": entry.get("taxes_price", 0),
                    "total_price": entry.get("total_price", 0),
                    "gross_kwh_price": entry.get("grossKwhPrice", 0) / 100,
                    "gross_tax_and_levies": entry.get("grossKwhTaxAndLevies", 0) / 100,
                }

                # Determine if this is today or tomorrow
                if slot_start.date() == today_start.date():
                    today_slots.append(slot)
                elif slot_start.date() == tomorrow_start.date():
                    tomorrow_slots.append(slot)

                # Check if this is the current slot
                if slot_start <= now < slot_end:
                    current_slot = slot

            # Sort slots by start time
            today_slots.sort(key=lambda x: x["start"])
            tomorrow_slots.sort(key=lambda x: x["start"])

            LOGGER.debug(
                "Processed %d slots for today, %d slots for tomorrow",
                len(today_slots),
                len(tomorrow_slots),
            )

            result = {
                "today_slots": today_slots,
                "tomorrow_slots": tomorrow_slots,
                "current_slot": current_slot,
                "last_update": now,
            }

            # Schedule next update
            self._schedule_next_update()

            return result

        except asyncio.CancelledError:
            LOGGER.debug("Price update cancelled, rescheduling...")
            # Schedule next update even when cancelled
            self._schedule_next_update()
            raise
        except OstromAuthError as err:
            LOGGER.error("Authentication error fetching prices: %s", err)
            # Schedule next update even on error
            self._schedule_next_update()
            raise UpdateFailed(f"Authentication error: {err}") from err
        except OstromApiError as err:
            LOGGER.error("API error fetching prices: %s", err)
            # Schedule next update even on error
            self._schedule_next_update()
            raise UpdateFailed(f"API error: {err}") from err
        except Exception as err:
            LOGGER.error("Unexpected error fetching prices: %s", err)
            # Schedule next update even on error
            self._schedule_next_update()
            raise UpdateFailed(f"Unexpected error: {err}") from err


class OstromConsumptionCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for fetching Ostrom energy consumption data.

    Fetches consumption for yesterday and today and organizes data into:
    - yesterday: List of hourly consumption data for yesterday
    - today: List of hourly consumption data for today
    """

    def __init__(
        self,
        hass: HomeAssistant,
        client: OstromApiClient,
        poll_interval_minutes: int = DEFAULT_CONSUMPTION_INTERVAL_MINUTES,
        update_offset_seconds: int = DEFAULT_UPDATE_OFFSET_SECONDS,
    ) -> None:
        """Initialize the consumption coordinator.

        Args:
            hass: Home Assistant instance
            client: Ostrom API client
            poll_interval_minutes: Polling interval in minutes
            update_offset_seconds: Seconds after full interval to trigger update
        """
        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}_consumption",
            update_interval=None,  # We handle scheduling manually
        )
        self._client = client
        self._poll_interval_minutes = poll_interval_minutes
        self._update_offset_seconds = update_offset_seconds
        self._update_timer: asyncio.TimerHandle | None = None

    def _calculate_next_update_time(
        self, interval_minutes: int, offset_seconds: int
    ) -> datetime:
        """Calculate the next update time based on interval and offset.

        Example: With 15-minute interval and 15-second offset:
        - Currently 10:07:30 → Next update: 10:15:15
        - Currently 10:15:20 → Next update: 10:30:15
        - Currently 10:00:00 → Next update: 10:00:15
        - Currently 10:00:20 → Next update: 10:15:15

        Args:
            interval_minutes: Update interval in minutes
            offset_seconds: Seconds after full interval to trigger update

        Returns:
            Next update datetime
        """
        now = dt_util.now()
        try:
            # Calculate minutes past the hour
            minutes_past_hour = now.minute

            # Find which interval we're in
            interval_count = minutes_past_hour // interval_minutes
            interval_start_minute = interval_count * interval_minutes
            interval_start_time = now.replace(
                minute=interval_start_minute, second=offset_seconds, microsecond=0
            )

            # If we're before the offset time of the current interval, use current interval
            if now < interval_start_time:
                next_time = interval_start_time
            else:
                # Otherwise, use next interval
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

            # Validate that next_time is in the future (handles DST edge cases)
            if next_time <= now:
                # If calculated time is in the past, add one interval
                next_time = next_time + timedelta(minutes=interval_minutes)

            return next_time
        except (ValueError, OverflowError) as err:
            # Fallback for DST transitions or other time calculation errors
            LOGGER.error(
                "Time calculation error (DST transition?): %s, using fallback", err
            )
            # Simple fallback: schedule for next interval from now
            fallback_time = now + timedelta(minutes=interval_minutes, seconds=offset_seconds)
            return fallback_time

    @callback
    def _schedule_next_update(self) -> None:
        """Schedule the next update based on interval and offset."""
        # Cancel existing timer if any
        if self._update_timer:
            self._update_timer.cancel()

        # Calculate next update time
        next_update = self._calculate_next_update_time(
            self._poll_interval_minutes, self._update_offset_seconds
        )
        now = dt_util.now()
        delay_seconds = (next_update - now).total_seconds()

        # If delay is negative or very small, schedule for next interval
        if delay_seconds < 1:
            # Add one interval to get the next one
            next_update = next_update + timedelta(minutes=self._poll_interval_minutes)
            delay_seconds = (next_update - now).total_seconds()

        LOGGER.debug(
            "Scheduling next consumption update at %s (in %.1f seconds)",
            next_update,
            delay_seconds,
        )

        # Safe callback wrapper that ensures timer is always rescheduled on errors
        def _safe_schedule_callback():
            """Safe callback wrapper that ensures timer is always rescheduled."""
            try:
                self.hass.async_create_task(self.async_request_refresh())
            except Exception as err:
                LOGGER.error(
                    "Failed to schedule consumption update: %s, rescheduling with fallback", err
                )
                # Reschedule with fallback delay (next interval) to keep loop running
                fallback_delay = self._poll_interval_minutes * 60
                self._update_timer = self.hass.loop.call_later(
                    fallback_delay, _safe_schedule_callback
                )

        # Schedule the update
        self._update_timer = self.hass.loop.call_later(
            delay_seconds, _safe_schedule_callback
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch consumption data from the API.

        Returns:
            Dictionary with yesterday and today consumption lists
        """
        try:
            # Get current time in local timezone
            now = dt_util.now()
            local_tz = now.tzinfo

            # Calculate time windows
            # Use dt_util.start_of_local_day() for DST-safe midnight calculation
            today_start = dt_util.start_of_local_day()
            yesterday_start = today_start - timedelta(days=1)
            end_date = today_start + timedelta(days=1)

            # Convert to UTC for API call
            start_utc = yesterday_start.astimezone(dt_util.UTC).replace(tzinfo=None)
            end_utc = end_date.astimezone(dt_util.UTC).replace(tzinfo=None)

            LOGGER.debug(
                "Fetching consumption from %s to %s (UTC)", start_utc, end_utc
            )

            raw_data = await self._client.async_get_energy_consumption(
                start_utc, end_utc, RESOLUTION_HOUR
            )

            # Process and organize the data
            yesterday_data: list[dict[str, Any]] = []
            today_data: list[dict[str, Any]] = []

            if not raw_data:
                LOGGER.info(
                    "No consumption data available for period %s to %s. "
                    "This may be normal if the smart meter is not yet active or data is not yet available.",
                    start_utc,
                    end_utc,
                )

            for entry in raw_data:
                # Parse the date from API response
                slot_start_str = entry.get("date", "")
                try:
                    # API returns UTC time
                    slot_start_utc = datetime.fromisoformat(
                        slot_start_str.replace("Z", "+00:00")
                    )
                    # Convert to local time
                    slot_start = slot_start_utc.astimezone(local_tz)
                except (ValueError, TypeError) as err:
                    LOGGER.warning("Could not parse date %s: %s", slot_start_str, err)
                    continue

                consumption_entry = {
                    "start": slot_start,
                    "end": slot_start + timedelta(hours=1),
                    "kwh": entry.get("kWh", 0),
                }

                # Determine if this is yesterday or today
                if slot_start.date() == yesterday_start.date():
                    yesterday_data.append(consumption_entry)
                elif slot_start.date() == today_start.date():
                    today_data.append(consumption_entry)

            # Sort by start time
            yesterday_data.sort(key=lambda x: x["start"])
            today_data.sort(key=lambda x: x["start"])

            LOGGER.debug(
                "Processed %d consumption entries for yesterday, %d for today",
                len(yesterday_data),
                len(today_data),
            )

            result = {
                "yesterday": yesterday_data,
                "today": today_data,
                "last_update": now,
            }

            # Schedule next update
            self._schedule_next_update()

            return result

        except asyncio.CancelledError:
            LOGGER.debug("Consumption update cancelled, rescheduling...")
            # Schedule next update even when cancelled
            self._schedule_next_update()
            raise
        except OstromAuthError as err:
            LOGGER.error("Authentication error fetching consumption: %s", err)
            # Schedule next update even on error
            self._schedule_next_update()
            raise UpdateFailed(f"Authentication error: {err}") from err
        except OstromApiError as err:
            LOGGER.error("API error fetching consumption: %s", err)
            # Schedule next update even on error
            self._schedule_next_update()
            raise UpdateFailed(f"API error: {err}") from err
        except Exception as err:
            LOGGER.error("Unexpected error fetching consumption: %s", err)
            # Schedule next update even on error
            self._schedule_next_update()
            raise UpdateFailed(f"Unexpected error: {err}") from err

