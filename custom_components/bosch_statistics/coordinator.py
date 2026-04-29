import json
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from typings import Any

from .api import BoschApiClient, BoschHomeAppliance
from .const import DOMAIN

__all__ = ["BoschDataUpdateCoordinator"]

_LOGGER = logging.getLogger(__name__)


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
            update_interval=timedelta(seconds=30),
        )
        self.device = device
        self.api = api

    async def _async_setup(self):
        """Set up the coordinator."""
        # self.devices = await self.api.async_get_home_appliances()

    async def _async_update_data(self):
        """Fetch data from the API."""
        data = await self.api.async_fetch_statistics(self.device.ha_id)
        _LOGGER.warn(
            json.dumps(
                {"fetching data for device": self.device.ha_id, "data": data}, indent=4
            )
        )

        return data

        # self.api.get
