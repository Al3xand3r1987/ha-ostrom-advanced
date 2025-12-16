"""Tests for coordinator classes."""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.ostrom_advanced.api import OstromApiClient, OstromApiError, OstromAuthError
from custom_components.ostrom_advanced.coordinator import (
    OstromConsumptionCoordinator,
    OstromPriceCoordinator,
)


@pytest.fixture
def mock_api_client() -> MagicMock:
    """Create a mock API client."""
    client = MagicMock(spec=OstromApiClient)
    client.async_get_spot_prices = AsyncMock()
    client.async_get_energy_consumption = AsyncMock()
    return client


@pytest.fixture
def mock_hass() -> MagicMock:
    """Create a mock Home Assistant instance."""
    hass = MagicMock(spec=HomeAssistant)
    hass.loop = MagicMock()
    hass.loop.call_later = MagicMock(return_value=MagicMock())
    hass.async_create_task = MagicMock()
    return hass


class TestOstromPriceCoordinator:
    """Tests for OstromPriceCoordinator."""

    @pytest.mark.asyncio
    async def test_update_data_success(
        self, mock_hass: MagicMock, mock_api_client: MagicMock
    ) -> None:
        """Test successful data update."""
        # Mock current time
        now = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        with patch("custom_components.ostrom_advanced.coordinator.dt_util.now", return_value=now):
            with patch(
                "custom_components.ostrom_advanced.coordinator.dt_util.start_of_local_day",
                return_value=now.replace(hour=0, minute=0, second=0, microsecond=0),
            ):
                coordinator = OstromPriceCoordinator(
                    hass=mock_hass,
                    client=mock_api_client,
                    poll_interval_minutes=15,
                    update_offset_seconds=15,
                )

                # Mock API response
                mock_api_client.async_get_spot_prices.return_value = [
                    {
                        "date": "2024-01-15T10:00:00.000Z",
                        "grossKwhPrice": 1500,
                        "grossKwhTaxAndLevies": 500,
                        "netKwhPrice": 1000,
                    },
                    {
                        "date": "2024-01-15T11:00:00.000Z",
                        "grossKwhPrice": 2000,
                        "grossKwhTaxAndLevies": 600,
                        "netKwhPrice": 1400,
                    },
                ]

                result = await coordinator._async_update_data()

                assert "yesterday_slots" in result
                assert "today_slots" in result
                assert "tomorrow_slots" in result
                assert "current_slot" in result
                assert "last_update" in result

    @pytest.mark.asyncio
    async def test_update_data_auth_error(
        self, mock_hass: MagicMock, mock_api_client: MagicMock
    ) -> None:
        """Test update data with authentication error."""
        now = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        with patch("custom_components.ostrom_advanced.coordinator.dt_util.now", return_value=now):
            with patch(
                "custom_components.ostrom_advanced.coordinator.dt_util.start_of_local_day",
                return_value=now.replace(hour=0, minute=0, second=0, microsecond=0),
            ):
                coordinator = OstromPriceCoordinator(
                    hass=mock_hass,
                    client=mock_api_client,
                    poll_interval_minutes=15,
                    update_offset_seconds=15,
                )

                mock_api_client.async_get_spot_prices.side_effect = OstromAuthError(
                    "Invalid credentials"
                )

                with pytest.raises(UpdateFailed, match="Authentication error"):
                    await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_update_data_api_error(
        self, mock_hass: MagicMock, mock_api_client: MagicMock
    ) -> None:
        """Test update data with API error."""
        now = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        with patch("custom_components.ostrom_advanced.coordinator.dt_util.now", return_value=now):
            with patch(
                "custom_components.ostrom_advanced.coordinator.dt_util.start_of_local_day",
                return_value=now.replace(hour=0, minute=0, second=0, microsecond=0),
            ):
                coordinator = OstromPriceCoordinator(
                    hass=mock_hass,
                    client=mock_api_client,
                    poll_interval_minutes=15,
                    update_offset_seconds=15,
                )

                mock_api_client.async_get_spot_prices.side_effect = OstromApiError("API error")

                with pytest.raises(UpdateFailed, match="API error"):
                    await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_update_data_empty_response(
        self, mock_hass: MagicMock, mock_api_client: MagicMock
    ) -> None:
        """Test update data with empty API response."""
        now = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        with patch("custom_components.ostrom_advanced.coordinator.dt_util.now", return_value=now):
            with patch(
                "custom_components.ostrom_advanced.coordinator.dt_util.start_of_local_day",
                return_value=now.replace(hour=0, minute=0, second=0, microsecond=0),
            ):
                coordinator = OstromPriceCoordinator(
                    hass=mock_hass,
                    client=mock_api_client,
                    poll_interval_minutes=15,
                    update_offset_seconds=15,
                )

                mock_api_client.async_get_spot_prices.return_value = []

                result = await coordinator._async_update_data()

                assert result["yesterday_slots"] == []
                assert result["today_slots"] == []
                assert result["tomorrow_slots"] == []

    @pytest.mark.asyncio
    async def test_update_data_missing_tomorrow_prices(
        self, mock_hass: MagicMock, mock_api_client: MagicMock
    ) -> None:
        """Test update data when tomorrow prices are not available."""
        now = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        with patch("custom_components.ostrom_advanced.coordinator.dt_util.now", return_value=now):
            with patch(
                "custom_components.ostrom_advanced.coordinator.dt_util.start_of_local_day",
                return_value=now.replace(hour=0, minute=0, second=0, microsecond=0),
            ):
                coordinator = OstromPriceCoordinator(
                    hass=mock_hass,
                    client=mock_api_client,
                    poll_interval_minutes=15,
                    update_offset_seconds=15,
                )

                # Only return today's prices
                mock_api_client.async_get_spot_prices.return_value = [
                    {
                        "date": "2024-01-15T10:00:00.000Z",
                        "grossKwhPrice": 1500,
                        "grossKwhTaxAndLevies": 500,
                        "netKwhPrice": 1000,
                    },
                ]

                result = await coordinator._async_update_data()

                assert len(result["tomorrow_slots"]) == 0


