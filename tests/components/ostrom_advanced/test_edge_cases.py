"""Tests for edge cases and error handling."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiohttp import ClientConnectorError

from custom_components.ostrom_advanced.api import OstromApiClient, OstromApiError
from custom_components.ostrom_advanced.sensor import (
    _get_avg_price,
    _get_cheapest_3h_block,
    _get_median_price,
    _get_min_price,
)


class TestEdgeCasesSensorCalculations:
    """Tests for edge cases in sensor calculations."""

    def test_min_price_with_none_values(self) -> None:
        """Test min price with None values in slots."""
        slots = [
            {"total_price": 0.25},
            {"total_price": None},  # None value
            {"total_price": 0.15},
        ]
        # get() returns None, which becomes 0 in the list comprehension
        result = _get_min_price(slots)
        assert result == 0.0  # min([0.25, 0, 0.15]) = 0.0

    def test_avg_price_with_zero_values(self) -> None:
        """Test average price with zero values."""
        slots = [
            {"total_price": 0.0},
            {"total_price": 0.0},
            {"total_price": 0.0},
        ]
        result = _get_avg_price(slots)
        assert result == 0.0

    def test_median_price_single_value(self) -> None:
        """Test median price with single value."""
        slots = [{"total_price": 0.25}]
        result = _get_median_price(slots)
        assert result == 0.25

    def test_median_price_two_values(self) -> None:
        """Test median price with two values (even count)."""
        slots = [
            {"total_price": 0.10},
            {"total_price": 0.30},
        ]
        result = _get_median_price(slots)
        assert result == 0.20  # (0.10 + 0.30) / 2

    def test_cheapest_3h_block_with_identical_prices(self) -> None:
        """Test cheapest 3h block when all prices are identical."""
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        slots = [
            {"total_price": 0.20, "start": start_time},
            {"total_price": 0.20, "start": start_time.replace(hour=11)},
            {"total_price": 0.20, "start": start_time.replace(hour=12)},
            {"total_price": 0.20, "start": start_time.replace(hour=13)},
        ]
        result = _get_cheapest_3h_block(slots)
        # Should return the first block
        assert result == start_time

    def test_empty_slots_list(self) -> None:
        """Test functions with empty slots list."""
        slots: list[dict] = []
        assert _get_min_price(slots) is None
        assert _get_avg_price(slots) is None
        assert _get_median_price(slots) is None
        assert _get_cheapest_3h_block(slots) is None


class TestEdgeCasesAPI:
    """Tests for edge cases in API client."""

    @pytest.mark.asyncio
    async def test_api_empty_response_data(self) -> None:
        """Test API with empty response data."""
        mock_hass = MagicMock()
        mock_session = AsyncMock()

        client = OstromApiClient(
            hass=mock_hass,
            session=mock_session,
            environment="sandbox",
            client_id="test_id",
            client_secret="test_secret",
            contract_id="test_contract",
            zip_code="12345",
        )

        # Mock authentication
        mock_auth_response = AsyncMock()
        mock_auth_response.status = 200
        mock_auth_response.json = AsyncMock(
            return_value={"access_token": "test_token", "expires_in": 3600}
        )
        mock_auth_response.text = AsyncMock(return_value="")

        # Mock empty spot prices response
        mock_spot_response = AsyncMock()
        mock_spot_response.status = 200
        mock_spot_response.json = AsyncMock(return_value={"data": []})  # Empty data

        async def mock_post(*args, **kwargs):
            mock = AsyncMock()
            mock.__aenter__ = AsyncMock(return_value=mock_auth_response)
            mock.__aexit__ = AsyncMock(return_value=None)
            return mock

        async def mock_request(*args, **kwargs):
            mock = AsyncMock()
            mock.__aenter__ = AsyncMock(return_value=mock_spot_response)
            mock.__aexit__ = AsyncMock(return_value=None)
            return mock

        mock_session.post = AsyncMock(side_effect=mock_post)
        mock_session.request = AsyncMock(side_effect=mock_request)

        start = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        result = await client.async_get_spot_prices(start, end)
        assert result == []

    @pytest.mark.asyncio
    async def test_api_missing_data_field(self) -> None:
        """Test API with missing data field in response."""
        mock_hass = MagicMock()
        mock_session = AsyncMock()

        client = OstromApiClient(
            hass=mock_hass,
            session=mock_session,
            environment="sandbox",
            client_id="test_id",
            client_secret="test_secret",
            contract_id="test_contract",
            zip_code="12345",
        )

        # Mock authentication
        mock_auth_response = AsyncMock()
        mock_auth_response.status = 200
        mock_auth_response.json = AsyncMock(
            return_value={"access_token": "test_token", "expires_in": 3600}
        )
        mock_auth_response.text = AsyncMock(return_value="")

        # Mock response without 'data' field
        mock_spot_response = AsyncMock()
        mock_spot_response.status = 200
        mock_spot_response.json = AsyncMock(return_value={})  # Missing 'data'

        async def mock_post(*args, **kwargs):
            mock = AsyncMock()
            mock.__aenter__ = AsyncMock(return_value=mock_auth_response)
            mock.__aexit__ = AsyncMock(return_value=None)
            return mock

        async def mock_request(*args, **kwargs):
            mock = AsyncMock()
            mock.__aenter__ = AsyncMock(return_value=mock_spot_response)
            mock.__aexit__ = AsyncMock(return_value=None)
            return mock

        mock_session.post = AsyncMock(side_effect=mock_post)
        mock_session.request = AsyncMock(side_effect=mock_request)

        start = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        with pytest.raises(
            OstromApiError, match="Invalid response structure: missing data"
        ):
            await client.async_get_spot_prices(start, end)

    @pytest.mark.asyncio
    async def test_api_rate_limit_429(self) -> None:
        """Test API with rate limit error (429)."""
        mock_hass = MagicMock()
        mock_session = AsyncMock()

        client = OstromApiClient(
            hass=mock_hass,
            session=mock_session,
            environment="sandbox",
            client_id="test_id",
            client_secret="test_secret",
            contract_id="test_contract",
            zip_code="12345",
        )

        # Mock authentication
        mock_auth_response = AsyncMock()
        mock_auth_response.status = 200
        mock_auth_response.json = AsyncMock(
            return_value={"access_token": "test_token", "expires_in": 3600}
        )
        mock_auth_response.text = AsyncMock(return_value="")

        # Mock 429 response
        mock_429_response = AsyncMock()
        mock_429_response.status = 429
        mock_429_response.text = AsyncMock(return_value="Too Many Requests")

        async def mock_post(*args, **kwargs):
            mock = AsyncMock()
            mock.__aenter__ = AsyncMock(return_value=mock_auth_response)
            mock.__aexit__ = AsyncMock(return_value=None)
            return mock

        async def mock_request(*args, **kwargs):
            mock = AsyncMock()
            mock.__aenter__ = AsyncMock(return_value=mock_429_response)
            mock.__aexit__ = AsyncMock(return_value=None)
            return mock

        mock_session.post = AsyncMock(side_effect=mock_post)
        mock_session.request = AsyncMock(side_effect=mock_request)

        start = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        with pytest.raises(OstromApiError, match="Rate limit exceeded"):
            await client.async_get_spot_prices(start, end)

    @pytest.mark.asyncio
    async def test_api_network_timeout(self) -> None:
        """Test API with network timeout."""
        mock_hass = MagicMock()
        mock_session = AsyncMock()

        client = OstromApiClient(
            hass=mock_hass,
            session=mock_session,
            environment="sandbox",
            client_id="test_id",
            client_secret="test_secret",
            contract_id="test_contract",
            zip_code="12345",
        )

        # Mock authentication
        mock_auth_response = AsyncMock()
        mock_auth_response.status = 200
        mock_auth_response.json = AsyncMock(
            return_value={"access_token": "test_token", "expires_in": 3600}
        )
        mock_auth_response.text = AsyncMock(return_value="")

        async def mock_post(*args, **kwargs):
            mock = AsyncMock()
            mock.__aenter__ = AsyncMock(return_value=mock_auth_response)
            mock.__aexit__ = AsyncMock(return_value=None)
            return mock

        # Mock timeout on request
        import asyncio

        async def mock_request(*args, **kwargs):
            raise asyncio.TimeoutError()

        mock_session.post = AsyncMock(side_effect=mock_post)
        mock_session.request = AsyncMock(side_effect=mock_request)

        start = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        with pytest.raises(OstromApiError, match="Request timeout"):
            await client.async_get_spot_prices(start, end)

    @pytest.mark.asyncio
    async def test_api_connection_error(self) -> None:
        """Test API with connection error."""
        mock_hass = MagicMock()
        mock_session = AsyncMock()

        client = OstromApiClient(
            hass=mock_hass,
            session=mock_session,
            environment="sandbox",
            client_id="test_id",
            client_secret="test_secret",
            contract_id="test_contract",
            zip_code="12345",
        )

        # Mock authentication
        mock_auth_response = AsyncMock()
        mock_auth_response.status = 200
        mock_auth_response.json = AsyncMock(
            return_value={"access_token": "test_token", "expires_in": 3600}
        )
        mock_auth_response.text = AsyncMock(return_value="")

        async def mock_post(*args, **kwargs):
            mock = AsyncMock()
            mock.__aenter__ = AsyncMock(return_value=mock_auth_response)
            mock.__aexit__ = AsyncMock(return_value=None)
            return mock

        # Mock connection error
        async def mock_request(*args, **kwargs):
            raise ClientConnectorError(request_info=MagicMock(), history=MagicMock())

        mock_session.post = AsyncMock(side_effect=mock_post)
        mock_session.request = AsyncMock(side_effect=mock_request)

        start = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        with pytest.raises(OstromApiError, match="Network error"):
            await client.async_get_spot_prices(start, end)
