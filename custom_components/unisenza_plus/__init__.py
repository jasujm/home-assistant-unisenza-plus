"""The Unisenza Plus integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import device_registry
from pyupgw import AuthenticationError, Client, create_api

from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.CLIMATE]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Unisenza Plus from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    try:
        api = await create_api(entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])
    except AuthenticationError as ex:
        raise ConfigEntryAuthFailed("Unable to authenticate") from ex
    except Exception as ex:
        raise ConfigEntryNotReady("Unable to connect") from ex

    client = Client(api)

    try:
        await client.populate_devices()
        await client.refresh_all_devices()
    except Exception as ex:
        await client.aclose()
        raise ConfigEntryNotReady("Unable to retrieve data from upstream") from ex

    dr = device_registry.async_get(hass)
    for gateway in client.get_gateways():
        formatted_mac = device_registry.format_mac(gateway.get_mac_address())
        dr.async_get_or_create(
            config_entry_id=entry.entry_id,
            connections={(device_registry.CONNECTION_NETWORK_MAC, formatted_mac)},
            identifiers={(DOMAIN, formatted_mac)},
            model=gateway.get_model(),
            name=gateway.get_name(),
            sw_version=gateway.get_firmware_version(),
        )

    hass.data[DOMAIN][entry.entry_id] = client

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        client = hass.data[DOMAIN].pop(entry.entry_id)
        await client.aclose()

    return unload_ok
