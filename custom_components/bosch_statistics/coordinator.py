import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import BoschApiClient, BoschHomeAppliance
from .const import DOMAIN

__all__ = ["BoschDataUpdateCoordinator"]

_LOGGER = logging.getLogger(__name__)


class BoschDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator to manage fetching data from the Bosch API."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        device: BoschHomeAppliance,
        api: BoschApiClient,
    ):
        """Initialize the coordinator."""
        _LOGGER.warning(
            "Initializing BoschDataUpdateCoordinator for device %s with ID %s on the interface %s",
            device.name,
            device.ha_id,
            config_entry.options[CONF_SCAN_INTERVAL],
        )
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
            always_update=False,
            update_interval=timedelta(minutes=5),
        )
        self.device = device
        self.api = api

    async def _async_setup(self):
        """Set up the coordinator."""
        # self.devices = await self.api.async_get_home_appliances()

    async def _async_update_data(self):
        """Fetch data from the API."""
        _LOGGER.warning(
            "Fetching data for device %s with ID %s",
            self.device.name,
            self.device.ha_id,
        )
        data = await self.api.async_fetch_statistics(self.device.ha_id)

        return data

        # self.api.get
