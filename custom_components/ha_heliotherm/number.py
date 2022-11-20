from homeassistant.core import callback
from homeassistant.components.number import NumberEntity
from homeassistant.components.input_number import (
    InputNumber,
    CONF_NAME,
    CONF_MIN,
    CONF_MAX,
    CONF_INITIAL,
    CONF_STEP,
    CONF_UNIT_OF_MEASUREMENT,
    CONF_MODE,
)
import logging
from typing import Optional, Dict, Any


import homeassistant.util.dt as dt_util

from .const import (
    ATTR_MANUFACTURER,
    DOMAIN,
    NUMBER_TYPES,
    HaHeliothermNumberEntityDescription,
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
    for sensor_description in NUMBER_TYPES.values():
        sensor = HaHeliothermModbusNumber(
            hub_name,
            hub,
            device_info,
            sensor_description,
        )
        entities.append(sensor)

    async_add_entities(entities)
    return True


class HaHeliothermModbusNumber(NumberEntity):
    """Representation of an Heliotherm Modbus number."""

    def __init__(
        self,
        platform_name,
        hub,
        device_info,
        description: HaHeliothermNumberEntityDescription,
    ):
        """Initialize the sensor."""
        self._platform_name = platform_name
        self._attr_device_info = device_info
        self._hub = hub
        self.entity_description: HaHeliothermNumberEntityDescription = description
        self._attr_mode = description.mode

    async def async_added_to_hass(self):
        """Register callbacks."""
        self._hub.async_add_haheliotherm_modbus_sensor(self._modbus_data_updated)

    async def async_will_remove_from_hass(self) -> None:
        self._hub.async_remove_haheliotherm_modbus_sensor(self._modbus_data_updated)

    @callback
    def _modbus_data_updated(self):
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

    def set_native_value(self, value: float) -> None:
        self._attr_value = value

    async def async_set_native_value(self, value: float) -> None:
        self._attr_value = value
