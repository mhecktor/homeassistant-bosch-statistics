from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

# from . import BoschConfigEntry
from .const import DOMAIN
from .utils import _LOGGER


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    # coordinator = entry.runtime_data.coordinator

    _LOGGER.warn("Setting up sensor platform with coordinator", extra=entry)
    # appliances = coordinator.data or []

    # async_add_entities(BoschHomeApplianceSensor(appliance) for appliance in appliances)


class BoschHomeApplianceSensor(SensorEntity):
    def __init__(self, appliance: dict[str, Any]) -> None:
        self._appliance = appliance

        appliance_id = appliance["haId"]
        name = appliance.get("name") or appliance.get("brand") or "Bosch appliance"

        self._attr_unique_id = f"{DOMAIN}_{appliance_id}"
        self._attr_name = name

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, appliance_id)},
            name=name,
            manufacturer=appliance.get("brand", "Bosch"),
            model=appliance.get("type"),
            serial_number=appliance.get("vib"),
        )

    # def native_value(self) -> str:
    #     return self._appliance.get("connected", "unknown")
