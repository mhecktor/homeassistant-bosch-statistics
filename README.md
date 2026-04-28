# My REST API – Home Assistant Custom Integration

A custom Home Assistant integration that connects to a REST API using OAuth-style access tokens with automatic token refresh support.

This integration uses:

- `DataUpdateCoordinator` for polling and shared updates
- `aiohttp` for async API communication
- automatic access token refresh using refresh tokens
- Home Assistant Config Flow support
- sensor platform example

---

# Features

- Authenticated REST API requests using Bearer tokens
- Automatic token refresh before expiration
- Retry on `401 Unauthorized`
- Configurable through the Home Assistant UI
- Example sensor entity for API status data
- Modern async Home Assistant integration structure

---

# Folder Structure

```text
custom_components/
└── my_rest_api/
    ├── __init__.py
    ├── api.py
    ├── const.py
    ├── config_flow.py
    ├── manifest.json
    └── sensor.py
