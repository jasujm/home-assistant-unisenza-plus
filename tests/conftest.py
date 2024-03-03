"""Common fixtures for the Unisenza Plus tests."""

from unittest.mock import AsyncMock

import pytest

import custom_components.unisenza_plus


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Always enable custom integrations."""
    yield


@pytest.fixture
def mock_setup_entry(monkeypatch: pytest.MonkeyPatch):
    """Override async_setup_entry."""
    mock = AsyncMock(return_value=True)
    monkeypatch.setattr(custom_components.unisenza_plus, "async_setup_entry", mock)
    yield mock
