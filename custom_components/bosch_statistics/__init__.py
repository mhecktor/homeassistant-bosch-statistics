from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta

from aiohttp import ClientError
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import BoschApiClient
from .const import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)


@dataclass
class BoschRuntimeData:
    client: BoschApiClient
    coordinator: DataUpdateCoordinator[list[dict]]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    api = BoschApiClient(hass, session, entry)

    coordinator = DataUpdateCoordinator(
        hass,
        logger=_LOGGER,
        name=DOMAIN,
        # update_method=async_update_data,
        update_method=api.async_get_home_appliances,
        update_interval=timedelta(minutes=5),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
