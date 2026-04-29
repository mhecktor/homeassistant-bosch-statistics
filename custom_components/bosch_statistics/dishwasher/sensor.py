import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.components.sensor.const import SensorStateClass
from homeassistant.const import UnitOfEnergy, UnitOfVolume
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from propcache.api import cached_property

from custom_components.bosch_statistics.coordinator import BoschDataUpdateCoordinator

from ..const import DOMAIN

__all__ = ["BoschDishwasherWaterSensor", "BoschDishwasherEnergySensor"]

_LOGGER = logging.getLogger(__name__)


class BoschHomeApplianceBaseEntity(CoordinatorEntity[BoschDataUpdateCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: BoschDataUpdateCoordinator) -> None:
        super().__init__(coordinator)


class BoschHomeApplianceEntity(BoschHomeApplianceBaseEntity):
    def __init__(
        self,
        coordinator: BoschDataUpdateCoordinator,
        feature_id: str,
    ) -> None:
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._id = coordinator.device.ha_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._id)},
            name=str(coordinator.device.name),
            manufacturer=str(coordinator.device.brand),
            model=str(coordinator.device.vib),
            serial_number=str(coordinator.device.serialnumber),
        )
        self.feature_id = feature_id
        self._attr_unique_id = f"{self._id}_{feature_id}"


def get_current_month_data(data: dict) -> dict | None:
    months: list[dict[str, Any]] = data.get("applianceConsumptionData", [])

    if not months:
        return None

    return max(
        months,
        key=lambda item: (
            item["asspcoatedMonth"]["year"],
            item["asspcoatedMonth"]["month"],
        ),
    )


# class BoschDishwasherWaterSensor(BoschHomeApplianceEntity, SensorEntity):
class BoschDishwasherWaterSensor(BoschHomeApplianceEntity):
    """Sensor for dishwasher water usage."""

    _attr_icon = "mdi:water"
    _attr_native_unit_of_measurement = UnitOfVolume["LITERS"]
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_device_class = SensorDeviceClass.WATER

    def __init__(
        self,
        coordinator: BoschDataUpdateCoordinator,
    ) -> None:
        super().__init__(coordinator, feature_id="water_usage")


class BoschDishwasherEnergySensor(BoschHomeApplianceEntity, SensorEntity):
    """Sensor for dishwasher energy usage."""

    _attr_icon = "mdi:power-plug"
    _attr_native_unit_of_measurement = UnitOfEnergy["WATT_HOUR"]
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_device_class = SensorDeviceClass.ENERGY

    def __init__(
        self,
        coordinator: BoschDataUpdateCoordinator,
    ) -> None:
        super().__init__(coordinator, feature_id="energy_consumption")
        self.entity_id = f"{self.coordinator.device.ha_id}_energy_consumption"

    @cached_property
    def native_value(self):
        _LOGGER.warning(
            "Called native_value for energy sensor with data", self.coordinator.data
        )
        month = get_current_month_data(self.coordinator.data)
        if not month:
            return None

        wh = month["totalConsumption"]["energyConsumptionInWh"]
        return wh
