"""The Ostrom Advanced integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OstromApiClient
from .const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_CONSUMPTION_INTERVAL_MINUTES,
    CONF_CONTRACT_ID,
    CONF_ENVIRONMENT,
    CONF_POLL_INTERVAL_MINUTES,
    CONF_UPDATE_OFFSET_SECONDS,
    CONF_ZIP_CODE,
    DEFAULT_CONSUMPTION_INTERVAL_MINUTES,
    DEFAULT_POLL_INTERVAL_MINUTES,
    DEFAULT_UPDATE_OFFSET_SECONDS,
    DOMAIN,
    LOGGER,
    PLATFORMS,
)
from .coordinator import OstromConsumptionCoordinator, OstromPriceCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ostrom Advanced from a config entry.

    Args:
        hass: Home Assistant instance
        entry: Config entry

    Returns:
        True if setup was successful
    """
    LOGGER.debug("Setting up Ostrom Advanced integration")

    # Get configuration from entry
    environment = entry.data[CONF_ENVIRONMENT]
    client_id = entry.data[CONF_CLIENT_ID]
    client_secret = entry.data[CONF_CLIENT_SECRET]
    contract_id = entry.data.get(CONF_CONTRACT_ID, "")
    zip_code = entry.data[CONF_ZIP_CODE]

    # Get options with defaults
    poll_interval = entry.options.get(
        CONF_POLL_INTERVAL_MINUTES, DEFAULT_POLL_INTERVAL_MINUTES
    )
    consumption_interval = entry.options.get(
        CONF_CONSUMPTION_INTERVAL_MINUTES, DEFAULT_CONSUMPTION_INTERVAL_MINUTES
    )
    update_offset_seconds = entry.options.get(
        CONF_UPDATE_OFFSET_SECONDS, DEFAULT_UPDATE_OFFSET_SECONDS
    )

    # Use existing aiohttp session from Home Assistant
    session = async_get_clientsession(hass)

    # Create API client
    client = OstromApiClient(
        hass=hass,
        session=session,
        environment=environment,
        client_id=client_id,
        client_secret=client_secret,
        contract_id=contract_id,
        zip_code=zip_code,
    )

    # Create coordinators
    price_coordinator = OstromPriceCoordinator(
        hass=hass,
        client=client,
        poll_interval_minutes=poll_interval,
        update_offset_seconds=update_offset_seconds,
    )

    # Consumption coordinator only if contract_id is provided
    consumption_coordinator = None
    if contract_id:
        consumption_coordinator = OstromConsumptionCoordinator(
            hass=hass,
            client=client,
            poll_interval_minutes=consumption_interval,
            update_offset_seconds=update_offset_seconds,
        )

    # Perform initial data fetch
    # This will raise ConfigEntryNotReady if it fails
    try:
        await price_coordinator.async_config_entry_first_refresh()
        LOGGER.info("Successfully fetched initial price data")
    except Exception as err:
        LOGGER.error("Failed to fetch initial price data: %s", err)
        # Re-raise to trigger ConfigEntryNotReady
        raise

    # Consumption data only if contract_id is provided
    if consumption_coordinator:
        try:
            await consumption_coordinator.async_config_entry_first_refresh()
        except Exception as err:
            LOGGER.warning(
                "Could not fetch initial consumption data: %s. "
                "Consumption sensors may show unavailable initially.",
                err,
            )
    else:
        LOGGER.info(
            "Contract ID not provided. Consumption sensors will not be available."
        )

    # Store data for use by platforms
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "price_coordinator": price_coordinator,
        "consumption_coordinator": consumption_coordinator,
        "contract_id": contract_id,
    }

    # Forward setup to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    LOGGER.info("Ostrom Advanced integration setup complete for contract %s", contract_id)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.

    Args:
        hass: Home Assistant instance
        entry: Config entry

    Returns:
        True if unload was successful
    """
    LOGGER.debug("Unloading Ostrom Advanced integration")

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        # Cancel coordinator timers before removing data
        if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
            data = hass.data[DOMAIN][entry.entry_id]
            price_coordinator = data.get("price_coordinator")
            consumption_coordinator = data.get("consumption_coordinator")
            
            if price_coordinator:
                await price_coordinator.async_shutdown()
            if consumption_coordinator:
                await consumption_coordinator.async_shutdown()
        
        # Remove stored data
        hass.data[DOMAIN].pop(entry.entry_id)

        # Clean up domain data if no entries left
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)

    return unload_ok

