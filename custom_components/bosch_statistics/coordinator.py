import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
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

    # async def _async_update_data(self):
    #     """Fetch data from the API."""
