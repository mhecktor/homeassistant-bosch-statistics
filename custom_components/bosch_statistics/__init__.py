from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import timedelta

from aiohttp import ClientError
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import BoschApiClient, BoschHomeAppliance
from .const import DOMAIN, PLATFORMS
from .coordinator import BoschDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class BoschRuntimeData:
    client: BoschApiClient
    coordinator: DataUpdateCoordinator[list[dict]]


async def async_setup(hass, config):
    hass.states.async_set(f"{DOMAIN}.interval", 30)

    # Return boolean to indicate that initialization was successful.
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    hass_data = dict(entry.data)

    # Registers update listener to update config entry when options are updated.
    unsub_options_update_listener = entry.add_update_listener(options_update_listener)
    # Store a reference to the unsubscribe function to cleanup if an entry is unloaded.
    hass_data["unsub_options_update_listener"] = unsub_options_update_listener
    hass.data[DOMAIN][entry.entry_id] = hass_data

    session = async_get_clientsession(hass)
    api = BoschApiClient(hass, session, entry)

    try:
        devices = await api.async_get_home_appliances()
    except Exception as err:
        _LOGGER.error(err, exc_info=True, stack_info=True)
        raise UpdateFailed("Failed to fetch home appliances") from err

    coordinators: list[BoschDataUpdateCoordinator] = []

    for device in devices:
        coordinator = BoschDataUpdateCoordinator(hass, entry, device, api)
        await coordinator._async_setup()
        coordinators.append(coordinator)

    entry.runtime_data = coordinators

    await asyncio.gather(
        *[
            coordinator.async_config_entry_first_refresh()
            for coordinator in coordinators
        ]
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def options_update_listener(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Remove config entry from domain.
        entry_data = hass.data[DOMAIN].pop(entry.entry_id)
        # Remove options_update_listener.
        entry_data["unsub_options_update_listener"]()

    return unload_ok
