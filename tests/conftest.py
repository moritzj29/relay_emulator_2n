import sys
import types
from enum import Enum

# Minimal Home Assistant shim to allow importing the integration without HA installed
# This must be loaded before any test imports from relay_emulator_2n

# Create module hierarchy
homeassistant = types.ModuleType("homeassistant")
core = types.ModuleType("homeassistant.core")
const = types.ModuleType("homeassistant.const")
config_entries = types.ModuleType("homeassistant.config_entries")
components = types.ModuleType("homeassistant.components")
components_http = types.ModuleType("homeassistant.components.http")
helpers = types.ModuleType("homeassistant.helpers")
entity_registry = types.ModuleType("homeassistant.helpers.entity_registry")

# Define Platform enum
class Platform(str, Enum):
    SWITCH = "switch"
    BUTTON = "button"

# Define classes
class HomeAssistant:
    pass

class ConfigEntry:
    pass

class HomeAssistantView:
    pass

# Attach attributes to modules
core.HomeAssistant = HomeAssistant
const.Platform = Platform
config_entries.ConfigEntry = ConfigEntry
components_http.HomeAssistantView = HomeAssistantView
entity_registry.async_get = lambda hass: None

# Register all modules in sys.modules BEFORE any imports
sys.modules["homeassistant"] = homeassistant
sys.modules["homeassistant.core"] = core
sys.modules["homeassistant.const"] = const
sys.modules["homeassistant.config_entries"] = config_entries
sys.modules["homeassistant.components"] = components
sys.modules["homeassistant.components.http"] = components_http
sys.modules["homeassistant.helpers"] = helpers
sys.modules["homeassistant.helpers.entity_registry"] = entity_registry
