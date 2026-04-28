from __future__ import annotations

import time
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
from .utils import _LOGGER, async_refresh_token

__all__ = ["BoschApiClient"]


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

    async def async_get_home_appliances(self) -> list[dict[str, Any]]:
        url = f"{self.entry.data[CONF_BASE_URL]}/api/homeappliances"

        headers = {
            "Authorization": f"Bearer {self.entry.data[CONF_ACCESS_TOKEN]}",
            "Accept": "application/json",
        }

        async with self.session.get(url, headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
        _LOGGER.info("Received home appliances data: %s", data)
        return data.get("data", {}).get("homeappliances", [])

    async def async_request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        await self.async_ensure_token_valid()

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.data[CONF_ACCESS_TOKEN]}"

        url = f"{self.data[CONF_BASE_URL].rstrip('/')}/{path.lstrip('/')}"
        async with self.session.request(method, url, headers=headers, **kwargs) as resp:
            if resp.status == 401:
                await self.async_refresh_token()
                headers["Authorization"] = f"Bearer {self.data[CONF_ACCESS_TOKEN]}"

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

    async def async_get_devices(
        self, user_input: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Scan for devices using the provided API credentials."""
        # This is a placeholder implementation. You would replace this with actual
        # logic to query the API and return a list of devices.
        devices = await self.async_request(
            "GET", "/api/homeappliances"
        )  # Ensure token is valid before scanning

        return devices.get("data", {}).get("homeappliances", [])

    async def async_get_status(self) -> dict[str, Any]:
        return await self.async_request("GET", "/api/status")
