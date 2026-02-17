"""
2N IP Relay Emulator for Home Assistant.

This component emulates a 2N IP relay unit and provides HTTP endpoints
that are compatible with 2N access control units (intercoms, readers, etc.).
"""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, CONF_RELAY_COUNT, CONF_BUTTON_COUNT
from .http_server import setup_http_server, cleanup_http_server

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SWITCH, Platform.BUTTON]


async def async_cleanup_orphaned_entities(
    hass: HomeAssistant,
    entry: ConfigEntry,
    new_relay_count: int,
    new_button_count: int,
) -> None:
    """Remove entities that are no longer in the new count range.
    
    When users decrease the number of relays or buttons, this function
    removes the corresponding entities from Home Assistant to prevent
    orphaned entities in the entity registry.
    """
    old_relay_count = int(entry.data.get(CONF_RELAY_COUNT, 0))
    old_button_count = int(entry.data.get(CONF_BUTTON_COUNT, 0))

    entity_registry = er.async_get(hass)

    # Remove orphaned relay entities if count decreased
    if new_relay_count < old_relay_count:
        for relay_num in range(new_relay_count + 1, old_relay_count + 1):
            unique_id = f"{entry.entry_id}_relay_{relay_num}"
            entity_id = entity_registry.async_get_entity_id("switch", DOMAIN, unique_id)
            if entity_id:
                _LOGGER.info("Removing orphaned relay entity: %s (relay %d)", entity_id, relay_num)
                entity_registry.async_remove(entity_id)

    # Remove orphaned button entities if count decreased
    if new_button_count < old_button_count:
        for button_num in range(new_button_count + 1, old_button_count + 1):
            unique_id = f"{entry.entry_id}_button_{button_num}"
            entity_id = entity_registry.async_get_entity_id("button", DOMAIN, unique_id)
            if entity_id:
                _LOGGER.info("Removing orphaned button entity: %s (button %d)", entity_id, button_num)
                entity_registry.async_remove(entity_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up 2N Relay Emulator from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Set up the HTTP server
    await setup_http_server(hass, entry)

    # Forward the setup to the switch platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Clean up HTTP server first (before unloading platforms)
    # This ensures the HTTP view is removed as early as possible
    try:
        await cleanup_http_server(hass, entry)
    except Exception as err:
        _LOGGER.error("Error cleaning up HTTP server: %s", err)
        # Continue with platform unload even if HTTP cleanup fails

    # Unload platforms
    try:
        unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    except Exception as err:
        _LOGGER.error("Error unloading platforms: %s", err)
        return False

    # Clean up data storage
    if unload_ok:
        try:
            hass.data[DOMAIN].pop(entry.entry_id, None)
        except Exception as err:
            _LOGGER.error("Error cleaning up data storage: %s", err)
            # Still return unload_ok since platforms were successfully unloaded

    return unload_ok
