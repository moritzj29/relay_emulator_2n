"""Button platform for 2N Relay Emulator."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.network import get_url

from .const import DOMAIN, VERSION, CONF_BUTTON_COUNT

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up buttons from a config entry."""
    button_count = int(entry.data.get(CONF_BUTTON_COUNT, 0))

    if button_count > 0:
        entities = []
        for button_num in range(1, button_count + 1):
            entities.append(RelayButton(hass, entry, button_num))

        async_add_entities(entities)


class RelayButton(ButtonEntity):
    """Representation of a button (momentary trigger)."""

    _attr_has_entity_name = True
    _attr_available = True

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, button_num: int) -> None:
        """Initialize the relay button."""
        self.hass = hass
        self._entry = entry
        self._button_num = button_num
        
        # Set unique ID
        self._attr_unique_id = f"{entry.entry_id}_button_{button_num}"
        
        # Set entity name
        self._attr_name = f"Button {button_num}"
        
        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"IP Relay Emulator for 2N (/{entry.data['subpath']})",
            manufacturer="Home Assistant",
            model="IP Relay Emulator for 2N",
            sw_version=VERSION,
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity-specific state attributes."""
        try:
            # Get base URL
            base_url = get_url(self.hass, allow_internal=False, allow_external=True) or get_url(
                self.hass, allow_internal=True
            )
            
            # If URL is None, Home Assistant might not be fully configured yet
            if not base_url:
                _LOGGER.debug(
                    "Cannot generate button URLs for button %d: get_url() returned None. "
                    "This typically means Home Assistant URL is not configured yet.",
                    self._button_num,
                )
                return {
                    "button_number": self._button_num,
                    "error": "Home Assistant URL not configured",
                }
            
            subpath = self._entry.data.get("subpath", "2n-relay")
            
            return {
                "button_number": self._button_num,
                "button_trigger_url": f"{base_url}/api/{subpath}/button/trigger?button={self._button_num}",
                "button_status_url": f"{base_url}/api/{subpath}/button/status?button={self._button_num}",
            }
        except Exception as err:
            _LOGGER.exception(
                "Unexpected error generating button URLs for button %d",
                self._button_num,
            )
            return {
                "button_number": self._button_num,
                "error": f"Error: {type(err).__name__}",
            }
