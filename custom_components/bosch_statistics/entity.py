from homeassistant.core import DOMAIN
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.bosch_statistics.coordinator import BoschDataUpdateCoordinator


class BoschHomeApplianceEntity(CoordinatorEntity[BoschDataUpdateCoordinator]):
    _attr_has_entity_name = True

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
