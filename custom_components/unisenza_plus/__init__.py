"""The Unisenza Plus integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from pyupgw import Client, create_api

from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.CLIMATE]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Unisenza Plus from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    api = await create_api(entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])
    client = Client(api)

    try:
        await client.populate_devices()
        await client.refresh_all_devices()
    except:
        await client.aclose()
        raise

    hass.data[DOMAIN][entry.entry_id] = client

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        client = hass.data[DOMAIN].pop(entry.entry_id)
        await client.aclose()

    return unload_ok
