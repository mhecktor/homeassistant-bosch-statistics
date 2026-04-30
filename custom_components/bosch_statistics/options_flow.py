from typing import Any, Dict, Mapping, cast

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_SCAN_INTERVAL


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Bosch Statistics integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage the options for the custom component."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            if not errors:
                # Process the user input and update the config entry
                return self.async_create_entry(
                    title="Bosch Statistics Options",
                    data=cast(
                        Mapping, {CONF_SCAN_INTERVAL, user_input[CONF_SCAN_INTERVAL]}
                    ),
                )

        options_schema = vol.Schema(
            {
                vol.Optional("scan_interval", default="5 minutes"): str,
                # Define your options schema here
                # Example: vol.Optional("option_name", default="default_value"): str,
            }
        )

        # Show the options form
        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors=errors,
        )
