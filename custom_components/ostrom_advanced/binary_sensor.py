"""Binary sensor platform for the Ostrom Advanced integration."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import (
    ATTRIBUTION,
    CONF_CONTRACT_ID,
    CONF_ZIP_CODE,
    DEVELOPER_PORTAL_URL,
    DOMAIN,
    LOGGER,
)
from .coordinator import OstromPriceCoordinator


def _get_cheapest_3h_block(slots: list[dict[str, Any]]) -> datetime | None:
    """Get start time of cheapest 3-hour block from slots."""
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


def _get_cheapest_4h_block(slots: list[dict[str, Any]]) -> datetime | None:
    """Get start time of cheapest 4-hour block from slots."""
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


def _is_cheapest_3h_block_active(
    slots: list[dict[str, Any]], now: datetime
) -> tuple[bool, datetime | None, datetime | None]:
    """Check if current time is within the cheapest 3-hour block.

    Args:
        slots: List of price slots for today or tomorrow
        now: Current datetime

    Returns:
        Tuple of (is_active, block_start, block_end)
    """
    block_start = _get_cheapest_3h_block(slots)
    if not block_start:
        return (False, None, None)

    # Calculate end time (start + 3 hours)
    block_end = block_start + timedelta(hours=3)

    # Check if current time is within the block
    is_active = block_start <= now < block_end

    return (is_active, block_start, block_end)


def _is_cheapest_4h_block_active(
    slots: list[dict[str, Any]], now: datetime
) -> tuple[bool, datetime | None, datetime | None]:
    """Check if current time is within the cheapest 4-hour block.

    Args:
        slots: List of price slots for today or tomorrow
        now: Current datetime

    Returns:
        Tuple of (is_active, block_start, block_end)
    """
    block_start = _get_cheapest_4h_block(slots)
    if not block_start:
        return (False, None, None)

    # Calculate end time (start + 4 hours)
    block_end = block_start + timedelta(hours=4)

    # Check if current time is within the block
    is_active = block_start <= now < block_end

    return (is_active, block_start, block_end)


def _is_today_cheapest_3h_block_active(data: dict[str, Any]) -> tuple[bool, dict[str, Any] | None]:
    """Check if today's cheapest 3-hour block is currently active.

    Returns:
        Tuple of (is_active, attributes_dict)
    """
    now = dt_util.now()
    today_slots = data.get("today_slots", [])
    is_active, block_start, block_end = _is_cheapest_3h_block_active(today_slots, now)

    attrs = None
    if block_start:
        attrs = {
            "block_start": block_start.isoformat(),
            "block_end": block_end.isoformat() if block_end else None,
        }

    return (is_active, attrs)


def _is_today_cheapest_4h_block_active(data: dict[str, Any]) -> tuple[bool, dict[str, Any] | None]:
    """Check if today's cheapest 4-hour block is currently active.

    Returns:
        Tuple of (is_active, attributes_dict)
    """
    now = dt_util.now()
    today_slots = data.get("today_slots", [])
    is_active, block_start, block_end = _is_cheapest_4h_block_active(today_slots, now)

    attrs = None
    if block_start:
        attrs = {
            "block_start": block_start.isoformat(),
            "block_end": block_end.isoformat() if block_end else None,
        }

    return (is_active, attrs)


def _is_tomorrow_cheapest_3h_block_active(
    data: dict[str, Any],
) -> tuple[bool, dict[str, Any] | None]:
    """Check if tomorrow's cheapest 3-hour block is currently active.

    Returns:
        Tuple of (is_active, attributes_dict)
    """
    now = dt_util.now()
    tomorrow_slots = data.get("tomorrow_slots", [])

    # If tomorrow slots are not available, return unavailable state
    if not tomorrow_slots:
        return (False, None)

    # Always calculate the block start/end for attributes, even if we're not in tomorrow yet
    block_start = _get_cheapest_3h_block(tomorrow_slots)
    if not block_start:
        return (False, None)

    # Calculate end time (start + 3 hours)
    block_end = block_start + timedelta(hours=3)

    # Check if we're already in tomorrow (after midnight)
    # Use dt_util.start_of_local_day() for DST-safe midnight calculation
    today_start = dt_util.start_of_local_day()
    tomorrow_start = today_start + timedelta(days=1)

    # Only check if we're in tomorrow AND within the block
    is_active = False
    if now >= tomorrow_start:
        is_active = block_start <= now < block_end

    # Always return attributes if block_start is found
    attrs = {
        "block_start": block_start.isoformat(),
        "block_end": block_end.isoformat() if block_end else None,
    }

    return (is_active, attrs)


BINARY_SENSORS: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key="cheapest_3h_block_today_active",
        translation_key="cheapest_3h_block_today_active",
        device_class=BinarySensorDeviceClass.POWER,
    ),
    BinarySensorEntityDescription(
        key="cheapest_3h_block_tomorrow_active",
        translation_key="cheapest_3h_block_tomorrow_active",
        device_class=BinarySensorDeviceClass.POWER,
    ),
    BinarySensorEntityDescription(
        key="cheapest_4h_block_today_active",
        translation_key="cheapest_4h_block_today_active",
        device_class=BinarySensorDeviceClass.POWER,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ostrom binary sensors from a config entry."""
    LOGGER.info("Setting up Ostrom Advanced binary sensors for entry %s", entry.entry_id)

    data = hass.data[DOMAIN][entry.entry_id]
    price_coordinator: OstromPriceCoordinator = data["price_coordinator"]
    contract_id = entry.data.get(CONF_CONTRACT_ID, "") or entry.data.get(CONF_ZIP_CODE, "")

    entities: list[BinarySensorEntity] = []

    # Add binary sensors
    LOGGER.info("Creating %d binary sensors", len(BINARY_SENSORS))
    for description in BINARY_SENSORS:
        entities.append(
            OstromCheapest3hBlockBinarySensor(
                coordinator=price_coordinator,
                description=description,
                contract_id=contract_id,
            )
        )

    LOGGER.info("Adding %d binary sensor entities to Home Assistant", len(entities))
    async_add_entities(entities)
    LOGGER.info("Successfully added %d Ostrom Advanced binary sensor entities", len(entities))


