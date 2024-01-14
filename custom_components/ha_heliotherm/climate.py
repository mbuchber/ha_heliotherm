import asyncio
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)

from homeassistant.components.ha_heliotherm import HaHeliothermModbusHub

import logging
from typing import Optional, Dict, Any


import homeassistant.util.dt as dt_util

from .const import (
    ATTR_MANUFACTURER,
    DOMAIN,
    CLIMATE_TYPES,
    HaHeliothermClimateEntityDescription,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    hub_name = entry.data[CONF_NAME]
    hub = hass.data[DOMAIN][hub_name]["hub"]

    device_info = {
        "identifiers": {(DOMAIN, hub_name)},
        "name": hub_name,
        "manufacturer": ATTR_MANUFACTURER,
    }

    entities = []
    for sensor_description in CLIMATE_TYPES.values():
        sensor = HaHeliothermModbusClimate(
            hub_name,
            hub,
            device_info,
            sensor_description,
        )
        entities.append(sensor)

    async_add_entities(entities)
    return True


class HaHeliothermModbusClimate(ClimateEntity):
    """Representation of an Heliotherm Modbus sensor."""

    def __init__(
        self,
        platform_name,
        hub: HaHeliothermModbusHub,
        device_info,
        description: HaHeliothermClimateEntityDescription,
    ):
        """Initialize the sensor."""
        self._platform_name = platform_name
        self._attr_device_info = device_info
        self._hub = hub
        self.entity_description: HaHeliothermClimateEntityDescription = description
        self._attr_hvac_modes = [HVACMode.AUTO]
        self._attr_hvac_mode = HVACMode.AUTO
        self._attr_temperature_unit = description.temperature_unit
        self._attr_min_temp = description.min_value
        self._attr_max_temp = description.max_value
        self._attr_target_temperature = description.target_temperature
        self._attr_target_temperature_low = description.min_value
        self._attr_target_temperature_high = description.max_value
        self._attr_target_temperature_step = description.step
        self._attr_supported_features = description.supported_features

    async def async_added_to_hass(self):
        """Register callbacks."""
        self._hub.async_add_haheliotherm_modbus_sensor(self._modbus_data_updated)

    async def async_will_remove_from_hass(self) -> None:
        self._hub.async_remove_haheliotherm_modbus_sensor(self._modbus_data_updated)

    @callback
    def _modbus_data_updated(self):
        if self.entity_description.key in self._hub.data:
            args = self._hub.data[self.entity_description.key]
            if "temperature" in args:
                self._attr_current_temperature = float(args["temperature"])
                self._attr_target_temperature = float(args["temperature"])
            if "target_temp_low" in args:
                self._attr_target_temperature_low = float(args["target_temp_low"])
            if "target_temp_high" in args:
                self._attr_target_temperature_high = float(args["target_temp_high"])

        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name."""
        return f"{self._platform_name} {self.entity_description.name}"

    @property
    def unique_id(self) -> Optional[str]:
        return f"{self._platform_name}_{self.entity_description.key}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return (
            self._hub.data[self.entity_description.key]
            if self.entity_description.key in self._hub.data
            else None
        )

    def set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        if "temperature" in kwargs:
            self._attr_current_temperature = float(kwargs["temperature"])
            self._attr_target_temperature = float(kwargs["temperature"])
        if "target_temp_low" in kwargs:
            self._attr_target_temperature_low = float(kwargs["target_temp_low"])
        if "target_temp_high" in kwargs:
            self._attr_target_temperature_high = float(kwargs["target_temp_high"])

        self.hass.add_job(self._hub.setter_function_callback(self, kwargs))
