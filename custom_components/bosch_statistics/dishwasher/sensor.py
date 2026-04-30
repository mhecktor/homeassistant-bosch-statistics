import logging
from decimal import Decimal
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.components.sensor.const import SensorStateClass
from homeassistant.const import UnitOfEnergy, UnitOfVolume
from homeassistant.core import callback
from homeassistant.helpers.typing import StateType
from propcache.api import cached_property

from custom_components.bosch_statistics.coordinator import BoschDataUpdateCoordinator
from custom_components.bosch_statistics.entity import BoschHomeApplianceEntity

__all__ = ["BoschDishwasherWaterSensor", "BoschDishwasherEnergySensor"]

_LOGGER = logging.getLogger(__name__)


def get_current_month_data(data: dict) -> dict | None:
    months: list[dict[str, Any]] = data.get("applianceConsumptionData", [])

    if not months:
        return None

    return max(
        months,
        key=lambda item: (
            item["associatedMonth"]["year"],
            item["associatedMonth"]["month"],
        ),
    )


class BoschDishwasherWaterSensor(BoschHomeApplianceEntity, SensorEntity):
    """Sensor for dishwasher water usage."""

    _attr_icon = "mdi:water"
    _attr_native_unit_of_measurement = UnitOfVolume["LITERS"]
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_device_class = SensorDeviceClass.WATER

    def get_native_value(self) -> StateType | Decimal:
        """Calculate the native value for water usage."""
        month = get_current_month_data(self.coordinator.data)
        if not month:
            return None

        ml = month["totalConsumption"]["waterConsumptionInMl"]
        return round(ml / 1000, 3)

    def __init__(
        self,
        coordinator: BoschDataUpdateCoordinator,
    ) -> None:
        super().__init__(coordinator, feature_id="water_usage")

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.get_native_value()
        self.async_write_ha_state()

    @cached_property
    def native_value(self):
        return self.get_native_value()


class BoschDishwasherEnergySensor(BoschHomeApplianceEntity, SensorEntity):
    """Sensor for dishwasher energy usage."""

    _attr_icon = "mdi:power-plug"
    _attr_native_unit_of_measurement = UnitOfEnergy["KILO_WATT_HOUR"]
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_device_class = SensorDeviceClass.ENERGY

    def get_native_value(self) -> StateType | Decimal:
        """Calculate the native value for water usage."""
        month = get_current_month_data(self.coordinator.data)
        if not month:
            return None

        wh = month["totalConsumption"]["energyConsumptionInWh"]
        return round(wh / 1000, 3)

    def __init__(
        self,
        coordinator: BoschDataUpdateCoordinator,
    ) -> None:
        super().__init__(coordinator, feature_id="energy_consumption")

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        self._attr_native_value = self.get_native_value()
        self.async_write_ha_state()

    @cached_property
    def native_value(self) -> StateType | Decimal:
        return self.get_native_value()
