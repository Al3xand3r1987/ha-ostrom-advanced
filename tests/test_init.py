"""Tests for Ostrom Advanced integration setup."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ostrom_advanced import async_setup_entry
from custom_components.ostrom_advanced.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_CONTRACT_ID,
    CONF_ENVIRONMENT,
    CONF_ZIP_CODE,
    DOMAIN,
    ENV_SANDBOX,
)

TEST_ENTRY_DATA = {
    CONF_ENVIRONMENT: ENV_SANDBOX,
    CONF_CLIENT_ID: "test-client-id",
    CONF_CLIENT_SECRET: "test-client-secret",
    CONF_CONTRACT_ID: "",
    CONF_ZIP_CODE: "12345",
}


async def test_async_setup_entry(hass: HomeAssistant) -> None:
    """Verify async_setup_entry sets up the integration."""
    entry = MockConfigEntry(domain=DOMAIN, data=TEST_ENTRY_DATA)
    entry.add_to_hass(hass)

    with patch(
        "custom_components.ostrom_advanced.OstromPriceCoordinator.async_config_entry_first_refresh",
        new=AsyncMock(),
    ), patch.object(
        hass.config_entries,
        "async_forward_entry_setups",
        AsyncMock(return_value=True),
    ):
        result = await async_setup_entry(hass, entry)

    assert result is True
    assert DOMAIN in hass.data
    assert entry.entry_id in hass.data[DOMAIN]


async def test_config_entries_async_setup(hass: HomeAssistant) -> None:
    """Verify hass.config_entries.async_setup returns True."""
    entry = MockConfigEntry(domain=DOMAIN, data=TEST_ENTRY_DATA)
    entry.add_to_hass(hass)

    with patch(
        "custom_components.ostrom_advanced.OstromPriceCoordinator.async_config_entry_first_refresh",
        new=AsyncMock(),
    ), patch.object(
        hass.config_entries,
        "async_forward_entry_setups",
        AsyncMock(return_value=True),
    ):
        setup_result = await hass.config_entries.async_setup(entry.entry_id)

    assert setup_result is True
