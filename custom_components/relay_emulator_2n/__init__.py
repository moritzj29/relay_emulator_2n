"""
2N IP Relay Emulator for Home Assistant.

This component emulates a 2N IP relay unit and provides HTTP endpoints
that are compatible with 2N access control units (intercoms, readers, etc.).
"""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN
from .http_server import setup_http_server, cleanup_http_server

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SWITCH, Platform.BUTTON]


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
