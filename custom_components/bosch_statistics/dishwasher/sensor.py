from homeassistant.components.sensor import (
    SensorDeviceClass,
)
from homeassistant.components.sensor.const import SensorStateClass
from homeassistant.const import UnitOfEnergy, UnitOfVolume
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.bosch_statistics.coordinator import BoschDataUpdateCoordinator

from ..const import DOMAIN

__all__ = ["BoschDishwasherWaterSensor", "BoschDishwasherEnergySensor"]


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


class BoschDishwasherEnergySensor(BoschHomeApplianceEntity):
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
