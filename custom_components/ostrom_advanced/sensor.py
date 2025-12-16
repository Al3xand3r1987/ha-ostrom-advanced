"""Sensor platform for the Ostrom Advanced integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    CONF_CONTRACT_ID,
    CONF_ZIP_CODE,
    DEVELOPER_PORTAL_URL,
    DOMAIN,
    LOGGER,
)
from .coordinator import OstromConsumptionCoordinator, OstromPriceCoordinator
from .utils import get_cheapest_3h_block


@dataclass(frozen=True, kw_only=True)
class OstromSensorEntityDescription(SensorEntityDescription):
    """Describes Ostrom sensor entity."""

    value_fn: Callable[[dict[str, Any]], Any]
    extra_state_attributes_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None
    icon: str | None = None


def _get_current_price(data: dict[str, Any]) -> float | None:
    """Get current price from data."""
    current_slot = data.get("current_slot")
    if current_slot:
        return round(current_slot.get("total_price", 0), 5)
    return None


# Generic helper functions for price calculations
def _get_min_price(slots: list[dict[str, Any]]) -> float | None:
    """Get minimum price from slots (generic for today/tomorrow)."""
    if not slots:
        return None
    prices = [s.get("total_price", 0) for s in slots]
    return round(min(prices), 5) if prices else None


def _get_max_price(slots: list[dict[str, Any]]) -> float | None:
    """Get maximum price from slots (generic for today/tomorrow)."""
    if not slots:
        return None
    prices = [s.get("total_price", 0) for s in slots]
    return round(max(prices), 5) if prices else None


def _get_avg_price(slots: list[dict[str, Any]]) -> float | None:
    """Get average price from slots (generic for today/tomorrow)."""
    if not slots:
        return None
    prices = [s.get("total_price", 0) for s in slots]
    return round(sum(prices) / len(prices), 5) if prices else None


def _get_median_price(slots: list[dict[str, Any]]) -> float | None:
    """Get median price from slots (generic for today/tomorrow)."""
    if not slots:
        return None
    prices = [s.get("total_price", 0) for s in slots]
    if not prices:
        return None

    # Sort prices
    sorted_prices = sorted(prices)
    length = len(sorted_prices)

    # Calculate median
    if length % 2 == 1:
        # Odd number of elements: return middle element
        median = sorted_prices[length // 2]
    else:
        # Even number of elements: return average of two middle elements
        median = (sorted_prices[length // 2 - 1] + sorted_prices[length // 2]) / 2

    return round(median, 5)


def _get_cheapest_hour(slots: list[dict[str, Any]]) -> datetime | None:
    """Get start time of cheapest hour from slots (generic for today/tomorrow)."""
    if not slots:
        return None
    cheapest = min(slots, key=lambda s: s.get("total_price", float("inf")))
    return cheapest.get("start")


def _get_most_expensive_hour(slots: list[dict[str, Any]]) -> datetime | None:
    """Get start time of most expensive hour from slots (generic for today/tomorrow)."""
    if not slots:
        return None
    most_expensive = max(slots, key=lambda s: s.get("total_price", float("-inf")))
    return most_expensive.get("start")


# Wrapper functions for today
def _get_today_min_price(data: dict[str, Any]) -> float | None:
    """Get minimum price for today."""
    return _get_min_price(data.get("today_slots", []))


def _get_today_max_price(data: dict[str, Any]) -> float | None:
    """Get maximum price for today."""
    return _get_max_price(data.get("today_slots", []))


def _get_today_avg_price(data: dict[str, Any]) -> float | None:
    """Get average price for today."""
    return _get_avg_price(data.get("today_slots", []))


def _get_today_median_price(data: dict[str, Any]) -> float | None:
    """Get median price for today."""
    return _get_median_price(data.get("today_slots", []))


def _get_today_cheapest_hour(data: dict[str, Any]) -> datetime | None:
    """Get start time of cheapest hour today."""
    return _get_cheapest_hour(data.get("today_slots", []))


def _get_today_most_expensive_hour(data: dict[str, Any]) -> datetime | None:
    """Get start time of most expensive hour today."""
    return _get_most_expensive_hour(data.get("today_slots", []))


def _get_today_cheapest_3h_block(data: dict[str, Any]) -> datetime | None:
    """Get start time of cheapest 3-hour block today."""
    return get_cheapest_3h_block(data.get("today_slots", []))


# Wrapper functions for tomorrow
def _get_tomorrow_min_price(data: dict[str, Any]) -> float | None:
    """Get minimum price for tomorrow."""
    return _get_min_price(data.get("tomorrow_slots", []))


def _get_tomorrow_max_price(data: dict[str, Any]) -> float | None:
    """Get maximum price for tomorrow."""
    return _get_max_price(data.get("tomorrow_slots", []))


def _get_tomorrow_avg_price(data: dict[str, Any]) -> float | None:
    """Get average price for tomorrow."""
    return _get_avg_price(data.get("tomorrow_slots", []))


def _get_tomorrow_median_price(data: dict[str, Any]) -> float | None:
    """Get median price for tomorrow."""
    return _get_median_price(data.get("tomorrow_slots", []))


def _get_tomorrow_cheapest_hour(data: dict[str, Any]) -> datetime | None:
    """Get start time of cheapest hour tomorrow."""
    return _get_cheapest_hour(data.get("tomorrow_slots", []))


def _get_tomorrow_most_expensive_hour(data: dict[str, Any]) -> datetime | None:
    """Get start time of most expensive hour tomorrow."""
    return _get_most_expensive_hour(data.get("tomorrow_slots", []))


def _get_tomorrow_cheapest_3h_block(data: dict[str, Any]) -> datetime | None:
    """Get start time of cheapest 3-hour block tomorrow."""
    return get_cheapest_3h_block(data.get("tomorrow_slots", []))


def _get_price_now_attributes(data: dict[str, Any]) -> dict[str, Any]:
    """Get attributes for the price_now sensor with total_price data for time series."""
    attrs: dict[str, Any] = {}

    # Serialize yesterday's total_price data for time series
    yesterday_prices = []
    for slot in data.get("yesterday_slots", []):
        start = slot.get("start")
        if start:
            yesterday_prices.append(
                {
                    "timestamp": start.isoformat(),
                    "total_price": round(slot.get("total_price", 0), 5),
                }
            )

    if yesterday_prices:
        attrs["yesterday_total_prices"] = yesterday_prices

    # Serialize today's total_price data for time series
    today_prices = []
    for slot in data.get("today_slots", []):
        start = slot.get("start")
        if start:
            today_prices.append(
                {
                    "timestamp": start.isoformat(),
                    "total_price": round(slot.get("total_price", 0), 5),
                }
            )

    if today_prices:
        attrs["today_total_prices"] = today_prices

    # Serialize tomorrow's total_price data for time series (if available)
    tomorrow_prices = []
    for slot in data.get("tomorrow_slots", []):
        start = slot.get("start")
        if start:
            tomorrow_prices.append(
                {
                    "timestamp": start.isoformat(),
                    "total_price": round(slot.get("total_price", 0), 5),
                }
            )

    if tomorrow_prices:
        attrs["tomorrow_total_prices"] = tomorrow_prices

    # Build timeline data for price-timeline-card compatibility
    # Combine yesterday and today for the first parameter, tomorrow for the second
    # This ensures chronological order: yesterday -> today -> tomorrow
    yesterday_and_today = yesterday_prices + today_prices
    timeline_data = build_timeline_data(yesterday_and_today, tomorrow_prices)
    attrs["data"] = timeline_data

    # Build ApexCharts format: array of pairs [timestamp, price]
    # This format is directly usable in ApexCharts time series
    # Contains yesterday, today, and tomorrow in chronological order
    apex_data = [[item["start_time"], item["price_per_kwh"]] for item in timeline_data]
    attrs["apex_data"] = apex_data

    # Add last update timestamp
    if data.get("last_update"):
        attrs["last_update"] = data.get("last_update").isoformat()

    return attrs


def build_timeline_data(
    today_list: list[dict[str, Any]] | None,
    tomorrow_list: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    """Build timeline data array for price-timeline-card compatibility.

    Converts price data from various formats into a unified timeline format:
    [{"start_time": "ISO-timestamp", "price_per_kwh": float}, ...]

    Args:
        today_list: List of price entries for today. Can be:
            - Format 1: [{"timestamp": "ISO-string", "total_price": float}, ...]
            - Format 2: [{"start": "ISO-string" or datetime, "total_price": float}, ...]
        tomorrow_list: Same format as today_list, but for tomorrow (optional).

    Returns:
        Sorted list of timeline entries with start_time and price_per_kwh.
    """
    timeline: list[dict[str, Any]] = []

    # Process today's data
    if today_list:
        for item in today_list:
            try:
                # Handle format 1: {timestamp, total_price}
                if "timestamp" in item:
                    start_time = item.get("timestamp")
                    price = item.get("total_price")
                # Handle format 2: {start, total_price}
                elif "start" in item:
                    start = item.get("start")
                    if start is None:
                        continue
                    # Convert datetime to ISO string if needed
                    if isinstance(start, datetime):
                        start_time = start.isoformat()
                    else:
                        start_time = str(start)
                    price = item.get("total_price")
                else:
                    continue

                # Validate required fields
                if start_time is None or price is None:
                    continue

                # Convert price to float
                try:
                    price_per_kwh = float(price)
                except (ValueError, TypeError):
                    continue

                timeline.append(
                    {
                        "start_time": str(start_time),
                        "price_per_kwh": round(price_per_kwh, 5),
                    }
                )
            except (KeyError, TypeError, AttributeError):
                # Skip invalid entries
                continue

    # Process tomorrow's data (if available)
    if tomorrow_list:
        for item in tomorrow_list:
            try:
                # Handle format 1: {timestamp, total_price}
                if "timestamp" in item:
                    start_time = item.get("timestamp")
                    price = item.get("total_price")
                # Handle format 2: {start, total_price}
                elif "start" in item:
                    start = item.get("start")
                    if start is None:
                        continue
                    # Convert datetime to ISO string if needed
                    if isinstance(start, datetime):
                        start_time = start.isoformat()
                    else:
                        start_time = str(start)
                    price = item.get("total_price")
                else:
                    continue

                # Validate required fields
                if start_time is None or price is None:
                    continue

                # Convert price to float
                try:
                    price_per_kwh = float(price)
                except (ValueError, TypeError):
                    continue

                timeline.append(
                    {
                        "start_time": str(start_time),
                        "price_per_kwh": round(price_per_kwh, 5),
                    }
                )
            except (KeyError, TypeError, AttributeError):
                # Skip invalid entries
                continue

    # Sort by start_time
    timeline.sort(key=lambda x: x.get("start_time", ""))

    # Deduplicate: if duplicate timestamps occur, keep the last entry
    # This handles cases where today and tomorrow might overlap
    seen: dict[str, dict[str, Any]] = {}
    for item in timeline:
        start_time = item.get("start_time")
        if start_time:
            seen[start_time] = item  # Last entry with same timestamp wins

    # Convert back to list and sort again to ensure order
    timeline = list(seen.values())
    timeline.sort(key=lambda x: x.get("start_time", ""))

    return timeline


def _get_raw_price_attributes(data: dict[str, Any]) -> dict[str, Any]:
    """Get attributes for the raw price sensor."""
    current_slot = data.get("current_slot")

    # Serialize slots for attributes
    yesterday_slots_serialized = []
    for slot in data.get("yesterday_slots", []):
        yesterday_slots_serialized.append(
            {
                "start": slot.get("start").isoformat() if slot.get("start") else None,
                "end": slot.get("end").isoformat() if slot.get("end") else None,
                "net_price": round(slot.get("net_price", 0), 5),
                "taxes_price": round(slot.get("taxes_price", 0), 5),
                "total_price": round(slot.get("total_price", 0), 5),
            }
        )

    today_slots_serialized = []
    for slot in data.get("today_slots", []):
        today_slots_serialized.append(
            {
                "start": slot.get("start").isoformat() if slot.get("start") else None,
                "end": slot.get("end").isoformat() if slot.get("end") else None,
                "net_price": round(slot.get("net_price", 0), 5),
                "taxes_price": round(slot.get("taxes_price", 0), 5),
                "total_price": round(slot.get("total_price", 0), 5),
            }
        )

    tomorrow_slots_serialized = []
    for slot in data.get("tomorrow_slots", []):
        tomorrow_slots_serialized.append(
            {
                "start": slot.get("start").isoformat() if slot.get("start") else None,
                "end": slot.get("end").isoformat() if slot.get("end") else None,
                "net_price": round(slot.get("net_price", 0), 5),
                "taxes_price": round(slot.get("taxes_price", 0), 5),
                "total_price": round(slot.get("total_price", 0), 5),
            }
        )

    attrs = {
        "yesterday_slots": yesterday_slots_serialized,
        "today_slots": today_slots_serialized,
        "tomorrow_slots": tomorrow_slots_serialized,
        "last_update": data.get("last_update").isoformat()
        if data.get("last_update")
        else None,
    }

    if current_slot:
        attrs["current_slot_start"] = (
            current_slot.get("start").isoformat() if current_slot.get("start") else None
        )
        attrs["current_slot_end"] = (
            current_slot.get("end").isoformat() if current_slot.get("end") else None
        )

    # Build timeline data for price-timeline-card compatibility
    # Map slots to {start, total_price} format for build_timeline_data
    yesterday_timeline_input = []
    for slot in data.get("yesterday_slots", []):
        start = slot.get("start")
        if start:
            yesterday_timeline_input.append(
                {
                    "start": start.isoformat()
                    if isinstance(start, datetime)
                    else start,
                    "total_price": slot.get("total_price", 0),
                }
            )

    today_timeline_input = []
    for slot in data.get("today_slots", []):
        start = slot.get("start")
        if start:
            today_timeline_input.append(
                {
                    "start": start.isoformat()
                    if isinstance(start, datetime)
                    else start,
                    "total_price": slot.get("total_price", 0),
                }
            )

    tomorrow_timeline_input = []
    for slot in data.get("tomorrow_slots", []):
        start = slot.get("start")
        if start:
            tomorrow_timeline_input.append(
                {
                    "start": start.isoformat()
                    if isinstance(start, datetime)
                    else start,
                    "total_price": slot.get("total_price", 0),
                }
            )

    # Build timeline data from yesterday, today, and tomorrow
    # Note: build_timeline_data accepts two lists, so we combine yesterday and today for the first parameter
    yesterday_and_today = yesterday_timeline_input + today_timeline_input
    attrs["data"] = build_timeline_data(yesterday_and_today, tomorrow_timeline_input)

    return attrs


PRICE_SENSORS: tuple[OstromSensorEntityDescription, ...] = (
    OstromSensorEntityDescription(
        key="spot_prices_raw",
        translation_key="spot_prices_raw",
        native_unit_of_measurement="€/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=5,
        value_fn=_get_current_price,
        extra_state_attributes_fn=_get_raw_price_attributes,
        icon="mdi:flash",
    ),
    OstromSensorEntityDescription(
        key="price_now",
        translation_key="price_now",
        native_unit_of_measurement="€/kWh",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=5,
        value_fn=_get_current_price,
        extra_state_attributes_fn=_get_price_now_attributes,
        icon="mdi:flash",
    ),
    OstromSensorEntityDescription(
        key="price_today_min",
        translation_key="price_today_min",
        native_unit_of_measurement="€/kWh",
        suggested_display_precision=5,
        value_fn=_get_today_min_price,
        icon="mdi:trending-down",
    ),
    OstromSensorEntityDescription(
        key="price_today_max",
        translation_key="price_today_max",
        native_unit_of_measurement="€/kWh",
        suggested_display_precision=5,
        value_fn=_get_today_max_price,
        icon="mdi:trending-up",
    ),
    OstromSensorEntityDescription(
        key="price_today_avg",
        translation_key="price_today_avg",
        native_unit_of_measurement="€/kWh",
        suggested_display_precision=5,
        value_fn=_get_today_avg_price,
        icon="mdi:chart-bell-curve-cumulative",
    ),
    OstromSensorEntityDescription(
        key="price_today_median",
        translation_key="price_today_median",
        native_unit_of_measurement="€/kWh",
        suggested_display_precision=5,
        value_fn=_get_today_median_price,
        icon="mdi:chart-bell-curve",
    ),
    OstromSensorEntityDescription(
        key="price_today_cheapest_hour_start",
        translation_key="price_today_cheapest_hour_start",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=_get_today_cheapest_hour,
        icon="mdi:clock-start",
    ),
    OstromSensorEntityDescription(
        key="price_today_cheapest_3h_block_start",
        translation_key="price_today_cheapest_3h_block_start",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=_get_today_cheapest_3h_block,
        icon="mdi:timer-outline",
    ),
    OstromSensorEntityDescription(
        key="price_today_most_expensive_hour_start",
        translation_key="price_today_most_expensive_hour_start",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=_get_today_most_expensive_hour,
        icon="mdi:clock-alert",
    ),
    OstromSensorEntityDescription(
        key="price_tomorrow_min",
        translation_key="price_tomorrow_min",
        native_unit_of_measurement="€/kWh",
        suggested_display_precision=5,
        value_fn=_get_tomorrow_min_price,
        icon="mdi:trending-down",
    ),
    OstromSensorEntityDescription(
        key="price_tomorrow_max",
        translation_key="price_tomorrow_max",
        native_unit_of_measurement="€/kWh",
        suggested_display_precision=5,
        value_fn=_get_tomorrow_max_price,
        icon="mdi:trending-up",
    ),
    OstromSensorEntityDescription(
        key="price_tomorrow_avg",
        translation_key="price_tomorrow_avg",
        native_unit_of_measurement="€/kWh",
        suggested_display_precision=5,
        value_fn=_get_tomorrow_avg_price,
        icon="mdi:chart-bell-curve-cumulative",
    ),
    OstromSensorEntityDescription(
        key="price_tomorrow_median",
        translation_key="price_tomorrow_median",
        native_unit_of_measurement="€/kWh",
        suggested_display_precision=5,
        value_fn=_get_tomorrow_median_price,
        icon="mdi:chart-bell-curve",
    ),
    OstromSensorEntityDescription(
        key="price_tomorrow_cheapest_hour_start",
        translation_key="price_tomorrow_cheapest_hour_start",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=_get_tomorrow_cheapest_hour,
        icon="mdi:clock-start",
    ),
    OstromSensorEntityDescription(
        key="price_tomorrow_cheapest_3h_block_start",
        translation_key="price_tomorrow_cheapest_3h_block_start",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=_get_tomorrow_cheapest_3h_block,
        icon="mdi:timer-outline",
    ),
    OstromSensorEntityDescription(
        key="price_tomorrow_most_expensive_hour_start",
        translation_key="price_tomorrow_most_expensive_hour_start",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=_get_tomorrow_most_expensive_hour,
        icon="mdi:clock-alert",
    ),
)


def _get_consumption_today(data: dict[str, Any]) -> float | None:
    """Get total consumption for today."""
    today_data = data.get("today", [])
    if not today_data:
        return None
    return round(sum(entry.get("kwh", 0) for entry in today_data), 3)


def _get_consumption_yesterday(data: dict[str, Any]) -> float | None:
    """Get total consumption for yesterday."""
    yesterday_data = data.get("yesterday", [])
    if not yesterday_data:
        return None
    return round(sum(entry.get("kwh", 0) for entry in yesterday_data), 3)


CONSUMPTION_SENSORS: tuple[OstromSensorEntityDescription, ...] = (
    OstromSensorEntityDescription(
        key="consumption_today_kwh",
        translation_key="consumption_today_kwh",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=3,
        value_fn=_get_consumption_today,
    ),
    OstromSensorEntityDescription(
        key="consumption_yesterday_kwh",
        translation_key="consumption_yesterday_kwh",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=3,
        value_fn=_get_consumption_yesterday,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ostrom sensors from a config entry."""
    LOGGER.info("Setting up Ostrom Advanced sensors for entry %s", entry.entry_id)

    data = hass.data[DOMAIN][entry.entry_id]
    price_coordinator: OstromPriceCoordinator = data["price_coordinator"]
    consumption_coordinator: OstromConsumptionCoordinator | None = data.get(
        "consumption_coordinator"
    )
    contract_id = entry.data.get(CONF_CONTRACT_ID, "") or entry.data.get(
        CONF_ZIP_CODE, ""
    )

    entities: list[SensorEntity] = []

    # Add price sensors
    LOGGER.info("Creating %d price sensors", len(PRICE_SENSORS))
    for description in PRICE_SENSORS:
        entities.append(
            OstromPriceSensor(
                coordinator=price_coordinator,
                description=description,
                contract_id=contract_id,
            )
        )

    # Add consumption sensors only if contract_id is provided
    if consumption_coordinator:
        LOGGER.info("Creating %d consumption sensors", len(CONSUMPTION_SENSORS))
        for description in CONSUMPTION_SENSORS:
            entities.append(
                OstromConsumptionSensor(
                    coordinator=consumption_coordinator,
                    description=description,
                    contract_id=contract_id,
                )
            )

        # Add cost sensors (use both coordinators)
        LOGGER.info("Creating 2 cost sensors")
        entities.append(
            OstromCostSensor(
                price_coordinator=price_coordinator,
                consumption_coordinator=consumption_coordinator,
                contract_id=contract_id,
                is_today=True,
            )
        )
        entities.append(
            OstromCostSensor(
                price_coordinator=price_coordinator,
                consumption_coordinator=consumption_coordinator,
                contract_id=contract_id,
                is_today=False,
            )
        )
    else:
        LOGGER.info("No contract ID provided, skipping consumption and cost sensors")

    LOGGER.info("Adding %d entities to Home Assistant", len(entities))
    async_add_entities(entities)
    LOGGER.info("Successfully added %d Ostrom Advanced entities", len(entities))


