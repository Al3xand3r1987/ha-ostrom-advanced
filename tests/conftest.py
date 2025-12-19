"""Pytest configuration for Ostrom Advanced tests."""

from __future__ import annotations

import asyncio
import os
import sys
import threading
import warnings
from typing import TYPE_CHECKING

import pytest
import pytest_socket

if TYPE_CHECKING:
    from homeassistant.core import HassJob

pytest_plugins = "pytest_homeassistant_custom_component.plugins"

# Ensure recorder util is not imported before pytest_homeassistant_custom_component patches it.
sys.modules.pop("homeassistant.components.recorder.util", None)

warnings.filterwarnings(
    "ignore",
    message="Inheritance class HomeAssistantApplication .*",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    message='The configuration option "asyncio_default_fixture_loop_scope" is unset\\.',
    category=pytest.PytestDeprecationWarning,
)

if os.name == "nt":
    def _disable_socket_windows(*_args, **_kwargs) -> None:
        """Keep sockets enabled on Windows so asyncio can create the event loop."""
        pytest_socket.enable_socket()

    pytest_socket.disable_socket = _disable_socket_windows


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    """Ensure pytest-asyncio has an explicit default loop scope."""
    try:
        current_scope = config.getini("asyncio_default_fixture_loop_scope")
    except (KeyError, ValueError):
        current_scope = None
    if not current_scope:
        config._inicache["asyncio_default_fixture_loop_scope"] = "function"
    if getattr(config.option, "asyncio_default_fixture_loop_scope", None) in (None, ""):
        config.option.asyncio_default_fixture_loop_scope = "function"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield


def _get_scheduled_timer_handles(event_loop: asyncio.AbstractEventLoop) -> list:
    scheduled = getattr(event_loop, "_scheduled", None)
    return list(scheduled) if scheduled else []


@pytest.fixture(autouse=True)
def verify_cleanup(
    event_loop: asyncio.AbstractEventLoop,
    expected_lingering_tasks: bool,
    expected_lingering_timers: bool,
) -> None:
    """Verify resources are cleaned up while allowing asyncio shutdown helper thread."""
    from pytest_homeassistant_custom_component.common import INSTANCES
    try:
        from homeassistant.core import HassJob as _HassJob
    except ImportError:
        _HassJob = None

    threads_before = frozenset(threading.enumerate())
    tasks_before = asyncio.all_tasks(event_loop)
    yield

    event_loop.run_until_complete(event_loop.shutdown_default_executor())

    if len(INSTANCES) >= 2:
        count = len(INSTANCES)
        for inst in INSTANCES:
            inst.stop()
        pytest.exit(f"Detected non stopped instances ({count}), aborting test run")

    tasks = asyncio.all_tasks(event_loop) - tasks_before
    for task in tasks:
        if expected_lingering_tasks:
            continue
        pytest.fail(f"Lingering task after test {task!r}")
    for task in tasks:
        task.cancel()
    if tasks:
        event_loop.run_until_complete(asyncio.wait(tasks))

    for handle in _get_scheduled_timer_handles(event_loop):
        if handle.cancelled():
            continue
        if expected_lingering_timers:
            handle.cancel()
            continue
        if _HassJob and handle._args and isinstance(job := handle._args[-1], _HassJob):
            if job.cancel_on_shutdown:
                continue
            pytest.fail(f"Lingering timer after job {job!r}")
        else:
            pytest.fail(f"Lingering timer after test {handle!r}")
        handle.cancel()

    threads = frozenset(threading.enumerate()) - threads_before
    for thread in threads:
        if "_run_safe_shutdown_loop" in thread.name:
            continue
        assert isinstance(thread, threading._DummyThread) or thread.name.startswith(
            "waitpid-"
        )
