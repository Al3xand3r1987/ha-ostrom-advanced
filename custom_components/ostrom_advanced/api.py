"""Ostrom API Client for the Ostrom Advanced integration."""

from __future__ import annotations

import asyncio
import base64
from datetime import datetime, timedelta
from typing import Any

import aiohttp
from aiohttp import ClientConnectorError, ClientResponseError, ClientTimeout, FormData

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError

from .const import (
    API_BASE_URLS,
    AUTH_URLS,
    DEFAULT_TIMEOUT,
    ENDPOINT_ENERGY_CONSUMPTION,
    ENDPOINT_OAUTH_TOKEN,
    ENDPOINT_SPOT_PRICES,
    LOGGER,
    OAUTH_GRANT_TYPE,
    RESOLUTION_HOUR,
)


class OstromApiError(HomeAssistantError):
    """Exception for Ostrom API errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """Initialize the error.

        Args:
            message: Error message
            status_code: Optional HTTP status code
        """
        super().__init__(message)
        self.status_code = status_code


class OstromAuthError(ConfigEntryAuthFailed):
    """Exception for authentication errors."""

    def __init__(self, message: str = "Authentication failed") -> None:
        """Initialize the authentication error.

        Args:
            message: Error message
        """
        super().__init__(message)


class OstromApiClient:
    """Client for interacting with the Ostrom API."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: aiohttp.ClientSession,
        environment: str,
        client_id: str,
        client_secret: str,
        contract_id: str,
        zip_code: str,
    ) -> None:
        """Initialize the Ostrom API client.

        Args:
            hass: Home Assistant instance
            session: aiohttp ClientSession
            environment: "sandbox" or "production"
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            contract_id: Ostrom contract ID (optional, only needed for consumption)
            zip_code: German zip code for price lookups
        """
        self._hass = hass
        self._session = session
        self._environment = environment
        self._client_id = client_id
        self._client_secret = client_secret
        self._contract_id = contract_id
        self._zip_code = zip_code

        # Set URLs based on environment
        self._base_url = API_BASE_URLS[environment]
        self._auth_url = AUTH_URLS[environment]

        # Token storage
        self._access_token: str | None = None
        self._token_expires_at: datetime | None = None
        # Lock for token refresh to prevent race conditions
        self._token_lock = asyncio.Lock()

    @property
    def contract_id(self) -> str:
        """Return the contract ID."""
        return self._contract_id

    @property
    def zip_code(self) -> str:
        """Return the zip code."""
        return self._zip_code

    async def async_authenticate(self) -> None:
        """Obtain an OAuth2 access token using client credentials flow.

        Based on Ostrom API documentation:
        POST {auth_url}/oauth2/token
        - Basic Auth with client_id:client_secret
        - Form data: grant_type=client_credentials
        - Response: access_token, expires_in, token_type
        """
        url = f"{self._auth_url.rstrip('/')}{ENDPOINT_OAUTH_TOKEN}"

        # Create Basic Auth header
        credentials = f"{self._client_id}:{self._client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        # Use URL-encoded form data to match API expectations
        form_data = FormData()
        form_data.add_field("grant_type", OAUTH_GRANT_TYPE)

        LOGGER.debug("Requesting OAuth2 token from %s", url)
        LOGGER.debug(
            "OAuth2 request headers (sanitized): %s",
            {k: v for k, v in headers.items() if k != "Authorization"},
        )
        LOGGER.debug("OAuth2 request body: grant_type=%s", OAUTH_GRANT_TYPE)

        try:
            async with self._session.post(
                url,
                headers=headers,
                data=form_data,
                timeout=ClientTimeout(total=DEFAULT_TIMEOUT),
            ) as response:
                if response.status == 401:
                    LOGGER.error("Authentication failed: Invalid credentials")
                    raise OstromAuthError("Invalid client credentials")

                if response.status == 400:
                    error_text = await response.text()
                    LOGGER.error("Bad request during authentication: %s", error_text)
                    raise OstromApiError(f"Bad request: {error_text}")

                if response.status == 429:
                    LOGGER.error("Rate limit exceeded during authentication")
                    raise OstromApiError("Rate limit exceeded")

                # Accept both 200 (OK) and 201 (Created) as success
                if response.status not in (200, 201):
                    error_text = await response.text()
                    LOGGER.error(
                        "Unexpected error during authentication: %s - %s",
                        response.status,
                        error_text,
                    )
                    raise OstromApiError(
                        f"Authentication failed with status {response.status}"
                    )

                result = await response.json()

                self._access_token = result.get("access_token")
                expires_in = result.get("expires_in", 3600)

                # Set expiration with a 60 second buffer
                self._token_expires_at = datetime.now() + timedelta(
                    seconds=expires_in - 60
                )

                LOGGER.debug(
                    "Successfully obtained access token, expires in %s seconds",
                    expires_in,
                )

        except ClientConnectorError as err:
            LOGGER.error("Network connection error during authentication: %s", err)
            raise OstromApiError(f"Network error: {err}") from err
        except asyncio.TimeoutError as err:
            LOGGER.error("Authentication request timeout: %s", err)
            raise OstromApiError("Authentication request timeout") from err
        except ClientResponseError as err:
            LOGGER.error(
                "HTTP error during authentication: %s - %s", err.status, err.message
            )
            raise OstromApiError(f"HTTP error {err.status}: {err.message}") from err
        except aiohttp.ClientError as err:
            LOGGER.error("Connection error during authentication: %s", err)
            raise OstromApiError(f"Connection error: {err}") from err

    def _is_token_valid(self) -> bool:
        """Check if the current token is still valid."""
        if self._access_token is None or self._token_expires_at is None:
            return False
        return datetime.now() < self._token_expires_at

    async def _async_ensure_token(self) -> None:
        """Ensure we have a valid access token."""
        # Check without lock first (fast path)
        if self._is_token_valid():
            return

        # Acquire lock for token refresh to prevent race conditions
        async with self._token_lock:
            # Check again after acquiring lock (another request might have refreshed it)
            if not self._is_token_valid():
                await self.async_authenticate()

    async def _async_request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an authenticated API request.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            params: Query parameters
            json_data: JSON body data

        Returns:
            Response JSON data

        Raises:
            OstromApiError: On API errors
            OstromAuthError: On authentication errors
        """
        await self._async_ensure_token()

        url = f"{self._base_url.rstrip('/')}{path}"

        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Accept": "application/json",
        }

        LOGGER.debug("Making %s request to %s with params %s", method, url, params)
        LOGGER.debug(
            "Request headers (sanitized): %s",
            {k: v for k, v in headers.items() if k != "Authorization"},
        )

        try:
            async with self._session.request(
                method,
                url,
                headers=headers,
                params=params,
                json=json_data,
                timeout=ClientTimeout(total=DEFAULT_TIMEOUT),
            ) as response:
                if response.status == 401:
                    # Token might be expired, try to refresh
                    LOGGER.warning("Token expired, attempting to refresh")
                    self._access_token = None
                    # Use lock to prevent race conditions during token refresh
                    async with self._token_lock:
                        # Check again after acquiring lock
                        if not self._is_token_valid():
                            await self.async_authenticate()
                    # Retry the request once
                    headers["Authorization"] = f"Bearer {self._access_token}"
                    async with self._session.request(
                        method,
                        url,
                        headers=headers,
                        params=params,
                        json=json_data,
                        timeout=ClientTimeout(total=DEFAULT_TIMEOUT),
                    ) as retry_response:
                        if retry_response.status == 401:
                            raise OstromAuthError("Authentication failed after refresh")
                        retry_response.raise_for_status()
                        return await retry_response.json()

                if response.status == 400:
                    error_text = await response.text()
                    LOGGER.error("Bad request: %s", error_text)
                    raise OstromApiError(f"Bad request: {error_text}")

                if response.status == 404:
                    error_text = await response.text()
                    LOGGER.error("Resource not found: %s", error_text)
                    raise OstromApiError(
                        f"Resource not found: {error_text}", status_code=404
                    )

                if response.status == 429:
                    LOGGER.error("Rate limit exceeded")
                    raise OstromApiError("Rate limit exceeded")

                if response.status != 200:
                    error_text = await response.text()
                    LOGGER.error("API error: %s - %s", response.status, error_text)
                    raise OstromApiError(
                        f"API request failed with status {response.status}"
                    )

                return await response.json()

        except ClientConnectorError as err:
            LOGGER.error("Network connection error: %s", err)
            raise OstromApiError(f"Network error: {err}") from err
        except asyncio.TimeoutError as err:
            LOGGER.error("Request timeout: %s", err)
            raise OstromApiError("Request timeout") from err
        except ClientResponseError as err:
            LOGGER.error("HTTP error: %s - %s", err.status, err.message)
            raise OstromApiError(f"HTTP error {err.status}: {err.message}") from err
        except aiohttp.ClientError as err:
            LOGGER.error("Connection error: %s", err)
            raise OstromApiError(f"Connection error: {err}") from err

    async def async_get_spot_prices(
        self, start: datetime, end: datetime
    ) -> list[dict[str, Any]]:
        """Retrieve day-ahead spot price information.

        Based on Ostrom API documentation:
        GET /spot-prices
        Query params:
        - startDate: ISO format UTC (e.g., 2023-11-01T00:00:00.000Z)
        - endDate: ISO format UTC (e.g., 2023-11-02T00:00:00.000Z)
        - resolution: HOUR
        - zip: German zip code (optional, but needed for tax/levy data)

        Response data fields (per entry):
        - date: string (start of the slot)
        - netKwhPrice: number (cents, without VAT)
        - grossKwhPrice: number (cents, with VAT)
        - netKwhTaxAndLevies: number (cents, without VAT)
        - grossKwhTaxAndLevies: number (cents, with VAT)
        - netMwhPrice: number (EUR, without VAT)
        - netMonthlyOstromBaseFee, grossMonthlyOstromBaseFee: number (EUR)
        - netMonthlyGridFees, grossMonthlyGridFees: number (EUR)

        Args:
            start: Start datetime (will be converted to UTC ISO format)
            end: End datetime (will be converted to UTC ISO format)

        Returns:
            List of price data dictionaries with added total_price field
        """
        params = {
            "startDate": start.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "endDate": end.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "resolution": RESOLUTION_HOUR,
            "zip": self._zip_code,
        }

        result = await self._async_request("GET", ENDPOINT_SPOT_PRICES, params=params)

        data = result.get("data")
        if data is None:
            LOGGER.error("Spot prices response missing 'data' field")
            raise OstromApiError("Invalid response structure: missing data")
        if not isinstance(data, list):
            LOGGER.error("Spot prices response 'data' is not a list: %s", type(data))
            raise OstromApiError("Invalid response structure: data is not a list")

        # Add calculated total_price for each entry
        # total_price = (grossKwhPrice + grossKwhTaxAndLevies) / 100  -> EUR/kWh
        for entry in data:
            gross_kwh_price = entry.get("grossKwhPrice", 0)
            gross_tax_and_levies = entry.get("grossKwhTaxAndLevies", 0)
            # Convert from cents to EUR/kWh
            entry["total_price"] = (gross_kwh_price + gross_tax_and_levies) / 100

            # Also store net values in EUR/kWh for convenience
            entry["net_price"] = entry.get("netKwhPrice", 0) / 100
            entry["taxes_price"] = entry.get("grossKwhTaxAndLevies", 0) / 100

        LOGGER.debug("Retrieved %d spot price entries", len(data))

        return data

    async def async_get_energy_consumption(
        self, start: datetime, end: datetime, resolution: str = RESOLUTION_HOUR
    ) -> list[dict[str, Any]]:
        """Retrieve user contract smart meter consumption.

        Based on Ostrom API documentation:
        GET /contracts/{contractId}/energy-consumption
        Query params:
        - startDate: ISO format UTC
        - endDate: ISO format UTC
        - resolution: HOUR, DAY, or MONTH

        Response data fields (per entry):
        - date: string (start of the slot)
        - kWh: number (energy consumption)

        Args:
            start: Start datetime
            end: End datetime
            resolution: HOUR, DAY, or MONTH

        Returns:
            List of consumption data dictionaries. Returns empty list if data is not available (404).

        Note:
            If the API returns 404 (not found), this method returns an empty list
            instead of raising an error, as this may simply indicate that no data
            is available for the requested time period.
        """
        path = ENDPOINT_ENERGY_CONSUMPTION.format(contract_id=self._contract_id)

        params = {
            "startDate": start.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "endDate": end.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "resolution": resolution,
        }

        try:
            result = await self._async_request("GET", path, params=params)
        except OstromApiError as err:
            # Check if this is a 404 error (data not available)
            # Use getattr to safely access status_code in case it's not set
            if getattr(err, "status_code", None) == 404:
                LOGGER.warning(
                    "No consumption data available for period %s to %s: %s",
                    start,
                    end,
                    err,
                )
                return []
            # Re-raise other API errors
            raise

        data = result.get("data")
        if data is None:
            LOGGER.error("Consumption response missing 'data' field")
            raise OstromApiError("Invalid response structure: missing data")
        if not isinstance(data, list):
            LOGGER.error("Consumption response 'data' is not a list: %s", type(data))
            raise OstromApiError("Invalid response structure: data is not a list")

        LOGGER.debug("Retrieved %d consumption entries", len(data))

        return data

    async def async_test_connection(self) -> bool:
        """Test the API connection by authenticating and making a simple request.

        Only tests spot prices endpoint (contract_id not required for this).

        Returns:
            True if connection is successful
        """
        try:
            LOGGER.debug("Testing connection: Authenticating...")
            await self.async_authenticate()
            LOGGER.debug("Authentication successful, testing API call...")

            # Make a simple price request to verify API access
            # Spot prices don't require contract_id
            # Use UTC timezone-aware datetime
            from datetime import timezone

            now = datetime.now(timezone.utc)
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(hours=1)

            # Remove timezone info for API call (API expects naive UTC)
            start_naive = start.replace(tzinfo=None)
            end_naive = end.replace(tzinfo=None)

            LOGGER.debug(
                "Making test API call for prices from %s to %s", start_naive, end_naive
            )
            await self.async_get_spot_prices(start_naive, end_naive)
            LOGGER.debug("Connection test successful")

            return True
        except OstromAuthError as err:
            LOGGER.error("Connection test failed: Authentication error - %s", err)
            raise
        except OstromApiError as err:
            LOGGER.error("Connection test failed: API error - %s", err)
            raise
        except Exception as err:
            LOGGER.exception("Connection test failed: Unexpected error - %s", err)
            raise OstromApiError(
                f"Unexpected error during connection test: {err}"
            ) from err
