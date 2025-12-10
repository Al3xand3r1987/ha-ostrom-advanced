"""Constants for the Ostrom Advanced integration."""
from __future__ import annotations

import logging
from typing import Final

# Domain
DOMAIN: Final = "ostrom_advanced"
DEFAULT_NAME: Final = "Ostrom Advanced"

# Logger
LOGGER = logging.getLogger(__package__)

# Configuration keys
CONF_ENVIRONMENT: Final = "environment"
CONF_CLIENT_ID: Final = "client_id"
CONF_CLIENT_SECRET: Final = "client_secret"
CONF_CONTRACT_ID: Final = "contract_id"
CONF_ZIP_CODE: Final = "zip_code"
CONF_POLL_INTERVAL_MINUTES: Final = "poll_interval_minutes"
CONF_CONSUMPTION_INTERVAL_MINUTES: Final = "consumption_interval_minutes"

# Default values
DEFAULT_POLL_INTERVAL_MINUTES: Final = 15
DEFAULT_CONSUMPTION_INTERVAL_MINUTES: Final = 60
DEFAULT_TIMEOUT: Final = 30  # seconds for HTTP requests

# Environment options
ENV_SANDBOX: Final = "sandbox"
ENV_PRODUCTION: Final = "production"

# API Base URLs (based on official Ostrom API documentation)
API_BASE_URLS: Final[dict[str, str]] = {
    ENV_SANDBOX: "https://sandbox.ostrom-api.io",
    ENV_PRODUCTION: "https://production.ostrom-api.io",
}

# Auth URLs (based on official Ostrom API documentation)
AUTH_URLS: Final[dict[str, str]] = {
    ENV_SANDBOX: "https://auth.sandbox.ostrom-api.io",
    ENV_PRODUCTION: "https://auth.production.ostrom-api.io",
}

# API Endpoints
ENDPOINT_OAUTH_TOKEN: Final = "/oauth2/token"
ENDPOINT_SPOT_PRICES: Final = "/spot-prices"
ENDPOINT_ENERGY_CONSUMPTION: Final = "/contracts/{contract_id}/energy-consumption"

# OAuth2 constants
OAUTH_GRANT_TYPE: Final = "client_credentials"

# Resolution options for API calls
RESOLUTION_HOUR: Final = "HOUR"
RESOLUTION_DAY: Final = "DAY"
RESOLUTION_MONTH: Final = "MONTH"

# Platforms
PLATFORMS: Final = ["sensor"]

# Attribution
ATTRIBUTION: Final = "Data provided by Ostrom"

# Developer Portal URL
DEVELOPER_PORTAL_URL: Final = "https://developer.ostrom-api.io/"

