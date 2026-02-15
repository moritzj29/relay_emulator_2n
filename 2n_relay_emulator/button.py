"""Button platform for 2N Relay Emulator."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, CONF_BUTTON_COUNT

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up 2N Relay buttons from a config entry."""
    button_count = entry.data.get(CONF_BUTTON_COUNT, 0)

    if button_count > 0:
        entities = []
        for button_num in range(1, button_count + 1):
            entities.append(RelayButton(entry, button_num))

        async_add_entities(entities)


class RelayButton(ButtonEntity):
    """Representation of a 2N relay button (momentary trigger)."""

    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, button_num: int) -> None:
        """Initialize the relay button."""
        self._entry = entry
        self._button_num = button_num
        
        # Set unique ID
        self._attr_unique_id = f"{entry.entry_id}_button_{button_num}"
        
        # Set entity name
        self._attr_name = f"Button {button_num}"
        
        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"2N Relay Emulator (/{entry.data['subpath']})",
            manufacturer="Home Assistant",
            model="2N IP Relay Emulator",
            sw_version="2.0.0",
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True

    async def async_press(self, **kwargs: Any) -> None:
        """Handle the button press."""
        _LOGGER.info("Button %d pressed", self._button_num)
        # Button press event is automatically fired by Home Assistant
        # No state to maintain - buttons are stateless
