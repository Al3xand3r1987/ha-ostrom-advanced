"""Config flow for Ostrom Advanced integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

# Initialize logger early to help with debugging
_LOGGER = logging.getLogger(__name__)

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OstromApiClient, OstromApiError, OstromAuthError
from .const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_CONSUMPTION_INTERVAL_MINUTES,
    CONF_CONTRACT_ID,
    CONF_ENVIRONMENT,
    CONF_POLL_INTERVAL_MINUTES,
    CONF_ZIP_CODE,
    DEFAULT_CONSUMPTION_INTERVAL_MINUTES,
    DEFAULT_POLL_INTERVAL_MINUTES,
    DOMAIN,
    ENV_PRODUCTION,
    ENV_SANDBOX,
    LOGGER,
)


class OstromAdvancedConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ostrom Advanced."""

    VERSION = 1

    def async_get_options_flow(self, config_entry: ConfigEntry) -> "OstromAdvancedOptionsFlow":
        """Get the options flow for this handler."""
        return OstromAdvancedOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step.

        This is the first step where users enter their Ostrom credentials.
        """
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate required fields first
            if not user_input.get(CONF_CLIENT_ID):
                errors[CONF_CLIENT_ID] = "required"
            if not user_input.get(CONF_CLIENT_SECRET):
                errors[CONF_CLIENT_SECRET] = "required"
            if not user_input.get(CONF_ZIP_CODE):
                errors[CONF_ZIP_CODE] = "required"

            # Only proceed if no validation errors
            if not errors:
                # Use zip_code as unique_id if contract_id is not provided
                # Ensure unique_id is never empty
                contract_id = user_input.get(CONF_CONTRACT_ID, "").strip() if user_input.get(CONF_CONTRACT_ID) else ""
                zip_code = user_input.get(CONF_ZIP_CODE, "").strip()
                
                if not zip_code:
                    errors[CONF_ZIP_CODE] = "required"
                else:
                    # Use contract_id if provided and not empty, otherwise use zip_code
                    unique_id = contract_id if contract_id else f"ostrom_{zip_code}"
                    await self.async_set_unique_id(unique_id)
                    self._abort_if_unique_id_configured()

                    # Try to authenticate and validate the connection
                    try:
                        await self._test_credentials(user_input)
                    except OstromAuthError as err:
                        LOGGER.warning("Authentication failed during config flow: %s", err)
                        errors["base"] = "invalid_auth"
                    except OstromApiError as err:
                        LOGGER.warning("API error during config flow: %s", err)
                        errors["base"] = "cannot_connect"
                    except Exception as err:  # pylint: disable=broad-except
                        LOGGER.exception("Unexpected exception during config flow: %s", err)
                        errors["base"] = "unknown"
                    
                    if not errors:
                        # Success - create the config entry
                        contract_id_value = contract_id if contract_id else ""
                        
                        if contract_id_value:
                            title = f"Ostrom Contract {contract_id_value[-4:]}"
                        else:
                            title = f"Ostrom {zip_code}"

                        # Separate data and options
                        data = {
                            CONF_ENVIRONMENT: user_input[CONF_ENVIRONMENT],
                            CONF_CLIENT_ID: user_input[CONF_CLIENT_ID],
                            CONF_CLIENT_SECRET: user_input[CONF_CLIENT_SECRET],
                            CONF_CONTRACT_ID: contract_id_value,
                            CONF_ZIP_CODE: zip_code,
                        }

                        options = {
                            CONF_POLL_INTERVAL_MINUTES: user_input.get(
                                CONF_POLL_INTERVAL_MINUTES, DEFAULT_POLL_INTERVAL_MINUTES
                            ),
                            CONF_CONSUMPTION_INTERVAL_MINUTES: user_input.get(
                                CONF_CONSUMPTION_INTERVAL_MINUTES,
                                DEFAULT_CONSUMPTION_INTERVAL_MINUTES,
                            ),
                        }

                        return self.async_create_entry(title=title, data=data, options=options)

        # Show the form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_ENVIRONMENT, default=ENV_PRODUCTION
                    ): vol.In({ENV_SANDBOX: "Sandbox", ENV_PRODUCTION: "Production"}),
                    vol.Required(CONF_CLIENT_ID): str,
                    vol.Required(CONF_CLIENT_SECRET): str,
                    vol.Required(CONF_ZIP_CODE): str,
                    vol.Optional(CONF_CONTRACT_ID, default=""): str,
                    vol.Optional(
                        CONF_POLL_INTERVAL_MINUTES,
                        default=DEFAULT_POLL_INTERVAL_MINUTES,
                    ): vol.All(vol.Coerce(int), vol.Range(min=5, max=120)),
                    vol.Optional(
                        CONF_CONSUMPTION_INTERVAL_MINUTES,
                        default=DEFAULT_CONSUMPTION_INTERVAL_MINUTES,
                    ): vol.All(vol.Coerce(int), vol.Range(min=15, max=1440)),
                }
            ),
            errors=errors,
        )

    async def _test_credentials(self, user_input: dict[str, Any]) -> None:
        """Test the provided credentials.

        Creates a temporary API client and attempts to:
        1. Get an access token
        2. Make a test API call to the prices endpoint

        Args:
            user_input: Dictionary with user configuration

        Raises:
            OstromAuthError: If authentication fails
            OstromApiError: If API call fails
        """
        session = async_get_clientsession(self.hass)

        # Contract ID is optional - only needed for consumption data
        contract_id = user_input.get(CONF_CONTRACT_ID, "")
        
        client = OstromApiClient(
            hass=self.hass,
            session=session,
            environment=user_input[CONF_ENVIRONMENT],
            client_id=user_input[CONF_CLIENT_ID],
            client_secret=user_input[CONF_CLIENT_SECRET],
            contract_id=contract_id,
            zip_code=user_input[CONF_ZIP_CODE],
        )

        # This will authenticate and make a test API call
        await client.async_test_connection()


class OstromAdvancedOptionsFlow(OptionsFlow):
    """Handle options for Ostrom Advanced."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle options flow.

        Allows users to modify polling intervals.
        """
        if user_input is not None:
            # Wenn Häkchen entfernt wurde (Feld nicht vorhanden oder None), verwende Default-Werte
            if (
                CONF_POLL_INTERVAL_MINUTES not in user_input
                or user_input.get(CONF_POLL_INTERVAL_MINUTES) is None
            ):
                user_input[CONF_POLL_INTERVAL_MINUTES] = DEFAULT_POLL_INTERVAL_MINUTES

            if (
                CONF_CONSUMPTION_INTERVAL_MINUTES not in user_input
                or user_input.get(CONF_CONSUMPTION_INTERVAL_MINUTES) is None
            ):
                user_input[CONF_CONSUMPTION_INTERVAL_MINUTES] = (
                    DEFAULT_CONSUMPTION_INTERVAL_MINUTES
                )

            return self.async_create_entry(data=user_input)

        # Get current values
        current_poll = self.config_entry.options.get(
            CONF_POLL_INTERVAL_MINUTES, DEFAULT_POLL_INTERVAL_MINUTES
        )
        current_consumption = self.config_entry.options.get(
            CONF_CONSUMPTION_INTERVAL_MINUTES, DEFAULT_CONSUMPTION_INTERVAL_MINUTES
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_POLL_INTERVAL_MINUTES,
                        default=current_poll,
                    ): vol.All(vol.Coerce(int), vol.Range(min=5, max=120)),
                    vol.Optional(
                        CONF_CONSUMPTION_INTERVAL_MINUTES,
                        default=current_consumption,
                    ): vol.All(vol.Coerce(int), vol.Range(min=15, max=1440)),
                }
            ),
        )