class OstromPriceSensor(CoordinatorEntity[OstromPriceCoordinator], SensorEntity):
    """Representation of an Ostrom price sensor."""

    entity_description: OstromSensorEntityDescription
    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: OstromPriceCoordinator,
        description: OstromSensorEntityDescription,
        contract_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._contract_id = contract_id
        self._attr_unique_id = f"ostrom_advanced_{contract_id}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._contract_id)},
            name="Ostrom",
            manufacturer="Ostrom",
            model="Dynamic tariff integration",
            configuration_url=DEVELOPER_PORTAL_URL,
        )

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def icon(self) -> str | None:
        """Return the icon for the sensor."""
        # Always use icon from description if available
        if self.entity_description.icon:
            return self.entity_description.icon
        # Fallback icon only if no icon specified in description
        return "mdi:clock-alert"

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if (
            self.entity_description.extra_state_attributes_fn is None
            or self.coordinator.data is None
        ):
            return None
        return self.entity_description.extra_state_attributes_fn(self.coordinator.data)


class OstromConsumptionSensor(
    CoordinatorEntity[OstromConsumptionCoordinator], SensorEntity
):
    """Representation of an Ostrom consumption sensor."""

    entity_description: OstromSensorEntityDescription
    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: OstromConsumptionCoordinator,
        description: OstromSensorEntityDescription,
        contract_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._contract_id = contract_id
        self._attr_unique_id = f"ostrom_advanced_{contract_id}_{description.key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._contract_id)},
            name="Ostrom",
            manufacturer="Ostrom",
            model="Dynamic tariff integration",
            configuration_url=DEVELOPER_PORTAL_URL,
        )

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)


