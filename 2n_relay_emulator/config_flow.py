"""Config flow for 2N Relay Emulator integration."""
from __future__ import annotations

import logging
import re
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_SUBPATH,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_RELAY_COUNT,
    CONF_BUTTON_COUNT,
    DEFAULT_SUBPATH,
    DEFAULT_USERNAME,
    DEFAULT_PASSWORD,
    DEFAULT_RELAY_COUNT,
    DEFAULT_BUTTON_COUNT,
)

_LOGGER = logging.getLogger(__name__)


def validate_subpath(subpath: str) -> str:
    """Validate and normalize subpath."""
    subpath = subpath.strip("/")
    
    if not re.match(r"^[a-zA-Z0-9_/-]+$", subpath):
        raise ValueError("Subpath can only contain letters, numbers, dashes, underscores, and forward slashes")
    
    if "//" in subpath:
        raise ValueError("Subpath cannot contain consecutive slashes")
    
    if subpath.startswith("/") or subpath.endswith("/"):
        raise ValueError("Subpath cannot start or end with a slash")
    
    if not subpath:
        raise ValueError("Subpath cannot be empty")
    
    return subpath


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for 2N Relay Emulator."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                subpath = validate_subpath(user_input[CONF_SUBPATH])
                user_input[CONF_SUBPATH] = subpath
                
                for entry in self._async_current_entries():
                    if entry.data.get(CONF_SUBPATH) == subpath:
                        errors["subpath"] = "subpath_in_use"
                        break

                if not errors:
                    return self.async_create_entry(
                        title=f"2N Relay Emulator (/{subpath})",
                        data={
                            CONF_SUBPATH: subpath,
                            CONF_USERNAME: user_input[CONF_USERNAME],
                            CONF_RELAY_COUNT: user_input[CONF_RELAY_COUNT],
                            CONF_BUTTON_COUNT: user_input[CONF_BUTTON_COUNT],
                        },
                        options={
                            CONF_PASSWORD: user_input[CONF_PASSWORD],
                        },
                    )

            except ValueError as err:
                errors["subpath"] = "invalid_subpath"
                _LOGGER.error("Invalid subpath: %s", err)
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_SUBPATH, default=DEFAULT_SUBPATH): str,
                vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): str,
                vol.Required(CONF_PASSWORD, default=DEFAULT_PASSWORD): str,
                vol.Required(CONF_RELAY_COUNT, default=DEFAULT_RELAY_COUNT): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0,
                        max=16,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(CONF_BUTTON_COUNT, default=DEFAULT_BUTTON_COUNT): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0,
                        max=16,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for 2N Relay Emulator."""

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            # Update the entry
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={
                    CONF_SUBPATH: user_input[CONF_SUBPATH],
                    CONF_USERNAME: user_input[CONF_USERNAME],
                    CONF_RELAY_COUNT: user_input[CONF_RELAY_COUNT],
                    CONF_BUTTON_COUNT: user_input[CONF_BUTTON_COUNT],
                },
                options={
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                },
            )
            
            # Reload the integration
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            
            return self.async_create_entry(title="", data={})

        # Get current values with safe defaults
        current_subpath = self.config_entry.data.get(CONF_SUBPATH, DEFAULT_SUBPATH)
        current_username = self.config_entry.data.get(CONF_USERNAME, DEFAULT_USERNAME)
        current_password = self.config_entry.options.get(
            CONF_PASSWORD,
            self.config_entry.data.get(CONF_PASSWORD, DEFAULT_PASSWORD)
        )
        current_relay_count = self.config_entry.data.get(CONF_RELAY_COUNT, DEFAULT_RELAY_COUNT)
        current_button_count = self.config_entry.data.get(CONF_BUTTON_COUNT, DEFAULT_BUTTON_COUNT)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SUBPATH, default=current_subpath): str,
                    vol.Required(CONF_USERNAME, default=current_username): str,
                    vol.Required(CONF_PASSWORD, default=current_password): str,
                    vol.Required(CONF_RELAY_COUNT, default=current_relay_count): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0,
                            max=16,
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Required(CONF_BUTTON_COUNT, default=current_button_count): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0,
                            max=16,
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                }
            ),
        )

