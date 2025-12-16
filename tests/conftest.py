"""Pytest configuration and fixtures for Ostrom Advanced tests."""

from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest plugins."""
    # Enable sockets to allow asyncio event loop creation on Windows
    # Home Assistant's event loop requires sockets for the Proactor on Windows
    # Tests should use mocking anyway (via aioresponses), so blocking sockets is not necessary
    try:
        import pytest_socket

        # Remove socket restrictions completely
        # This allows asyncio event loop creation while tests still use mocking for network calls
        pytest_socket._remove_restrictions()
    except (ImportError, AttributeError):
        # pytest-socket not installed or API changed, nothing to configure
        pass

