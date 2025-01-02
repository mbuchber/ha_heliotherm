"""Constants for the HaHeliotherm integration."""

from dataclasses import dataclass
from homeassistant.components.climate import (
    ClimateEntityDescription,
    ClimateEntityFeature,
)

from homeassistant.components.sensor import *

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberDeviceClass,
)

from homeassistant.const import *

DOMAIN = "ha_heliotherm"
DEFAULT_NAME = "Heliotherm Heatpump"
DEFAULT_SCAN_INTERVAL = 15
DEFAULT_PORT = 502
CONF_HALEIOTHERM_HUB = "haheliotherm_hub"
ATTR_MANUFACTURER = "Heliotherm"


@dataclass
class HaHeliothermNumberEntityDescription(NumberEntityDescription):
    """A class that describes HaHeliotherm Modbus sensor entities."""

    mode: str = "slider"
    initial: float = None
    editable: bool = True


@dataclass
class HaHeliothermSensorEntityDescription(SensorEntityDescription):
    """A class that describes HaHeliotherm Modbus sensor entities."""


@dataclass
class HaHeliothermBinarySensorEntityDescription(BinarySensorEntityDescription):
    """A class that describes HaHeliotherm Modbus binarysensor entities."""


@dataclass
class HaHeliothermSelectEntityDescription(SensorEntityDescription):
    """A class that describes HaHeliotherm Modbus binarysensor entities."""

    select_options: list[str] = None
    default_select_option: str = None
    setter_function = None


@dataclass
class HaHeliothermClimateEntityDescription(ClimateEntityDescription):
    """A class that describes HaHeliotherm Modbus binarysensor entities."""

    min_value: float = None
    max_value: float = None
    step: float = None
    hvac_modes: list[str] = None
    temperature_unit: str = "°C"
    supported_features: ClimateEntityFeature = ClimateEntityFeature.TARGET_TEMPERATURE


CLIMATE_TYPES: dict[str, list[HaHeliothermClimateEntityDescription]] = {
    "climate_hkr_raum_soll": HaHeliothermClimateEntityDescription(
        name="Raum Solltemperatur",
        key="climate_hkr_raum_soll",
        min_value=10,
        max_value=25,
        step=0.5,
        temperature_unit="°C",
    ),
    "climate_rlt_kuehlen": HaHeliothermClimateEntityDescription(
        name="Kühlen RLT Soll",
        key="climate_rlt_kuehlen",
        min_value=15,
        max_value=25,
        step=1,
        temperature_unit="°C",
    ),
    "climate_ww_bereitung": HaHeliothermClimateEntityDescription(
        name="Warmwasserbereitung",
        key="climate_ww_bereitung",
        min_value=5,
        max_value=65,
        step=0.5,
        temperature_unit="°C",
        supported_features=ClimateEntityFeature.TARGET_TEMPERATURE_RANGE,
    ),
}

NUMBER_TYPES: dict[str, list[HaHeliothermNumberEntityDescription]] = {}

SELECT_TYPES: dict[str, list[HaHeliothermSelectEntityDescription]] = {
    "select_betriebsart": HaHeliothermSelectEntityDescription(
        name="Betriebsart",
        key="select_betriebsart",
        select_options=[
            "Aus",
            "Auto",
            "Kühlen",
            "Sommer",
            "Dauerbetrieb",
            "Absenken",
            "Urlaub",
            "Party",
        ],
        default_select_option="Auto",
    ),
    "select_mkr1_betriebsart": HaHeliothermSelectEntityDescription(
        name="MKR 1 Betriebsart",
        key="select_mkr1_betriebsart",
        select_options=[
            "Aus",
            "Auto",
            "Kühlen",
            "Sommer",
            "Dauerbetrieb",
            "Absenken",
            "Urlaub",
            "Party",
        ],
        default_select_option="Auto",
    ),
    "select_mkr2_betriebsart": HaHeliothermSelectEntityDescription(
        name="MKR 2 Betriebsart",
        key="select_mkr2_betriebsart",
        select_options=[
            "Aus",
            "Auto",
            "Kühlen",
            "Sommer",
            "Dauerbetrieb",
            "Absenken",
            "Urlaub",
            "Party",
        ],
        default_select_option="Auto",
    ),
}