class OstromCheapest3hBlockBinarySensor(
    CoordinatorEntity[OstromPriceCoordinator], BinarySensorEntity
):
    """Representation of an Ostrom cheapest 3h block binary sensor."""

    entity_description: BinarySensorEntityDescription
    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: OstromPriceCoordinator,
        description: BinarySensorEntityDescription,
        contract_id: str,
    ) -> None:
        """Initialize the binary sensor."""
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
    def is_on(self) -> bool | None:
        """Return the state of the binary sensor."""
        if self.coordinator.data is None:
            return None

        if self.entity_description.key == "cheapest_3h_block_today_active":
            is_active, _ = _is_today_cheapest_3h_block_active(self.coordinator.data)
            return is_active
        elif self.entity_description.key == "cheapest_3h_block_tomorrow_active":
            is_active, _ = _is_tomorrow_cheapest_3h_block_active(self.coordinator.data)
            return is_active
        elif self.entity_description.key == "cheapest_4h_block_today_active":
            is_active, _ = _is_today_cheapest_4h_block_active(self.coordinator.data)
            return is_active

        return None

    @property
    def icon(self) -> str | None:
        """Return the icon for the binary sensor."""
        if self.is_on:
            return "mdi:toggle-switch"
        return "mdi:toggle-switch-off"

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if self.coordinator.data is None:
            return None

        if self.entity_description.key == "cheapest_3h_block_today_active":
            _, attrs = _is_today_cheapest_3h_block_active(self.coordinator.data)
            return attrs
        elif self.entity_description.key == "cheapest_3h_block_tomorrow_active":
            _, attrs = _is_tomorrow_cheapest_3h_block_active(self.coordinator.data)
            return attrs
        elif self.entity_description.key == "cheapest_4h_block_today_active":
            _, attrs = _is_today_cheapest_4h_block_active(self.coordinator.data)
            return attrs

        return None

