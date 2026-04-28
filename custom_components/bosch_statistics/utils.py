import logging
from typing import Any

import aiohttp

__all__ = ["async_refresh_token"]

_LOGGER = logging.getLogger(__name__)


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate invalid auth."""

    def __init__(self, message: str | None = None) -> None:
        self.message = message or "Invalid authentication"
        super().__init__(self.message)


async def async_refresh_token(
    session: aiohttp.ClientSession,
    base_url: str,
    client_id: str,
    refresh_token: str,
) -> dict[str, Any]:
    """Refresh an OAuth access token."""

    url = f"{base_url.rstrip('/')}/security/oauth/token"

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "hc_context": "WebViewVM_getAccessToken|registered",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        async with session.post(url, data=payload, headers=headers) as response:
            if response.status in (400, 401, 403):
                response_message = await response.text()
                _LOGGER.error(
                    "Invalid auth response [%s]: %s",
                    response.status,
                    response_message,
                )
                raise InvalidAuth(response_message)

            response.raise_for_status()
            token_data = await response.json()

    except InvalidAuth:
        raise
    except aiohttp.ClientError as err:
        raise CannotConnect from err

    if "access_token" not in token_data:
        raise InvalidAuth

    return token_data