SENSOR_TYPES: dict[str, list[HaHeliothermSensorEntityDescription]] = {
    "temp_aussen": HaHeliothermSensorEntityDescription(
        name="Temp. Aussen",
        key="temp_aussen",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    "temp_brauchwasser": HaHeliothermSensorEntityDescription(
        name="Temp. Brauchwasser",
        key="temp_brauchwasser",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    "temp_vorlauf": HaHeliothermSensorEntityDescription(
        name="Temp. Vorlauf",
        key="temp_vorlauf",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    "temp_ruecklauf": HaHeliothermSensorEntityDescription(
        name="Temp. Rücklauf",
        key="temp_ruecklauf",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    "temp_pufferspeicher": HaHeliothermSensorEntityDescription(
        name="Temp. Pufferspeicher",
        key="temp_pufferspeicher",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    "temp_eq_eintritt": HaHeliothermSensorEntityDescription(
        name="Temp. EQ Eintritt",
        key="temp_eq_eintritt",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    "temp_eq_austritt": HaHeliothermSensorEntityDescription(
        name="Temp. EQ Austritt",
        key="temp_eq_austritt",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    "temp_sauggas": HaHeliothermSensorEntityDescription(
        name="Temp. Sauggas",
        key="temp_sauggas",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    "temp_verdampfung": HaHeliothermSensorEntityDescription(
        name="Temp. Verdampfung",
        key="temp_verdampfung",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    "temp_kodensation": HaHeliothermSensorEntityDescription(
        name="Temp. Kondensation",
        key="temp_kodensation",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    "temp_heissgas": HaHeliothermSensorEntityDescription(
        name="Temp. Heissgas",
        key="temp_heissgas",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    "bar_niederdruck": HaHeliothermSensorEntityDescription(
        name="Niederdruck (bar)",
        key="bar_niederdruck",
        native_unit_of_measurement=PRESSURE_BAR,
        device_class=DEVICE_CLASS_PRESSURE,
    ),
    "bar_hochdruck": HaHeliothermSensorEntityDescription(
        name="Hochdruck (bar)",
        key="bar_hochdruck",
        native_unit_of_measurement=PRESSURE_BAR,
        device_class=DEVICE_CLASS_PRESSURE,
    ),
    "vierwegeventil_luft": HaHeliothermSensorEntityDescription(
        name="Vierwegeventil Luft",
        key="vierwegeventil_luft",
    ),
    "wmz_durchfluss": HaHeliothermSensorEntityDescription(
        name="WMZ_Durchfluss",
        key="wmz_durchfluss",
        native_unit_of_measurement="l/min",
    ),
    "n_soll_verdichter": HaHeliothermSensorEntityDescription(
        name="n-Soll Verdichter",
        key="n_soll_verdichter",
        native_unit_of_measurement="‰",
        device_class=DEVICE_CLASS_PRESSURE,
    ),
    "cop": HaHeliothermSensorEntityDescription(
        name="COP",
        key="cop",
        native_unit_of_measurement="",
    ),
    "temp_frischwasser": HaHeliothermSensorEntityDescription(
        name="Temp. Frischwasser",
        key="temp_frischwasser",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    "temp_aussen_verzoegert": HaHeliothermSensorEntityDescription(
        name="Temp. Aussen verzögert",
        key="temp_aussen_verzoegert",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    "hkr_solltemperatur": HaHeliothermSensorEntityDescription(
        name="HKR Soll Temperatur",
        key="hkr_solltemperatur",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    "mkr1_solltemperatur": HaHeliothermSensorEntityDescription(
        name="MKR1 Soll Temperatur",
        key="mkr1_solltemperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    "mkr2_solltemperatur": HaHeliothermSensorEntityDescription(
        name="MKR2 Soll Temperatur",
        key="mkr2_solltemperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    "expansionsventil": HaHeliothermSensorEntityDescription(
        name="Expansionsventil",
        key="expansionsventil",
        native_unit_of_measurement="‰",
        device_class=DEVICE_CLASS_PRESSURE,
    ),
    "verdichteranforderung": HaHeliothermSensorEntityDescription(
        name="Anforderung",
        key="verdichteranforderung",
    ),
    "wmz_heizung": HaHeliothermSensorEntityDescription(
        name="WMZ Heizung",
        key="wmz_heizung",
        native_unit_of_measurement="kWh",
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),
    "stromz_heizung": HaHeliothermSensorEntityDescription(
        name="Stromzähler Heizung",
        key="stromz_heizung",
        native_unit_of_measurement="kWh",
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),
    "wmz_brauchwasser": HaHeliothermSensorEntityDescription(
        name="WMZ Brauchwasser",
        key="wmz_brauchwasser",
        native_unit_of_measurement="kWh",
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),
    "stromz_brauchwasser": HaHeliothermSensorEntityDescription(
        name="Stromzähler Brauchwasser",
        key="stromz_brauchwasser",
        native_unit_of_measurement="kWh",
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),
    "stromz_gesamt": HaHeliothermSensorEntityDescription(
        name="Stromzähler Gesamt",
        key="stromz_gesamt",
        native_unit_of_measurement="kWh",
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),
    "stromz_leistung": HaHeliothermSensorEntityDescription(
        name="Stromzähler Leistung",
        key="stromz_leistung",
        native_unit_of_measurement="W",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    "wmz_gesamt": HaHeliothermSensorEntityDescription(
        name="WMZ Gesamt",
        key="wmz_gesamt",
        native_unit_of_measurement="kWh",
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),
    "wmz_leistung": HaHeliothermSensorEntityDescription(
        name="WMZ Leistung",
        key="wmz_leistung",
        native_unit_of_measurement="kW",
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
}


BINARYSENSOR_TYPES: dict[str, list[HaHeliothermBinarySensorEntityDescription]] = {
    "on_off_heizkreispumpe": HaHeliothermBinarySensorEntityDescription(
        name="Heizkreispumpe",
        key="on_off_heizkreispumpe",
    ),
    "on_off_pufferladepumpe": HaHeliothermBinarySensorEntityDescription(
        name="Pufferladepumpe",
        key="on_off_pufferladepumpe",
    ),
    "on_off_verdichter": HaHeliothermBinarySensorEntityDescription(
        name="Verdichter",
        key="on_off_verdichter",
    ),
    "on_off_stoerung": HaHeliothermBinarySensorEntityDescription(
        name="Stoerung",
        key="on_off_stoerung",
    ),
    "on_off_evu_sperre": HaHeliothermBinarySensorEntityDescription(
        name="EVU Sperre",
        key="on_off_evu_sperre",
    ),
    "on_off_eq_ventilator": HaHeliothermBinarySensorEntityDescription(
        name="EQ Ventilator",
        key="on_off_eq_ventilator",
    ),
    "ww_vorrang": HaHeliothermBinarySensorEntityDescription(
        name="WW Vorrang",
        key="ww_vorrang",
    ),
    "kuehlen_umv_passiv": HaHeliothermBinarySensorEntityDescription(
        name="Kühlen UMV passiv",
        key="kuehlen_umv_passiv",
    ),
}
