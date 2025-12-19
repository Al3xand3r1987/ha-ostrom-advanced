"""Pytest configuration for Ostrom Advanced tests."""

from __future__ import annotations

import os
import warnings

import pytest
import pytest_socket

pytest_plugins = "pytest_homeassistant_custom_component.plugins"

warnings.filterwarnings(
    "ignore",
    message="Inheritance class HomeAssistantApplication .*",
    category=DeprecationWarning,
)

if os.name == "nt":
    def _disable_socket_windows(*_args, **_kwargs) -> None:
        """Keep sockets enabled on Windows so asyncio can create the event loop."""
        pytest_socket.enable_socket()

    pytest_socket.disable_socket = _disable_socket_windows


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield
