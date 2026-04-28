from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.bosch_statistics.api import BoschHomeAppliance
from custom_components.bosch_statistics.coordinator import BoschDataUpdateCoordinator

# from . import BoschConfigEntry
from .const import DOMAIN
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

    async_add_entities(
        BoschHomeApplianceSensor(coordinator, sensor_description)
        for sensor_description in SENSOR_ENTITY_DESCRIPTIONS
        for coordinator in entry.runtime_data
    )

    # appliances = coordinator.data or []

    # async_add_entities(BoschHomeApplianceSensor(appliance) for appliance in appliances)


class BoschHomeApplianceBaseEntity(CoordinatorEntity[BoschDataUpdateCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: BoschDataUpdateCoordinator) -> None:
        super().__init__(coordinator)


class BoschHomeApplianceEntity:
    def __init__(
        self,
        coordinator: BoschDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        # super().__init__(coordinator)
        self.coordinator = coordinator
        self._id = coordinator.device.ha_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._id)},
            name=str(coordinator.device.name),
            manufacturer=str(coordinator.device.brand),
            model=str(coordinator.device.vib),
            serial_number=str(coordinator.device.serialnumber),
        )

        self.entity_description = entity_description
        self._attr_unique_id = f"{self._id}_{entity_description.key}"


class BoschHomeApplianceSensor(BoschHomeApplianceEntity, SensorEntity):
    def __init__(
        self,
        coordinator: BoschDataUpdateCoordinator,
        entity_description: BoschHomeApplianceSensorDescription,
    ) -> None:
        super().__init__(coordinator, entity_description)

    # @cached_property
    # def native_value(self) -> Any:
    #     return self.entity_description.value_fn(self.coordinator.device)