class TestOstromConsumptionCoordinator:
    """Tests for OstromConsumptionCoordinator."""

    @pytest.mark.asyncio
    async def test_update_data_success(
        self, mock_hass: MagicMock, mock_api_client: MagicMock
    ) -> None:
        """Test successful consumption data update."""
        now = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        with patch("custom_components.ostrom_advanced.coordinator.dt_util.now", return_value=now):
            with patch(
                "custom_components.ostrom_advanced.coordinator.dt_util.start_of_local_day",
                return_value=now.replace(hour=0, minute=0, second=0, microsecond=0),
            ):
                coordinator = OstromConsumptionCoordinator(
                    hass=mock_hass,
                    client=mock_api_client,
                    poll_interval_minutes=60,
                    update_offset_seconds=15,
                )

                mock_api_client.async_get_energy_consumption.return_value = [
                    {
                        "date": "2024-01-15T10:00:00.000Z",
                        "kWh": 1.5,
                    },
                    {
                        "date": "2024-01-15T11:00:00.000Z",
                        "kWh": 2.0,
                    },
                ]

                result = await coordinator._async_update_data()

                assert "yesterday" in result
                assert "today" in result
                assert "last_update" in result

    @pytest.mark.asyncio
    async def test_update_data_empty_response(
        self, mock_hass: MagicMock, mock_api_client: MagicMock
    ) -> None:
        """Test consumption update with empty response."""
        now = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        with patch("custom_components.ostrom_advanced.coordinator.dt_util.now", return_value=now):
            with patch(
                "custom_components.ostrom_advanced.coordinator.dt_util.start_of_local_day",
                return_value=now.replace(hour=0, minute=0, second=0, microsecond=0),
            ):
                coordinator = OstromConsumptionCoordinator(
                    hass=mock_hass,
                    client=mock_api_client,
                    poll_interval_minutes=60,
                    update_offset_seconds=15,
                )

                mock_api_client.async_get_energy_consumption.return_value = []

                result = await coordinator._async_update_data()

                assert result["yesterday"] == []
                assert result["today"] == []

    @pytest.mark.asyncio
    async def test_update_data_auth_error(
        self, mock_hass: MagicMock, mock_api_client: MagicMock
    ) -> None:
        """Test consumption update with authentication error."""
        now = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        with patch("custom_components.ostrom_advanced.coordinator.dt_util.now", return_value=now):
            with patch(
                "custom_components.ostrom_advanced.coordinator.dt_util.start_of_local_day",
                return_value=now.replace(hour=0, minute=0, second=0, microsecond=0),
            ):
                coordinator = OstromConsumptionCoordinator(
                    hass=mock_hass,
                    client=mock_api_client,
                    poll_interval_minutes=60,
                    update_offset_seconds=15,
                )

                mock_api_client.async_get_energy_consumption.side_effect = OstromAuthError(
                    "Invalid credentials"
                )

                with pytest.raises(UpdateFailed, match="Authentication error"):
                    await coordinator._async_update_data()

