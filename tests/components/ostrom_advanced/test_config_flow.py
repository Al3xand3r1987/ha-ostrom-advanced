"""Tests for config flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.ostrom_advanced.api import OstromApiError, OstromAuthError
from custom_components.ostrom_advanced.config_flow import OstromAdvancedConfigFlow
from custom_components.ostrom_advanced.const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_CONTRACT_ID,
    CONF_ENVIRONMENT,
    CONF_ZIP_CODE,
    ENV_PRODUCTION,
)


@pytest.fixture
def mock_hass() -> MagicMock:
    """Create a mock Home Assistant instance."""
    return MagicMock(spec=HomeAssistant)


class TestOstromAdvancedConfigFlow:
    """Tests for OstromAdvancedConfigFlow."""

    @pytest.mark.asyncio
    async def test_flow_user_step_success(self, mock_hass: MagicMock) -> None:
        """Test successful user step."""
        flow = OstromAdvancedConfigFlow()
        flow.hass = mock_hass
        flow._async_get_unique_id = AsyncMock(return_value="test_unique_id")

        # Mock successful authentication
        with patch.object(flow, "_test_credentials", new_callable=AsyncMock):
            result = await flow.async_step_user(
                {
                    CONF_ENVIRONMENT: ENV_PRODUCTION,
                    CONF_CLIENT_ID: "test_client_id",
                    CONF_CLIENT_SECRET: "test_secret",
                    CONF_ZIP_CODE: "12345",
                    CONF_CONTRACT_ID: "",
                }
            )

            assert result["type"] == FlowResultType.CREATE_ENTRY
            assert result["data"][CONF_CLIENT_ID] == "test_client_id"
            assert result["data"][CONF_ZIP_CODE] == "12345"

    @pytest.mark.asyncio
    async def test_flow_user_step_invalid_auth(self, mock_hass: MagicMock) -> None:
        """Test user step with invalid authentication."""
        flow = OstromAdvancedConfigFlow()
        flow.hass = mock_hass
        flow._async_get_unique_id = AsyncMock(return_value="test_unique_id")

        # Mock authentication failure
        with patch.object(
            flow,
            "_test_credentials",
            side_effect=OstromAuthError("Invalid credentials"),
        ):
            result = await flow.async_step_user(
                {
                    CONF_ENVIRONMENT: ENV_PRODUCTION,
                    CONF_CLIENT_ID: "test_client_id",
                    CONF_CLIENT_SECRET: "test_secret",
                    CONF_ZIP_CODE: "12345",
                    CONF_CONTRACT_ID: "",
                }
            )

            assert result["type"] == FlowResultType.FORM
            assert result["errors"]["base"] == "invalid_auth"

    @pytest.mark.asyncio
    async def test_flow_user_step_cannot_connect(self, mock_hass: MagicMock) -> None:
        """Test user step with connection error."""
        flow = OstromAdvancedConfigFlow()
        flow.hass = mock_hass
        flow._async_get_unique_id = AsyncMock(return_value="test_unique_id")

        # Mock connection error
        with patch.object(
            flow, "_test_credentials", side_effect=OstromApiError("Connection failed")
        ):
            result = await flow.async_step_user(
                {
                    CONF_ENVIRONMENT: ENV_PRODUCTION,
                    CONF_CLIENT_ID: "test_client_id",
                    CONF_CLIENT_SECRET: "test_secret",
                    CONF_ZIP_CODE: "12345",
                    CONF_CONTRACT_ID: "",
                }
            )

            assert result["type"] == FlowResultType.FORM
            assert result["errors"]["base"] == "cannot_connect"

    @pytest.mark.asyncio
    async def test_flow_user_step_invalid_zip_code(self, mock_hass: MagicMock) -> None:
        """Test user step with invalid zip code format."""
        flow = OstromAdvancedConfigFlow()
        flow.hass = mock_hass

        result = await flow.async_step_user(
            {
                CONF_ENVIRONMENT: ENV_PRODUCTION,
                CONF_CLIENT_ID: "test_client_id",
                CONF_CLIENT_SECRET: "test_secret",
                CONF_ZIP_CODE: "123",  # Invalid: not 5 digits
                CONF_CONTRACT_ID: "",
            }
        )

        assert result["type"] == FlowResultType.FORM
        assert CONF_ZIP_CODE in result["errors"]

    @pytest.mark.asyncio
    async def test_flow_user_step_missing_fields(self, mock_hass: MagicMock) -> None:
        """Test user step with missing required fields."""
        flow = OstromAdvancedConfigFlow()
        flow.hass = mock_hass

        result = await flow.async_step_user(
            {
                CONF_ENVIRONMENT: ENV_PRODUCTION,
                CONF_CLIENT_ID: "",  # Missing
                CONF_CLIENT_SECRET: "test_secret",
                CONF_ZIP_CODE: "12345",
                CONF_CONTRACT_ID: "",
            }
        )

        assert result["type"] == FlowResultType.FORM
        assert CONF_CLIENT_ID in result["errors"]

    @pytest.mark.asyncio
    async def test_flow_user_step_with_contract_id(self, mock_hass: MagicMock) -> None:
        """Test user step with contract ID provided."""
        flow = OstromAdvancedConfigFlow()
        flow.hass = mock_hass
        flow._async_get_unique_id = AsyncMock(return_value="test_unique_id")

        with patch.object(flow, "_test_credentials", new_callable=AsyncMock):
            result = await flow.async_step_user(
                {
                    CONF_ENVIRONMENT: ENV_PRODUCTION,
                    CONF_CLIENT_ID: "test_client_id",
                    CONF_CLIENT_SECRET: "test_secret",
                    CONF_ZIP_CODE: "12345",
                    CONF_CONTRACT_ID: "contract123",
                }
            )

            assert result["type"] == FlowResultType.CREATE_ENTRY
            assert result["data"][CONF_CONTRACT_ID] == "contract123"