class OstromCostSensor(SensorEntity):
    """Representation of an Ostrom cost sensor.

    This sensor combines data from both the price and consumption coordinators
    to calculate the actual energy cost.
    """

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = "€"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL
    _attr_suggested_display_precision = 2

    def __init__(
        self,
        price_coordinator: OstromPriceCoordinator,
        consumption_coordinator: OstromConsumptionCoordinator,
        contract_id: str,
        is_today: bool,
    ) -> None:
        """Initialize the cost sensor."""
        self._price_coordinator = price_coordinator
        self._consumption_coordinator = consumption_coordinator
        self._contract_id = contract_id
        self._is_today = is_today

        key = "cost_today_eur" if is_today else "cost_yesterday_eur"
        self._attr_unique_id = f"ostrom_advanced_{contract_id}_{key}"
        self._attr_translation_key = key

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._contract_id)},
            name="Ostrom",
            manufacturer="Ostrom",
            model="Dynamic tariff integration",
            configuration_url=DEVELOPER_PORTAL_URL,
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self._price_coordinator.last_update_success
            and self._consumption_coordinator.last_update_success
        )

    @property
    def native_value(self) -> float | None:
        """Calculate and return the cost."""
        price_data = self._price_coordinator.data
        consumption_data = self._consumption_coordinator.data

        if not price_data or not consumption_data:
            return None

        # Get the appropriate data
        if self._is_today:
            consumption_entries = consumption_data.get("today", [])
            price_slots = price_data.get("today_slots", [])
        else:
            consumption_entries = consumption_data.get("yesterday", [])
            # Use yesterday's price slots for accurate historical cost calculation
            price_slots = price_data.get("yesterday_slots", [])

        if not consumption_entries or not price_slots:
            return None

        # Build a price lookup by full datetime (date + hour) for accurate matching
        # This ensures we match the correct price for each consumption entry
        price_by_datetime: dict[datetime, float] = {}
        for slot in price_slots:
            start = slot.get("start")
            if start:
                # Use the start datetime as key (normalized to hour precision)
                hour_start = start.replace(minute=0, second=0, microsecond=0)
                price_by_datetime[hour_start] = slot.get("total_price", 0)

        # Calculate cost by matching consumption entries with price slots
        total_cost = 0.0
        for entry in consumption_entries:
            kwh = entry.get("kwh", 0)
            start = entry.get("start")
            if start:
                # Normalize to hour precision for matching
                hour_start = start.replace(minute=0, second=0, microsecond=0)

                if hour_start in price_by_datetime:
                    # Exact match found
                    total_cost += kwh * price_by_datetime[hour_start]
                elif price_slots:
                    # Fallback: use average price if exact hour not found
                    avg_price = sum(s.get("total_price", 0) for s in price_slots) / len(
                        price_slots
                    )
                    total_cost += kwh * avg_price
                    LOGGER.warning(
                        "No exact price match for %s, using average price %.5f €/kWh",
                        hour_start,
                        avg_price,
                    )

        return round(total_cost, 2)

    async def async_update(self) -> None:
        """Update the entity.

        Note: This entity doesn't need its own update logic since it
        derives its state from the coordinators.
        """

    async def async_added_to_hass(self) -> None:
        """Register callbacks when entity is added."""
        # Listen to both coordinators for updates
        self.async_on_remove(
            self._price_coordinator.async_add_listener(self._handle_coordinator_update)
        )
        self.async_on_remove(
            self._consumption_coordinator.async_add_listener(
                self._handle_coordinator_update
            )
        )

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from coordinators."""
        self.async_write_ha_state()
