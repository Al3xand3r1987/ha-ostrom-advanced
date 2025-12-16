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
from .utils import calculate_next_update_time


class OstromBaseCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Base coordinator with common scheduling logic."""

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        poll_interval_minutes: int,
        update_offset_seconds: int,
    ) -> None:
        """Initialize base coordinator.

        Args:
            hass: Home Assistant instance
            name: Coordinator name
            poll_interval_minutes: Polling interval in minutes
            update_offset_seconds: Seconds after full interval to trigger update
        """
        super().__init__(
            hass,
            LOGGER,
            name=name,
            update_interval=None,  # We handle scheduling manually
        )
        self._poll_interval_minutes = poll_interval_minutes
        self._update_offset_seconds = update_offset_seconds
        self._update_timer: asyncio.TimerHandle | None = None

    @callback
    def _schedule_next_update(self, log_name: str = "update") -> None:
        """Schedule the next update based on interval and offset.

        Args:
            log_name: Name for logging (e.g., "price" or "consumption")
        """
        # Cancel existing timer if any
        if self._update_timer:
            self._update_timer.cancel()

        # Calculate next update time
        next_update = calculate_next_update_time(
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
            "Scheduling next %s update at %s (in %.1f seconds)",
            log_name,
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
                    "Failed to schedule %s update: %s, rescheduling with fallback",
                    log_name,
                    err,
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

    async def async_shutdown(self) -> None:
        """Cancel any pending timer when coordinator is shut down."""
        if self._update_timer:
            self._update_timer.cancel()
            self._update_timer = None
            LOGGER.debug("Cancelled update timer for %s", self.name)


class OstromPriceCoordinator(OstromBaseCoordinator):
    """Coordinator for fetching Ostrom spot price data.

    Fetches a 72-hour window (yesterday, today, and tomorrow) and organizes data into:
    - yesterday_slots: List of price slots for yesterday (for historical cost calculation)
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
            f"{DOMAIN}_price",
            poll_interval_minutes,
            update_offset_seconds,
        )
        self._client = client

    @callback
    def _schedule_next_update(self) -> None:
        """Schedule the next update based on interval and offset."""
        super()._schedule_next_update("price")

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch price data from the API.

        Returns:
            Dictionary with yesterday_slots, today_slots, tomorrow_slots, and current_slot
        """
        try:
            # Get current time in local timezone
            now = dt_util.now()
            local_tz = now.tzinfo

            # Calculate start (midnight yesterday) and end (midnight day after tomorrow)
            # Use dt_util.start_of_local_day() for DST-safe midnight calculation
            today_start = dt_util.start_of_local_day()
            yesterday_start = today_start - timedelta(days=1)
            # Request 72+ hours: yesterday, today, and tomorrow
            end_date = today_start + timedelta(days=2)

            # Convert to UTC for API call
            start_utc = yesterday_start.astimezone(dt_util.UTC).replace(tzinfo=None)
            end_utc = end_date.astimezone(dt_util.UTC).replace(tzinfo=None)

            LOGGER.debug(
                "Fetching prices from %s to %s (UTC)", start_utc, end_utc
            )

            raw_data = await self._client.async_get_spot_prices(start_utc, end_utc)

            # Process and organize the data
            yesterday_slots: list[dict[str, Any]] = []
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

                # Determine which day this slot belongs to
                slot_date = slot_start.date()
                if slot_date == yesterday_start.date():
                    yesterday_slots.append(slot)
                elif slot_date == today_start.date():
                    today_slots.append(slot)
                elif slot_date == tomorrow_start.date():
                    tomorrow_slots.append(slot)

                # Check if this is the current slot
                if slot_start <= now < slot_end:
                    current_slot = slot

            # Sort slots by start time
            yesterday_slots.sort(key=lambda x: x["start"])
            today_slots.sort(key=lambda x: x["start"])
            tomorrow_slots.sort(key=lambda x: x["start"])

            LOGGER.debug(
                "Processed %d slots for yesterday, %d slots for today, %d slots for tomorrow",
                len(yesterday_slots),
                len(today_slots),
                len(tomorrow_slots),
            )

            result = {
                "yesterday_slots": yesterday_slots,
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


class OstromConsumptionCoordinator(OstromBaseCoordinator):
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
            f"{DOMAIN}_consumption",
            poll_interval_minutes,
            update_offset_seconds,
        )
        self._client = client

    @callback
    def _schedule_next_update(self) -> None:
        """Schedule the next update based on interval and offset."""
        super()._schedule_next_update("consumption")

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
