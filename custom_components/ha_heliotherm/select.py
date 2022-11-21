"""Support for weenect select entities."""
from __future__ import annotations
from . import HaHeliothermModbusHub


from homeassistant.components.select import SelectEntity
from homeassistant.core import callback

from .const import *


async def async_setup_entry(hass, entry, async_add_entities):
    hub_name = entry.data[CONF_NAME]
    hub = hass.data[DOMAIN][hub_name]["hub"]

    device_info = {
        "identifiers": {(DOMAIN, hub_name)},
        "name": hub_name,
        "manufacturer": ATTR_MANUFACTURER,
    }

    entities = []
    for sensor_description in SELECT_TYPES.values():
        sensor = HeliothermSelect(
            hub_name,
            hub,
            device_info,
            sensor_description,
        )
        entities.append(sensor)

    async_add_entities(entities)
    return True


class HeliothermSelect(SelectEntity):
    """Representation of a weenect select."""

    def __init__(
        self,
        platform_name,
        hub: HaHeliothermModbusHub,
        device_info,
        description: HaHeliothermSelectEntityDescription,
    ):
        """Initialize the sensor."""
        self._platform_name = platform_name
        self._attr_device_info = device_info
        self._hub = hub
        self.entity_description: HaHeliothermSelectEntityDescription = description
        self._attr_options = description.select_options
        self._attr_current_option: str = description.default_select_option
        self._setter_function = description.setter_function

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        return self._attr_current_option

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        self._attr_current_option = option
        await self._hub.setter_function_callback(self, option)
        # await self._hub.set_betriebsart(option)

    async def async_added_to_hass(self):
        """Register callbacks."""
        self._hub.async_add_haheliotherm_modbus_sensor(self._modbus_data_updated)

    async def async_will_remove_from_hass(self) -> None:
        self._hub.async_remove_haheliotherm_modbus_sensor(self._modbus_data_updated)

    @callback
    def _modbus_data_updated(self):
        if self.entity_description.key in self._hub.data:
            self._attr_current_option = self._hub.data[self.entity_description.key]
        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name."""
        return f"{self._platform_name} {self.entity_description.name}"

    @property
    def unique_id(self):
        return f"{self._platform_name}_{self.entity_description.key}"
