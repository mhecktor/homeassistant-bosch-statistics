from __future__ import _Feature, annotations

from dataclasses import dataclass
from typing import Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.bosch_statistics.api import BoschHomeAppliance
from custom_components.bosch_statistics.coordinator import BoschDataUpdateCoordinator
from custom_components.bosch_statistics.dishwasher.sensor import (
    BoschDishwasherWaterSensor,
)

# from . import BoschConfigEntry
from .utils import _LOGGER


@dataclass(frozen=True, kw_only=True)
class BoschHomeApplianceSensorDescription(SensorEntityDescription):
    """Class describing Fressnapf Tracker sensor entities."""

    value_fn: Callable[[BoschHomeAppliance], int]


SENSOR_ENTITY_DESCRIPTIONS: tuple[BoschHomeApplianceSensorDescription, ...] = (
    BoschHomeApplianceSensorDescription(
        key="battery",
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.ddfversion,
    ),
)


def get_device_handlers(
    coordinator: BoschDataUpdateCoordinator,
):
    return {"Dishwasher": [BoschDishwasherWaterSensor(coordinator)]}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    # coordinator = entry.runtime_data.coordinator
    _LOGGER.warning(
        "Setting up sensor platform with coordinator %s",
        entry.entry_id,
        extra=entry.data,
    )

    entities = []

    for coordinator in entry.runtime_data:
        device_handlers = get_device_handlers(coordinator)
        device_type = coordinator.device.type
        _LOGGER.warning(
            "Found device of type %s with ID %s",
            device_type,
            coordinator.device.ha_id,
        )

        for device_class, entity in device_handlers.items():
            if device_type == device_class:
                entities.extend(entity)
                _LOGGER.warning(
                    "Adding %d sensors for device %s",
                    coordinator.device.ha_id,
                )

    async_add_entities(entities)

    # appliances = coordinator.data or []

    # async_add_entities(BoschHomeApplianceSensor(appliance) for appliance in appliances)
