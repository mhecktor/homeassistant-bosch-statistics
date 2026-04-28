from __future__ import annotations

import logging
import time
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries

from .const import (
    CONF_ACCESS_TOKEN,
    CONF_BASE_URL,
    CONF_CLIENT_ID,
    CONF_EXPIRES_AT,
    CONF_REFRESH_TOKEN,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate invalid auth."""


class MyRestApiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self.data: dict[str, Any] = {}

    async def async_refresh_token(
        self,
        session: aiohttp.ClientSession,
        base_url: str,
        client_id: str,
        client_secret: str,
        refresh_token: str,
    ) -> dict[str, Any]:
        """Refresh an OAuth access token."""

        url = f"{base_url.rstrip('/')}/oauth/token"

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "hc_context": "WebViewVM_getAccessToken|registered",
            "grant_type": "refresh_token",
        }

        try:
            async with session.post(url, data=payload) as response:
                if response.status in (400, 401, 403):
                    raise InvalidAuth

                response.raise_for_status()
                token_data = await response.json()

        except InvalidAuth:
            raise
        except aiohttp.ClientError as err:
            raise CannotConnect from err

        if "access_token" not in token_data:
            raise InvalidAuth

        return token_data

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ):
        """Page 1: collect API details"""

        if user_input is not None:
            self.data = user_input
            return await self.async_step_token()

        errors = {}

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_BASE_URL): str,
                    vol.Required(CONF_CLIENT_ID): str,
                    vol.Required(CONF_REFRESH_TOKEN): str,
                }
            ),
            errors={},
        )

    async def async_step_token(
        self,
        user_input: dict[str, Any] | None = None,
    ):
        errors = {}
        try:
            if self.data is not None:
                session = aiohttp.ClientSession()
                refresh_token = self.data[CONF_REFRESH_TOKEN]
                token_data = await self.async_refresh_token(
                    session=session,
                    base_url=self.data[CONF_BASE_URL],
                    client_id=self.data[CONF_CLIENT_ID],
                    client_secret=self.data[CONF_CLIENT_SECRET],
                    refresh_token=refresh_token,
                )
                access_token = token_data["access_token"]
                new_refresh_token = token_data.get(
                    "refresh_token",
                    refresh_token,
                )
                expires_in = token_data.get("expires_in", 3600)

                new_data = {
                    **self.data,
                    CONF_ACCESS_TOKEN: access_token,
                    CONF_REFRESH_TOKEN: new_refresh_token,
                    CONF_EXPIRES_AT: time.time() + expires_in,
                }

                await self.async_set_unique_id(self._base_data[CONF_CLIENT_ID])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="Bosch Statistics",
                    data=self.data,
                )

        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_show_form(
                step_id="token",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_REFRESH_TOKEN): str,
                    }
                ),
                errors=errors,
            )
