from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_ACCESS_TOKEN,
    CONF_BASE_URL,
    CONF_CLIENT_ID,
    CONF_EXPIRES_AT,
    CONF_REFRESH_TOKEN,
)
from .utils import async_refresh_token

__all__ = ["BoschApiClient"]

_LOGGER = logging.getLogger(__name__)


@dataclass
class BoschHomeAppliance:
    connected: bool
    brand: str
    type: str
    ha_id: str
    ddfversion: int
    demo: bool
    enumber: str
    name: str
    serialnumber: str
    vib: str


class BoschApiClient:
    def __init__(
        self,
        hass: HomeAssistant,
        session: aiohttp.ClientSession,
        entry: ConfigEntry,
    ) -> None:
        self.hass = hass
        self.session = session
        self.entry = entry

    @property
    def data(self) -> MappingProxyType[str, Any]:
        return self.entry.data

    async def async_request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        await self.async_ensure_token_valid()

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.entry.data[CONF_ACCESS_TOKEN]}"

        url = f"{self.data[CONF_BASE_URL].rstrip('/')}/{path.lstrip('/')}"
        async with self.session.request(method, url, headers=headers, **kwargs) as resp:
            if resp.status == 401:
                await self.async_refresh_token()
                headers["Authorization"] = (
                    f"Bearer {self.entry.data[CONF_ACCESS_TOKEN]}"
                )

                async with self.session.request(
                    method, url, headers=headers, **kwargs
                ) as retry_resp:
                    retry_resp.raise_for_status()
                    return await retry_resp.json()

            resp.raise_for_status()
            return await resp.json()

    async def async_ensure_token_valid(self) -> None:
        expires_at = self.data.get(CONF_EXPIRES_AT, 0)

        # Refresh 60 seconds early.
        if time.time() >= expires_at - 60:
            await self.async_refresh_token()

    async def async_refresh_token(self) -> None:
        token_data = await async_refresh_token(
            session=self.session,
            base_url=self.data[CONF_BASE_URL],
            client_id=self.data[CONF_CLIENT_ID],
            refresh_token=self.data[CONF_REFRESH_TOKEN],
        )

        new_data = dict(self.entry.data)
        new_data[CONF_ACCESS_TOKEN] = token_data["access_token"]
        new_data[CONF_REFRESH_TOKEN] = token_data.get(
            "refresh_token",
            self.data[CONF_REFRESH_TOKEN],
        )
        new_data[CONF_EXPIRES_AT] = time.time() + token_data.get("expires_in", 3600)

        self.hass.config_entries.async_update_entry(
            self.entry,
            data=new_data,
        )

    async def async_get_home_appliances(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> list[BoschHomeAppliance]:
        """Scan for devices using the provided API credentials."""
        _LOGGER.warn("Scanning for devices with current API credentials")

        # _LOGGER.warn(
        #     "Current API credentials:",
        #     json.dumps({"data": self.entry.data, "user_input": user_input}, indent=4),
        # )
        # This is a placeholder implementation. You would replace this with actual
        # logic to query the API and return a list of devices.
        devices = await self.async_request(
            "GET", "/api/homeappliances"
        )  # Ensure token is valid before scanning

        return [
            BoschHomeAppliance(
                connected=device.get("connected", False),
                brand=device.get("brand", ""),
                type=device.get("type", ""),
                ha_id=device.get("haId", ""),
                ddfversion=device.get("ddfversion", 0),
                demo=device.get("demo", False),
                enumber=device.get("enumber", ""),
                name=device.get("name", ""),
                serialnumber=device.get("serialnumber", ""),
                vib=device.get("vib", ""),
            )
            for device in devices.get("data", {}).get("homeappliances", [])
        ]

    async def async_get_status(self) -> dict[str, Any]:
        return await self.async_request("GET", "/api/status")

    async def async_fetch_statistics(self, ha_id) -> dict[str, Any]:
        url = f"https://eu.services.home-connect.com/appliance-usage-statistics-webapp/private/api/appliances/{ha_id}/statistics"
        await self.async_ensure_token_valid()

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.entry.data[CONF_ACCESS_TOKEN]}"
        async with self.session.request("GET", url, headers=headers, **kwargs) as resp:
            if resp.status == 401:
                await self.async_refresh_token()
                headers["Authorization"] = (
                    f"Bearer {self.entry.data[CONF_ACCESS_TOKEN]}"
                )

                async with self.session.request(
                    method, url, headers=headers, **kwargs
                ) as retry_resp:
                    retry_resp.raise_for_status()
                    return await retry_resp.json()

            resp.raise_for_status()
            return await resp.json()
