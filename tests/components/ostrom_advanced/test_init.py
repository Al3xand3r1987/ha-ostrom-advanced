"""Tests for integration setup."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.ostrom_advanced import async_setup_entry, async_unload_entry
from custom_components.ostrom_advanced.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_CONTRACT_ID,
    CONF_ENVIRONMENT,
    CONF_ZIP_CODE,
    DOMAIN,
    ENV_PRODUCTION,
)


@pytest.fixture
def mock_config_entry() -> MagicMock:
    """Create a mock config entry."""
    entry = MagicMock(spec=ConfigEntry)
    entry.data = {
        CONF_ENVIRONMENT: ENV_PRODUCTION,
        CONF_CLIENT_ID: "test_client_id",
        CONF_CLIENT_SECRET: "test_secret",
        CONF_CONTRACT_ID: "test_contract",
        CONF_ZIP_CODE: "12345",
    }
    entry.options = {}
    entry.entry_id = "test_entry_id"
    return entry


@pytest.fixture
def mock_hass() -> MagicMock:
    """Create a mock Home Assistant instance."""
    hass = MagicMock(spec=HomeAssistant)
    hass.data = {}
    hass.config_entries = MagicMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    return hass


class TestAsyncSetupEntry:
    """Tests for async_setup_entry function."""

    @pytest.mark.asyncio
    async def test_setup_entry_success(
        self, mock_hass: MagicMock, mock_config_entry: MagicMock
    ) -> None:
        """Test successful integration setup."""
        with patch(
            "custom_components.ostrom_advanced.async_get_clientsession"
        ) as mock_session:
            with patch(
                "custom_components.ostrom_advanced.OstromApiClient"
            ) as mock_client_class:
                with patch(
                    "custom_components.ostrom_advanced.OstromPriceCoordinator"
                ) as mock_price_coord:
                    with patch(
                        "custom_components.ostrom_advanced.OstromConsumptionCoordinator"
                    ) as mock_consumption_coord:
                        # Setup mocks
                        mock_session.return_value = MagicMock()
                        mock_client = MagicMock()
                        mock_client_class.return_value = mock_client

                        mock_price_coord_instance = MagicMock()
                        mock_price_coord_instance.async_config_entry_first_refresh = (
                            AsyncMock()
                        )
                        mock_price_coord.return_value = mock_price_coord_instance

                        mock_consumption_coord_instance = MagicMock()
                        mock_consumption_coord_instance.async_config_entry_first_refresh = AsyncMock()
                        mock_consumption_coord.return_value = (
                            mock_consumption_coord_instance
                        )

                        result = await async_setup_entry(mock_hass, mock_config_entry)

                        assert result is True
                        assert DOMAIN in mock_hass.data
                        assert mock_config_entry.entry_id in mock_hass.data[DOMAIN]

    @pytest.mark.asyncio
    async def test_setup_entry_without_contract_id(
        self, mock_hass: MagicMock, mock_config_entry: MagicMock
    ) -> None:
        """Test setup entry without contract ID."""
        mock_config_entry.data[CONF_CONTRACT_ID] = ""

        with patch(
            "custom_components.ostrom_advanced.async_get_clientsession"
        ) as mock_session:
            with patch(
                "custom_components.ostrom_advanced.OstromApiClient"
            ) as mock_client_class:
                with patch(
                    "custom_components.ostrom_advanced.OstromPriceCoordinator"
                ) as mock_price_coord:
                    # Setup mocks
                    mock_session.return_value = MagicMock()
                    mock_client = MagicMock()
                    mock_client_class.return_value = mock_client

                    mock_price_coord_instance = MagicMock()
                    mock_price_coord_instance.async_config_entry_first_refresh = (
                        AsyncMock()
                    )
                    mock_price_coord.return_value = mock_price_coord_instance

                    result = await async_setup_entry(mock_hass, mock_config_entry)

                    assert result is True
                    # Consumption coordinator should not be created
                    data = mock_hass.data[DOMAIN][mock_config_entry.entry_id]
                    assert data.get("consumption_coordinator") is None

    @pytest.mark.asyncio
    async def test_setup_entry_price_fetch_fails(
        self, mock_hass: MagicMock, mock_config_entry: MagicMock
    ) -> None:
        """Test setup entry when price fetch fails."""
        with patch(
            "custom_components.ostrom_advanced.async_get_clientsession"
        ) as mock_session:
            with patch(
                "custom_components.ostrom_advanced.OstromApiClient"
            ) as mock_client_class:
                with patch(
                    "custom_components.ostrom_advanced.OstromPriceCoordinator"
                ) as mock_price_coord:
                    # Setup mocks
                    mock_session.return_value = MagicMock()
                    mock_client = MagicMock()
                    mock_client_class.return_value = mock_client

                    mock_price_coord_instance = MagicMock()
                    mock_price_coord_instance.async_config_entry_first_refresh = (
                        AsyncMock(side_effect=Exception("Fetch failed"))
                    )
                    mock_price_coord.return_value = mock_price_coord_instance

                    with pytest.raises(Exception):
                        await async_setup_entry(mock_hass, mock_config_entry)


class TestAsyncUnloadEntry:
    """Tests for async_unload_entry function."""

    @pytest.mark.asyncio
    async def test_unload_entry_success(
        self, mock_hass: MagicMock, mock_config_entry: MagicMock
    ) -> None:
        """Test successful entry unload."""
        # Setup data
        mock_hass.data[DOMAIN] = {mock_config_entry.entry_id: {}}

        result = await async_unload_entry(mock_hass, mock_config_entry)

        assert result is True
        assert mock_config_entry.entry_id not in mock_hass.data[DOMAIN]

    @pytest.mark.asyncio
    async def test_unload_entry_removes_domain_if_empty(
        self, mock_hass: MagicMock, mock_config_entry: MagicMock
    ) -> None:
        """Test that domain is removed when last entry is unloaded."""
        # Setup data with only one entry
        mock_hass.data[DOMAIN] = {mock_config_entry.entry_id: {}}

        result = await async_unload_entry(mock_hass, mock_config_entry)

        assert result is True
        assert DOMAIN not in mock_hass.data
