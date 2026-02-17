"""Switch platform for 2N Relay Emulator."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.network import get_url

from .const import DOMAIN, VERSION, CONF_RELAY_COUNT

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up relay switches from a config entry."""
    relay_count = int(entry.data.get(CONF_RELAY_COUNT, 0))

    if relay_count > 0:
        entities = []
        for relay_num in range(1, relay_count + 1):
            entities.append(RelaySwitch(hass, entry, relay_num))

        async_add_entities(entities)


class RelaySwitch(SwitchEntity):
    """Representation of a relay switch."""

    _attr_has_entity_name = True

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, relay_num: int) -> None:
        """Initialize the relay switch."""
        self.hass = hass
        self._entry = entry
        self._relay_num = relay_num
        self._attr_is_on = False
        
        # Set unique ID
        self._attr_unique_id = f"{entry.entry_id}_relay_{relay_num}"
        
        # Set entity name
        self._attr_name = f"Relay {relay_num}"
        
        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"IP Relay Emulator for 2N (/{entry.data['subpath']})",
            manufacturer="Home Assistant",
            model="IP Relay Emulator for 2N",
            sw_version=VERSION,
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity-specific state attributes."""
        # Get base URL
        base_url = get_url(self.hass, allow_internal=False, allow_external=True) or get_url(
            self.hass, allow_internal=True
        )
        subpath = self._entry.data.get("subpath", "2n-relay")
        
        return {
            "relay_number": self._relay_num,
            "relay_on_url": f"{base_url}/api/{subpath}/relay/ctrl?relay={self._relay_num}&value=on",
            "relay_off_url": f"{base_url}/api/{subpath}/relay/ctrl?relay={self._relay_num}&value=off",
            "relay_status_url": f"{base_url}/api/{subpath}/relay/status?relay={self._relay_num}",
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the relay on."""
        self._attr_is_on = True
        self.async_write_ha_state()
        _LOGGER.info("Relay %d turned on", self._relay_num)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the relay off."""
        self._attr_is_on = False
        self.async_write_ha_state()
        _LOGGER.info("Relay %d turned off", self._relay_num)

    async def async_toggle(self, **kwargs: Any) -> None:
        """Toggle the relay."""
        if self._attr_is_on:
            await self.async_turn_off()
        else:
            await self.async_turn_on()
