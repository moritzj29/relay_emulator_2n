"""Config flow for 2N Relay Emulator integration."""
from __future__ import annotations

import logging
import re
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
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

# Note: Home Assistant encrypts sensitive data in config entries when marked as such
# We'll store password as sensitive data


def validate_subpath(subpath: str) -> str:
    """Validate and normalize subpath."""
    # Remove leading and trailing slashes
    subpath = subpath.strip("/")
    
    # Check for valid characters (alphanumeric, dash, underscore, forward slash for nested paths)
    if not re.match(r"^[a-zA-Z0-9_/-]+$", subpath):
        raise ValueError("Subpath can only contain letters, numbers, dashes, underscores, and forward slashes")
    
    # Ensure no double slashes
    if "//" in subpath:
        raise ValueError("Subpath cannot contain consecutive slashes")
    
    # Ensure doesn't start or end with slash
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
                # Validate and normalize subpath
                subpath = validate_subpath(user_input[CONF_SUBPATH])
                user_input[CONF_SUBPATH] = subpath
                
                # Check if subpath is already in use by another instance
                for entry in self._async_current_entries():
                    if entry.data.get(CONF_SUBPATH) == subpath:
                        errors["subpath"] = "subpath_in_use"
                        break

                if not errors:
                    # Store sensitive data separately to enable encryption
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
            except Exception:  # pylint: disable=broad-except
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
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for 2N Relay Emulator."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Validate subpath if changed
                new_subpath = validate_subpath(user_input[CONF_SUBPATH])
                
                # Check if subpath changed and if new subpath is already in use
                if new_subpath != self.config_entry.data.get(CONF_SUBPATH):
                    for entry in self.hass.config_entries.async_entries(DOMAIN):
                        if entry.entry_id != self.config_entry.entry_id:
                            if entry.data.get(CONF_SUBPATH) == new_subpath:
                                errors["subpath"] = "subpath_in_use"
                                break

                if not errors:
                    # Update config entry with new data
                    self.hass.config_entries.async_update_entry(
                        self.config_entry,
                        data={
                            CONF_SUBPATH: new_subpath,
                            CONF_USERNAME: user_input[CONF_USERNAME],
                            CONF_RELAY_COUNT: user_input[CONF_RELAY_COUNT],
                            CONF_BUTTON_COUNT: user_input[CONF_BUTTON_COUNT],
                        },
                        options={
                            CONF_PASSWORD: user_input[CONF_PASSWORD],
                        },
                    )
                    
                    # Reload the config entry to apply changes
                    await self.hass.config_entries.async_reload(self.config_entry.entry_id)
                    
                    return self.async_create_entry(title="", data={})

            except ValueError as err:
                errors["subpath"] = "invalid_subpath"
                _LOGGER.error("Invalid subpath: %s", err)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Get current values
        current_subpath = self.config_entry.data.get(CONF_SUBPATH, DEFAULT_SUBPATH)
        current_username = self.config_entry.data.get(CONF_USERNAME, DEFAULT_USERNAME)
        current_password = self.config_entry.options.get(
            CONF_PASSWORD, 
            self.config_entry.data.get(CONF_PASSWORD, DEFAULT_PASSWORD)
        )
        current_relay_count = self.config_entry.data.get(CONF_RELAY_COUNT, DEFAULT_RELAY_COUNT)
        current_button_count = self.config_entry.data.get(CONF_BUTTON_COUNT, DEFAULT_BUTTON_COUNT)

        data_schema = vol.Schema(
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
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "current_subpath": current_subpath,
                "current_relay_count": str(current_relay_count),
                "current_button_count": str(current_button_count),
            },
        )
