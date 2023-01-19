"""The HaHeliotherm integration."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
import threading
from typing import Optional

from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.exceptions import ConnectionException
from pymodbus.payload import BinaryPayloadDecoder
import voluptuous as vol

from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    Platform,
)
from homeassistant.core import HomeAssistant, callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import async_track_time_interval


from .const import DEFAULT_NAME, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

# PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.SELECT]
PLATFORMS = [Platform.SELECT, Platform.SENSOR, Platform.BINARY_SENSOR, Platform.CLIMATE]


async def async_setup(hass, config):
    """Set up the HaHeliotherm modbus component."""
    hass.data[DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up a HaHeliotherm modbus."""
    host = entry.data[CONF_HOST]
    name = entry.data[CONF_NAME]
    port = entry.data[CONF_PORT]
    scan_interval = DEFAULT_SCAN_INTERVAL

    _LOGGER.debug("Setup %s.%s", DOMAIN, name)

    hub = HaHeliothermModbusHub(hass, name, host, port, scan_interval)
    # """Register the hub."""
    hass.data[DOMAIN][name] = {"hub": hub}

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass, entry):
    """Unload HaHeliotherm mobus entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if not unload_ok:
        return False

    hass.data[DOMAIN].pop(entry.data["name"])
    return True


class HaHeliothermModbusHub:
    """Thread safe wrapper class for pymodbus."""

    def __init__(
        self,
        hass: HomeAssistant,
        name,
        host,
        port,
        scan_interval,
    ):
        """Initialize the Modbus hub."""
        self._hass = hass
        self._client = ModbusTcpClient(
            host=host, port=port, timeout=3, retries=3, retry_on_empty=True
        )
        self._lock = threading.Lock()
        self._name = name
        self._scan_interval = timedelta(seconds=scan_interval)
        self._unsub_interval_method = None
        self._sensors = []
        self.data = {}

    @callback
    def async_add_haheliotherm_modbus_sensor(self, update_callback):
        """Listen for data updates."""
        # This is the first sensor, set up interval.
        if not self._sensors:
            self.connect()
            self._unsub_interval_method = async_track_time_interval(
                self._hass, self.async_refresh_modbus_data, self._scan_interval
            )

        self._sensors.append(update_callback)

    @callback
    def async_remove_haheliotherm_modbus_sensor(self, update_callback):
        """Remove data update."""
        self._sensors.remove(update_callback)

        if not self._sensors:
            # """stop the interval timer upon removal of last sensor"""
            self._unsub_interval_method()
            self._unsub_interval_method = None
            self.close()

    async def async_refresh_modbus_data(self, _now: Optional[int] = None) -> None:
        """Time to update."""
        if not self._sensors:
            return

        update_result = self.read_modbus_registers()

        if update_result:
            for update_callback in self._sensors:
                update_callback()

    @property
    def name(self):
        """Return the name of this hub."""
        return self._name

    def close(self):
        """Disconnect client."""
        with self._lock:
            self._client.close()

    def connect(self):
        """Connect client."""
        with self._lock:
            self._client.connect()

    def read_input_registers(self, slave, address, count):
        """Read holding registers."""
        with self._lock:
            kwargs = {"slave": slave, "unit": slave} if slave else {}
            return self._client.read_input_registers(address, count, **kwargs)

    def getsignednumber(self, number, bitlength=16):
        mask = (2**bitlength) - 1
        if number & (1 << (bitlength - 1)):
            return number | ~mask
        else:
            return number & mask

    def checkval(self, value, scale, bitlength=16):
        """Check value for missing item"""
        if value is None:
            return None
        value = self.getsignednumber(value, bitlength)
        value = round(value * scale, 1)
        if value == -50.0:
            value = None
        return value

    def getbetriebsart(self, bietriebsart_nr: int):
        return (
            "Aus"
            if bietriebsart_nr == 0
            else "Auto"
            if bietriebsart_nr == 1
            else "Kühlen"
            if bietriebsart_nr == 2
            else "Sommer"
            if bietriebsart_nr == 3
            else "Dauerbetrieb"
            if bietriebsart_nr == 4
            else "Absenken"
            if bietriebsart_nr == 5
            else "Urlaub"
            if bietriebsart_nr == 6
            else "Party"
            if bietriebsart_nr == 7
            else None
        )

    def getbetriebsartnr(self, bietriebsart_str: str):
        return (
            0
            if bietriebsart_str == "Aus"
            else 1
            if bietriebsart_str == "Auto"
            else 2
            if bietriebsart_str == "Kühlen"
            else 3
            if bietriebsart_str == "Sommer"
            else 4
            if bietriebsart_str == "Dauerbetrieb"
            else 5
            if bietriebsart_str == "Absenken"
            else 6
            if bietriebsart_str == "Urlaub"
            else 7
            if bietriebsart_str == "Party"
            else None
        )

    async def setter_function_callback(self, entity: Entity, option):
        if entity.entity_description.key == "select_betriebsart":
            await self.set_betriebsart(option)
            return
        if entity.entity_description.key == "climate_hkr_raum_soll":
            temp = float(option["temperature"])
            await self.set_raumtemperatur(temp)

        if entity.entity_description.key == "climate_ww_bereitung":
            tmin = float(option["target_temp_low"])
            tmax = float(option["target_temp_high"])
            await self.set_ww_bereitung(tmin, tmax)

    async def set_betriebsart(self, betriebsart: str):
        betriebsart_nr = self.getbetriebsartnr(betriebsart)
        if betriebsart_nr is None:
            return
        self._client.write_register(address=100, value=betriebsart_nr, slave=1, unit=1)
        await self.async_refresh_modbus_data()

    async def set_raumtemperatur(self, temperature: float):
        if temperature is None:
            return
        temp_int = int(temperature * 10)
        self._client.write_register(address=101, value=temp_int, slave=1, unit=1)
        await self.async_refresh_modbus_data()

    async def set_ww_bereitung(self, temp_min: float, temp_max: float):
        if temp_min is None or temp_max is None:
            return
        temp_max_int = int(temp_max * 10)
        temp_min_int = int(temp_min * 10)
        self._client.write_register(address=105, value=temp_max_int, slave=1, unit=1)
        self._client.write_register(address=106, value=temp_min_int, slave=1, unit=1)
        await self.async_refresh_modbus_data()

    def read_modbus_registers(self):
        """Read from modbus registers"""
        modbusdata = self.read_input_registers(slave=1, address=10, count=32)
        modbusdata2 = self.read_input_registers(slave=1, address=60, count=16)
        modbusdata3 = self._client.read_holding_registers(address=100, count=27, unit=1)

        # if modbusdata.isError():
        #    return False

        temp_aussen = modbusdata.registers[0]
        self.data["temp_aussen"] = self.checkval(temp_aussen, 0.1)

        temp_brauchwasser = modbusdata.registers[1]
        self.data["temp_brauchwasser"] = self.checkval(temp_brauchwasser, 0.1)

        temp_vorlauf = modbusdata.registers[2]
        self.data["temp_vorlauf"] = self.checkval(temp_vorlauf, 0.1)

        temp_ruecklauf = modbusdata.registers[3]
        self.data["temp_ruecklauf"] = self.checkval(temp_ruecklauf, 0.1)

        temp_pufferspeicher = modbusdata.registers[4]
        self.data["temp_pufferspeicher"] = self.checkval(temp_pufferspeicher, 0.1)

        temp_eq_eintritt = modbusdata.registers[5]
        self.data["temp_eq_eintritt"] = self.checkval(temp_eq_eintritt, 0.1)

        temp_eq_austritt = modbusdata.registers[6]
        self.data["temp_eq_austritt"] = self.checkval(temp_eq_austritt, 0.1)

        temp_sauggas = modbusdata.registers[7]
        self.data["temp_sauggas"] = self.checkval(temp_sauggas, 0.1)

        temp_verdampfung = modbusdata.registers[8]
        self.data["temp_verdampfung"] = self.checkval(temp_verdampfung, 0.1)

        temp_kodensation = modbusdata.registers[9]
        self.data["temp_kodensation"] = self.checkval(temp_kodensation, 0.1)

        temp_heissgas = modbusdata.registers[10]
        self.data["temp_heissgas"] = self.checkval(temp_heissgas, 0.1)

        bar_niederdruck = modbusdata.registers[11]
        self.data["bar_niederdruck"] = self.checkval(bar_niederdruck, 0.1)

        bar_hochdruck = modbusdata.registers[12]
        self.data["bar_hochdruck"] = self.checkval(bar_hochdruck, 0.1)

        on_off_heizkreispumpe = modbusdata.registers[13]
        self.data["on_off_heizkreispumpe"] = (
            "off" if (on_off_heizkreispumpe == 0) else "on"
        )

        on_off_pufferladepumpe = modbusdata.registers[14]
        self.data["on_off_pufferladepumpe"] = (
            "off" if (on_off_pufferladepumpe == 0) else "on"
        )

        on_off_verdichter = modbusdata.registers[15]
        self.data["on_off_verdichter"] = "off" if (on_off_verdichter == 0) else "on"

        on_off_stoerung = modbusdata.registers[16]
        self.data["on_off_stoerung"] = "off" if (on_off_stoerung == 0) else "on"

        vierwegeventil_luft = modbusdata.registers[17]
        self.data["vierwegeventil_luft"] = (
            "Abtaubetrieb" if (vierwegeventil_luft != 0) else "Aus"
        )

        wmz_durchfluss = modbusdata.registers[18]
        self.data["wmz_durchfluss"] = self.checkval(wmz_durchfluss, 0.1)

        n_soll_verdichter = modbusdata.registers[19]
        self.data["n_soll_verdichter"] = self.checkval(n_soll_verdichter, 1)

        cop = modbusdata.registers[20]
        self.data["cop"] = self.checkval(cop, 0.1)

        temp_frischwasser = modbusdata.registers[21]
        self.data["temp_frischwasser"] = self.checkval(temp_frischwasser, 0.1)

        on_off_evu_sperre = modbusdata.registers[22]
        self.data["on_off_evu_sperre"] = "off" if (on_off_evu_sperre == 0) else "on"

        temp_aussen_verzoegert = modbusdata.registers[23]
        self.data["temp_aussen_verzoegert"] = self.checkval(temp_aussen_verzoegert, 0.1)

        hkr_solltemperatur = modbusdata.registers[24]
        self.data["hkr_solltemperatur"] = self.checkval(hkr_solltemperatur, 0.1)

        mkr1_solltemperatur = modbusdata.registers[25]
        self.data["mkr1_solltemperatur"] = self.checkval(mkr1_solltemperatur, 0.1)

        mkr2_solltemperatur = modbusdata.registers[26]
        self.data["mkr2_solltemperatur"] = self.checkval(mkr2_solltemperatur, 0.1)

        on_off_eq_ventilator = modbusdata.registers[27]
        self.data["on_off_eq_ventilator"] = (
            "off" if (on_off_eq_ventilator == 0) else "on"
        )

        ww_vorrang = modbusdata.registers[28]
        self.data["ww_vorrang"] = "off" if (ww_vorrang == 0) else "on"

        kuehlen_umv_passiv = modbusdata.registers[29]
        self.data["kuehlen_umv_passiv"] = "off" if (kuehlen_umv_passiv == 0) else "on"

        expansionsventil = modbusdata.registers[30]
        self.data["expansionsventil"] = self.checkval(expansionsventil, 1)

        verdichteranforderung = modbusdata.registers[31]
        self.data["verdichteranforderung"] = (
            "Kühlen"
            if (verdichteranforderung == 10)
            else "Heizen"
            if (verdichteranforderung == 20)
            else "Warmwasser"
            if (verdichteranforderung == 30)
            else "Keine Anforderung"
        )

        # -----------------------------------------------------------------------------------
        decoder = BinaryPayloadDecoder.fromRegisters(
            modbusdata2.registers, wordorder=Endian.Big
        )

        wmz_heizung = decoder.decode_32bit_uint()
        self.data["wmz_heizung"] = self.checkval(wmz_heizung, 1, 32)

        stromz_heizung = decoder.decode_32bit_uint()
        self.data["stromz_heizung"] = self.checkval(stromz_heizung, 1, 32)

        wmz_brauchwasser = decoder.decode_32bit_uint()
        self.data["wmz_brauchwasser"] = self.checkval(wmz_brauchwasser, 1, 32)

        stromz_brauchwasser = decoder.decode_32bit_uint()
        self.data["stromz_brauchwasser"] = self.checkval(stromz_brauchwasser, 1, 32)

        stromz_gesamt = decoder.decode_32bit_uint()
        self.data["stromz_gesamt"] = self.checkval(stromz_gesamt, 1, 32)

        stromz_leistung = decoder.decode_32bit_uint()
        self.data["stromz_leistung"] = self.checkval(stromz_leistung, 1, 32)

        wmz_gesamt = decoder.decode_32bit_uint()
        self.data["wmz_gesamt"] = self.checkval(wmz_gesamt, 1, 32)

        wmz_leistung = decoder.decode_32bit_uint()
        self.data["wmz_leistung"] = self.checkval(wmz_leistung, 1, 32)

        # -----------------------------------------------------------------------------------

        select_betriebsart = modbusdata3.registers[0]
        self.data["select_betriebsart"] = self.getbetriebsart(select_betriebsart)

        climate_hkr_raum_soll = modbusdata3.registers[1]
        self.data["climate_hkr_raum_soll"] = {
            "temperature": self.checkval(climate_hkr_raum_soll, 0.1)
        }

        climate_ww_bereitung_max = modbusdata3.registers[5]
        climate_ww_bereitung_min = modbusdata3.registers[6]
        self.data["climate_ww_bereitung"] = {
            "target_temp_low": self.checkval(climate_ww_bereitung_min, 0.1),
            "target_temp_high": self.checkval(climate_ww_bereitung_max, 0.1),
            "temperature": self.checkval(temp_brauchwasser, 0.1),
        }

        # externe_anforderung = modbusdata3.registers[20]

        return True
