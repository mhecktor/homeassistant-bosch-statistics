from __future__ import _Feature, annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.bosch_statistics.coordinator import BoschDataUpdateCoordinator
from custom_components.bosch_statistics.dishwasher.sensor import (
    BoschDishwasherEnergySensor,
    BoschDishwasherWaterSensor,
)

# from . import BoschConfigEntry
from .utils import _LOGGER


def get_device_handlers(
    coordinator: BoschDataUpdateCoordinator,
):
    return {
        "Dishwasher": [
            BoschDishwasherWaterSensor(coordinator),
            BoschDishwasherEnergySensor(coordinator),
        ]
    }


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
