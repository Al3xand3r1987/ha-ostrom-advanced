"""Data coordinators for the Ostrom Advanced integration."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import OstromApiClient, OstromApiError, OstromAuthError
from .const import (
    DEFAULT_CONSUMPTION_INTERVAL_MINUTES,
    DEFAULT_POLL_INTERVAL_MINUTES,
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
    ) -> None:
        """Initialize the price coordinator.

        Args:
            hass: Home Assistant instance
            client: Ostrom API client
            poll_interval_minutes: Polling interval in minutes
        """
        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}_price",
            update_interval=timedelta(minutes=poll_interval_minutes),
        )
        self._client = client

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
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
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

            return {
                "today_slots": today_slots,
                "tomorrow_slots": tomorrow_slots,
                "current_slot": current_slot,
                "last_update": now,
            }

        except OstromAuthError as err:
            LOGGER.error("Authentication error fetching prices: %s", err)
            raise UpdateFailed(f"Authentication error: {err}") from err
        except OstromApiError as err:
            LOGGER.error("API error fetching prices: %s", err)
            raise UpdateFailed(f"API error: {err}") from err
        except Exception as err:
            LOGGER.error("Unexpected error fetching prices: %s", err)
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
    ) -> None:
        """Initialize the consumption coordinator.

        Args:
            hass: Home Assistant instance
            client: Ostrom API client
            poll_interval_minutes: Polling interval in minutes
        """
        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}_consumption",
            update_interval=timedelta(minutes=poll_interval_minutes),
        )
        self._client = client

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
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
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

            return {
                "yesterday": yesterday_data,
                "today": today_data,
                "last_update": now,
            }

        except OstromAuthError as err:
            LOGGER.error("Authentication error fetching consumption: %s", err)
            raise UpdateFailed(f"Authentication error: {err}") from err
        except OstromApiError as err:
            LOGGER.error("API error fetching consumption: %s", err)
            raise UpdateFailed(f"API error: {err}") from err
        except Exception as err:
            LOGGER.error("Unexpected error fetching consumption: %s", err)
            raise UpdateFailed(f"Unexpected error: {err}") from err

