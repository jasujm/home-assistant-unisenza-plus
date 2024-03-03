"""Unisenza Plus climate platform"""

from __future__ import annotations

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyupgw import Client, ClientError, DeviceType, HvacDevice, RunningState, SystemMode

from .const import DOMAIN

_SYSTEM_MODE_TO_HVAC_MODE = {
    SystemMode.OFF: HVACMode.OFF,
    SystemMode.HEAT: HVACMode.HEAT,
}

_HVAC_MODE_TO_SYSTEM_MODE = {v: k for (k, v) in _SYSTEM_MODE_TO_HVAC_MODE.items()}

_RUNNING_STATE_TO_HVAC_ACTION = {
    RunningState.IDLE: HVACAction.IDLE,
    RunningState.HEATING: HVACAction.HEATING,
}

_DEFAULT_MIN_TEMP = 5.0
_DEFAULT_MAX_TEMP = 30.0
_TEMPERATURE_STEP = 0.5


class UnisenzaPlusClimateEntity(ClimateEntity):
    _enable_turn_on_off_backwards_compatibility = False
    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_hvac_modes = list(_SYSTEM_MODE_TO_HVAC_MODE.values())
    _attr_target_temperature_step = _TEMPERATURE_STEP
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(self, device: HvacDevice, gateway_mac_address: str):
        self._device = device
        self._gateway_mac_address = device_registry.format_mac(gateway_mac_address)

    async def async_added_to_hass(self) -> None:
        """Subscribe to devices on addition to Home Assistant."""
        self._device.subscribe(self._on_update_device)

    async def async_will_remove_from_hass(self) -> None:
        """Unsubscribe from devices on removal from Home Assistant."""
        self._device.unsubscribe(self._on_update_device)

    async def async_update(self) -> None:
        """Refresh device state from the cloud service."""
        try:
            return await self._device.refresh()
        except ClientError as ex:
            raise HomeAssistantError(str(ex)) from ex

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        if system_mode := _HVAC_MODE_TO_SYSTEM_MODE.get(hvac_mode):
            try:
                await self._device.update_system_mode(system_mode)
            except ClientError as ex:
                raise HomeAssistantError(str(ex)) from ex

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        if target_temperature := kwargs.get(ATTR_TEMPERATURE):
            try:
                await self._device.update_target_temperature(float(target_temperature))
            except ClientError as ex:
                raise HomeAssistantError(str(ex)) from ex

    async def async_turn_on(self) -> None:
        """Turn on the device."""
        try:
            await self._device.update_system_mode(SystemMode.HEAT)
        except ClientError as ex:
            raise HomeAssistantError(str(ex)) from ex

    async def async_turn_off(self) -> None:
        """Turn off the device."""
        try:
            await self._device.update_system_mode(SystemMode.OFF)
        except ClientError as ex:
            raise HomeAssistantError(str(ex)) from ex

    @property
    def unique_id(self):
        return self._device.get_serial_number()

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name=self._device.get_name(),
            manufacturer=self._device.get_manufacturer(),
            model=self._device.get_model(),
            serial_number=self._device.get_serial_number(),
            sw_version=self._device.get_firmware_version(),
            via_device=(DOMAIN, self._gateway_mac_address),
        )

    @property
    def current_temperature(self):
        return self._device.get_current_temperature()

    @property
    def target_temperature(self):
        return self._device.get_target_temperature()

    @property
    def hvac_mode(self):
        if system_mode := self._device.get_system_mode():
            return _SYSTEM_MODE_TO_HVAC_MODE.get(system_mode)
        return None

    @property
    def hvac_action(self):
        if self.hvac_mode == HVACMode.OFF:
            return HVACAction.OFF
        if running_state := self._device.get_running_state():
            return _RUNNING_STATE_TO_HVAC_ACTION.get(running_state)
        return None

    @property
    def min_temp(self):
        return self._device.get_min_temp() or _DEFAULT_MIN_TEMP

    @property
    def max_temp(self):
        return self._device.get_max_temp() or _DEFAULT_MAX_TEMP

    @property
    def available(self):
        return bool(self._device.is_available())

    def _on_update_device(self, device, _changes):
        self.schedule_update_ha_state(False)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the climate entities."""
    client: Client = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        UnisenzaPlusClimateEntity(device, gateway.get_mac_address())
        for (gateway, device) in client.get_devices()
        if device.get_type() == DeviceType.HVAC
        and device.get_serial_number() is not None
    )
