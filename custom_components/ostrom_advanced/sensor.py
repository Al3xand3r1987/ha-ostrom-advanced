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


def _get_cheapest_3h_block(slots: list[dict[str, Any]]) -> datetime | None:
    """Get start time of cheapest 3-hour block from slots (generic for today/tomorrow)."""
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


def _get_today_cheapest_hour(data: dict[str, Any]) -> datetime | None:
    """Get start time of cheapest hour today."""
    return _get_cheapest_hour(data.get("today_slots", []))


def _get_today_most_expensive_hour(data: dict[str, Any]) -> datetime | None:
    """Get start time of most expensive hour today."""
    return _get_most_expensive_hour(data.get("today_slots", []))


def _get_today_cheapest_3h_block(data: dict[str, Any]) -> datetime | None:
    """Get start time of cheapest 3-hour block today."""
    return _get_cheapest_3h_block(data.get("today_slots", []))


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


def _get_tomorrow_cheapest_hour(data: dict[str, Any]) -> datetime | None:
    """Get start time of cheapest hour tomorrow."""
    return _get_cheapest_hour(data.get("tomorrow_slots", []))


def _get_tomorrow_most_expensive_hour(data: dict[str, Any]) -> datetime | None:
    """Get start time of most expensive hour tomorrow."""
    return _get_most_expensive_hour(data.get("tomorrow_slots", []))


def _get_tomorrow_cheapest_3h_block(data: dict[str, Any]) -> datetime | None:
    """Get start time of cheapest 3-hour block tomorrow."""
    return _get_cheapest_3h_block(data.get("tomorrow_slots", []))


def _get_raw_price_attributes(data: dict[str, Any]) -> dict[str, Any]:
    """Get attributes for the raw price sensor."""
    current_slot = data.get("current_slot")

    # Serialize slots for attributes
    today_slots_serialized = []
    for slot in data.get("today_slots", []):
        today_slots_serialized.append({
            "start": slot.get("start").isoformat() if slot.get("start") else None,
            "end": slot.get("end").isoformat() if slot.get("end") else None,
            "net_price": round(slot.get("net_price", 0), 5),
            "taxes_price": round(slot.get("taxes_price", 0), 5),
            "total_price": round(slot.get("total_price", 0), 5),
        })

    tomorrow_slots_serialized = []
    for slot in data.get("tomorrow_slots", []):
        tomorrow_slots_serialized.append({
            "start": slot.get("start").isoformat() if slot.get("start") else None,
            "end": slot.get("end").isoformat() if slot.get("end") else None,
            "net_price": round(slot.get("net_price", 0), 5),
            "taxes_price": round(slot.get("taxes_price", 0), 5),
            "total_price": round(slot.get("total_price", 0), 5),
        })

    attrs = {
        "today_slots": today_slots_serialized,
        "tomorrow_slots": tomorrow_slots_serialized,
        "last_update": data.get("last_update").isoformat() if data.get("last_update") else None,
    }

    if current_slot:
        attrs["current_slot_start"] = (
            current_slot.get("start").isoformat() if current_slot.get("start") else None
        )
        attrs["current_slot_end"] = (
            current_slot.get("end").isoformat() if current_slot.get("end") else None
        )

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
    consumption_coordinator: OstromConsumptionCoordinator | None = data.get("consumption_coordinator")
    contract_id = entry.data.get(CONF_CONTRACT_ID, "") or entry.data.get(CONF_ZIP_CODE, "")

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
            name=f"Ostrom Contract {self._contract_id[-4:]}",
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
            name=f"Ostrom Contract {self._contract_id[-4:]}",
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
            name=f"Ostrom Contract {self._contract_id[-4:]}",
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
            # For yesterday, we need to use today's price slots shifted
            # In practice, yesterday's prices would have been the same structure
            # but we don't have historical prices stored
            # We'll use today's prices as an approximation or return None if not available
            price_slots = price_data.get("today_slots", [])

        if not consumption_entries or not price_slots:
            return None

        # Build a price lookup by hour
        price_by_hour: dict[int, float] = {}
        for slot in price_slots:
            start = slot.get("start")
            if start:
                price_by_hour[start.hour] = slot.get("total_price", 0)

        # Calculate cost
        total_cost = 0.0
        for entry in consumption_entries:
            kwh = entry.get("kwh", 0)
            start = entry.get("start")
            if start and start.hour in price_by_hour:
                total_cost += kwh * price_by_hour[start.hour]
            elif price_slots:
                # Fallback: use average price if exact hour not found
                avg_price = sum(s.get("total_price", 0) for s in price_slots) / len(
                    price_slots
                )
                total_cost += kwh * avg_price

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
            self._price_coordinator.async_add_listener(
                self._handle_coordinator_update
            )
        )
        self.async_on_remove(
            self._consumption_coordinator.async_add_listener(
                self._handle_coordinator_update
            )
        )

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from coordinators."""
        self.async_write_ha_state()

