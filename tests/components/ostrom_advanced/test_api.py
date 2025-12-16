"""Tests for API client functions."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest
from aiohttp import ClientConnectorError

from custom_components.ostrom_advanced.api import (
    OstromApiClient,
    OstromApiError,
    OstromAuthError,
)
from custom_components.ostrom_advanced.const import (
    ENDPOINT_OAUTH_TOKEN,
)


@pytest.fixture
def mock_hass() -> MagicMock:
    """Create a mock Home Assistant instance."""
    return MagicMock()


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create a mock aiohttp session."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    return session


@pytest.fixture
def api_client(mock_hass: MagicMock, mock_session: AsyncMock) -> OstromApiClient:
    """Create an API client instance for testing."""
    return OstromApiClient(
        hass=mock_hass,
        session=mock_session,
        environment="sandbox",
        client_id="test_client_id",
        client_secret="test_client_secret",
        contract_id="test_contract_id",
        zip_code="12345",
    )


class TestAsyncAuthenticate:
    """Tests for async_authenticate function."""

    @pytest.mark.asyncio
    async def test_authenticate_success(
        self, api_client: OstromApiClient, mock_session: AsyncMock
    ) -> None:
        """Test successful authentication."""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "access_token": "test_access_token",
                "expires_in": 3600,
                "token_type": "Bearer",
            }
        )
        mock_response.text = AsyncMock(return_value="")

        mock_session.post.return_value.__aenter__.return_value = mock_response

        await api_client.async_authenticate()

        # Verify token was stored
        assert api_client._access_token == "test_access_token"
        assert api_client._token_expires_at is not None

        # Verify request was made correctly
        mock_session.post.assert_called_once()
        call_args = mock_session.post.call_args
        assert ENDPOINT_OAUTH_TOKEN in call_args[0][0]

    @pytest.mark.asyncio
    async def test_authenticate_401_invalid_credentials(
        self, api_client: OstromApiClient, mock_session: AsyncMock
    ) -> None:
        """Test authentication with invalid credentials (401)."""
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.text = AsyncMock(return_value="Unauthorized")

        mock_session.post.return_value.__aenter__.return_value = mock_response

        with pytest.raises(OstromAuthError, match="Invalid client credentials"):
            await api_client.async_authenticate()

    @pytest.mark.asyncio
    async def test_authenticate_400_bad_request(
        self, api_client: OstromApiClient, mock_session: AsyncMock
    ) -> None:
        """Test authentication with bad request (400)."""
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.text = AsyncMock(return_value="Bad Request")

        mock_session.post.return_value.__aenter__.return_value = mock_response

        with pytest.raises(OstromApiError, match="Bad request"):
            await api_client.async_authenticate()

    @pytest.mark.asyncio
    async def test_authenticate_429_rate_limit(
        self, api_client: OstromApiClient, mock_session: AsyncMock
    ) -> None:
        """Test authentication with rate limit (429)."""
        mock_response = AsyncMock()
        mock_response.status = 429
        mock_response.text = AsyncMock(return_value="Too Many Requests")

        mock_session.post.return_value.__aenter__.return_value = mock_response

        with pytest.raises(OstromApiError, match="Rate limit exceeded"):
            await api_client.async_authenticate()

    @pytest.mark.asyncio
    async def test_authenticate_network_error(
        self, api_client: OstromApiClient, mock_session: AsyncMock
    ) -> None:
        """Test authentication with network error."""
        # Create a connection key for ClientConnectorError
        from aiohttp.client_reqrep import ConnectionKey
        conn_key = ConnectionKey(host='test', port=443, is_ssl=True, ssl=None, proxy=None, proxy_auth=None, proxy_headers_hash=None)
        mock_session.post.side_effect = ClientConnectorError(conn_key, OSError())

        with pytest.raises(OstromApiError, match="Network error"):
            await api_client.async_authenticate()

    @pytest.mark.asyncio
    async def test_authenticate_timeout(
        self, api_client: OstromApiClient, mock_session: AsyncMock
    ) -> None:
        """Test authentication with timeout."""
        mock_session.post.side_effect = asyncio.TimeoutError()

        with pytest.raises(OstromApiError, match="Authentication request timeout"):
            await api_client.async_authenticate()

    @pytest.mark.asyncio
    async def test_authenticate_unexpected_status(
        self, api_client: OstromApiClient, mock_session: AsyncMock
    ) -> None:
        """Test authentication with unexpected status code."""
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")

        mock_session.post.return_value.__aenter__.return_value = mock_response

        with pytest.raises(
            OstromApiError, match="Authentication failed with status 500"
        ):
            await api_client.async_authenticate()


class TestAsyncGetSpotPrices:
    """Tests for async_get_spot_prices function."""

    @pytest.mark.asyncio
    async def test_get_spot_prices_success(
        self, api_client: OstromApiClient, mock_session: AsyncMock
    ) -> None:
        """Test successful spot prices retrieval."""
        # First authenticate
        mock_auth_response = AsyncMock()
        mock_auth_response.status = 200
        mock_auth_response.json = AsyncMock(
            return_value={
                "access_token": "test_token",
                "expires_in": 3600,
            }
        )
        mock_auth_response.text = AsyncMock(return_value="")

        # Mock spot prices response
        mock_spot_response = AsyncMock()
        mock_spot_response.status = 200
        mock_spot_response.json = AsyncMock(
            return_value={
                "data": [
                    {
                        "date": "2024-01-01T10:00:00.000Z",
                        "grossKwhPrice": 1500,  # 15.00 EUR in cents
                        "grossKwhTaxAndLevies": 500,  # 5.00 EUR in cents
                        "netKwhPrice": 1000,
                    },
                    {
                        "date": "2024-01-01T11:00:00.000Z",
                        "grossKwhPrice": 2000,
                        "grossKwhTaxAndLevies": 600,
                        "netKwhPrice": 1400,
                    },
                ]
            }
        )

        # Setup mock to return different responses for auth and spot prices
        class MockContextManager:
            def __init__(self, return_value):
                self.return_value = return_value
            
            async def __aenter__(self):
                return self.return_value
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return None

        mock_session.post = MagicMock(return_value=MockContextManager(mock_auth_response))
        mock_session.request = MagicMock(return_value=MockContextManager(mock_spot_response))

        start = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        result = await api_client.async_get_spot_prices(start, end)

        assert len(result) == 2
        assert result[0]["total_price"] == 20.0  # (1500 + 500) / 100
        assert result[1]["total_price"] == 26.0  # (2000 + 600) / 100
        assert result[0]["net_price"] == 10.0  # 1000 / 100

    @pytest.mark.asyncio
    async def test_get_spot_prices_missing_data(
        self, api_client: OstromApiClient, mock_session: AsyncMock
    ) -> None:
        """Test spot prices with missing data field."""
        # Authenticate first
        mock_auth_response = AsyncMock()
        mock_auth_response.status = 200
        mock_auth_response.json = AsyncMock(
            return_value={"access_token": "test_token", "expires_in": 3600}
        )
        mock_auth_response.text = AsyncMock(return_value="")

        mock_spot_response = AsyncMock()
        mock_spot_response.status = 200
        mock_spot_response.json = AsyncMock(return_value={})  # Missing 'data' field

        class MockContextManager:
            def __init__(self, return_value):
                self.return_value = return_value
            
            async def __aenter__(self):
                return self.return_value
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return None

        mock_session.post = MagicMock(return_value=MockContextManager(mock_auth_response))
        mock_session.request = MagicMock(return_value=MockContextManager(mock_spot_response))

        start = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        with pytest.raises(
            OstromApiError, match="Invalid response structure: missing data"
        ):
            await api_client.async_get_spot_prices(start, end)

    @pytest.mark.asyncio
    async def test_get_spot_prices_401_retry(
        self, api_client: OstromApiClient, mock_session: AsyncMock
    ) -> None:
        """Test spot prices with 401 that triggers token refresh."""
        # First auth
        mock_auth_response = AsyncMock()
        mock_auth_response.status = 200
        mock_auth_response.json = AsyncMock(
            return_value={"access_token": "test_token", "expires_in": 3600}
        )
        mock_auth_response.text = AsyncMock(return_value="")

        # First request returns 401, then retry succeeds
        mock_401_response = AsyncMock()
        mock_401_response.status = 401
        mock_401_response.text = AsyncMock(return_value="Unauthorized")

        mock_success_response = AsyncMock()
        mock_success_response.status = 200
        mock_success_response.json = AsyncMock(
            return_value={
                "data": [
                    {
                        "date": "2024-01-01T10:00:00.000Z",
                        "grossKwhPrice": 1500,
                        "grossKwhTaxAndLevies": 500,
                        "netKwhPrice": 1000,
                    }
                ]
            }
        )
        mock_success_response.raise_for_status = AsyncMock()

        class MockContextManager:
            def __init__(self, return_value):
                self.return_value = return_value
            
            async def __aenter__(self):
                return self.return_value
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return None

        class MockRequestContextManager:
            def __init__(self):
                self.count = 0
            
            async def __aenter__(self):
                if self.count == 0:
                    self.count += 1
                    return mock_401_response
                else:
                    return mock_success_response
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return None

        mock_session.post = MagicMock(return_value=MockContextManager(mock_auth_response))
        mock_session.request = MagicMock(return_value=MockRequestContextManager())

        start = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        result = await api_client.async_get_spot_prices(start, end)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_spot_prices_404(
        self, api_client: OstromApiClient, mock_session: AsyncMock
    ) -> None:
        """Test spot prices with 404 error."""
        # Authenticate first
        mock_auth_response = AsyncMock()
        mock_auth_response.status = 200
        mock_auth_response.json = AsyncMock(
            return_value={"access_token": "test_token", "expires_in": 3600}
        )
        mock_auth_response.text = AsyncMock(return_value="")

        mock_404_response = AsyncMock()
        mock_404_response.status = 404
        mock_404_response.text = AsyncMock(return_value="Not Found")

        class MockContextManager:
            def __init__(self, return_value):
                self.return_value = return_value
            
            async def __aenter__(self):
                return self.return_value
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return None

        mock_session.post = MagicMock(return_value=MockContextManager(mock_auth_response))
        mock_session.request = MagicMock(return_value=MockContextManager(mock_404_response))

        start = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        with pytest.raises(OstromApiError) as exc_info:
            await api_client.async_get_spot_prices(start, end)
        assert exc_info.value.status_code == 404


class TestAsyncGetEnergyConsumption:
    """Tests for async_get_energy_consumption function."""

    @pytest.mark.asyncio
    async def test_get_energy_consumption_success(
        self, api_client: OstromApiClient, mock_session: AsyncMock
    ) -> None:
        """Test successful energy consumption retrieval."""
        # Authenticate first
        mock_auth_response = AsyncMock()
        mock_auth_response.status = 200
        mock_auth_response.json = AsyncMock(
            return_value={"access_token": "test_token", "expires_in": 3600}
        )
        mock_auth_response.text = AsyncMock(return_value="")

        mock_consumption_response = AsyncMock()
        mock_consumption_response.status = 200
        mock_consumption_response.json = AsyncMock(
            return_value={
                "data": [
                    {
                        "date": "2024-01-01T10:00:00.000Z",
                        "kWh": 1.5,
                    },
                    {
                        "date": "2024-01-01T11:00:00.000Z",
                        "kWh": 2.0,
                    },
                ]
            }
        )

        class MockContextManager:
            def __init__(self, return_value):
                self.return_value = return_value
            
            async def __aenter__(self):
                return self.return_value
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return None

        mock_session.post = MagicMock(return_value=MockContextManager(mock_auth_response))
        mock_session.request = MagicMock(return_value=MockContextManager(mock_consumption_response))

        start = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        result = await api_client.async_get_energy_consumption(start, end)

        assert len(result) == 2
        assert result[0]["kWh"] == 1.5
        assert result[1]["kWh"] == 2.0

    @pytest.mark.asyncio
    async def test_get_energy_consumption_404_returns_empty(
        self, api_client: OstromApiClient, mock_session: AsyncMock
    ) -> None:
        """Test energy consumption with 404 returns empty list."""
        # Authenticate first
        mock_auth_response = AsyncMock()
        mock_auth_response.status = 200
        mock_auth_response.json = AsyncMock(
            return_value={"access_token": "test_token", "expires_in": 3600}
        )
        mock_auth_response.text = AsyncMock(return_value="")

        # Create 404 error
        error = OstromApiError("Resource not found", status_code=404)

        class MockContextManager:
            def __init__(self, return_value):
                self.return_value = return_value
            
            async def __aenter__(self):
                return self.return_value
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return None

        class MockErrorContextManager:
            async def __aenter__(self):
                raise error
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return None

        mock_session.post = MagicMock(return_value=MockContextManager(mock_auth_response))
        mock_session.request = MagicMock(return_value=MockErrorContextManager())

        start = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        result = await api_client.async_get_energy_consumption(start, end)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_energy_consumption_missing_data(
        self, api_client: OstromApiClient, mock_session: AsyncMock
    ) -> None:
        """Test energy consumption with missing data field."""
        # Authenticate first
        mock_auth_response = AsyncMock()
        mock_auth_response.status = 200
        mock_auth_response.json = AsyncMock(
            return_value={"access_token": "test_token", "expires_in": 3600}
        )
        mock_auth_response.text = AsyncMock(return_value="")

        mock_consumption_response = AsyncMock()
        mock_consumption_response.status = 200
        mock_consumption_response.json = AsyncMock(return_value={})  # Missing 'data'

        class MockContextManager:
            def __init__(self, return_value):
                self.return_value = return_value
            
            async def __aenter__(self):
                return self.return_value
            
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                return None

        mock_session.post = MagicMock(return_value=MockContextManager(mock_auth_response))
        mock_session.request = MagicMock(return_value=MockContextManager(mock_consumption_response))

        start = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        with pytest.raises(
            OstromApiError, match="Invalid response structure: missing data"
        ):
            await api_client.async_get_energy_consumption(start, end)
