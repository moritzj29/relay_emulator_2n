import sys
import types
from enum import Enum

# Minimal Home Assistant shim to allow importing the integration without HA installed
# This must be loaded before any test imports from custom_components.relay_emulator_2n

# Create module hierarchy
homeassistant = types.ModuleType("homeassistant")
core = types.ModuleType("homeassistant.core")
const = types.ModuleType("homeassistant.const")
config_entries = types.ModuleType("homeassistant.config_entries")
components = types.ModuleType("homeassistant.components")
components_switch = types.ModuleType("homeassistant.components.switch")
components_button = types.ModuleType("homeassistant.components.button")
components_http = types.ModuleType("homeassistant.components.http")
helpers = types.ModuleType("homeassistant.helpers")
entity_registry = types.ModuleType("homeassistant.helpers.entity_registry")
entity_platform = types.ModuleType("homeassistant.helpers.entity_platform")
network = types.ModuleType("homeassistant.helpers.network")
entity = types.ModuleType("homeassistant.helpers.entity")

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

class SwitchEntity:
    """Base class for switch entities."""
    pass

class ButtonEntity:
    """Base class for button entities."""
    pass

class DeviceInfo:
    """Device info class."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# Attach attributes to modules
core.HomeAssistant = HomeAssistant
const.Platform = Platform
config_entries.ConfigEntry = ConfigEntry
components_http.HomeAssistantView = HomeAssistantView
components_switch.SwitchEntity = SwitchEntity
components_button.ButtonEntity = ButtonEntity
entity.DeviceInfo = DeviceInfo
entity_registry.async_get = lambda hass: None
entity_platform.AddEntitiesCallback = None

# Mock get_url function for network helpers
def mock_get_url(hass, allow_internal=False, allow_external=False):
    """Mock get_url to return a test URL."""
    return "http://homeassistant.local:8123"

network.get_url = mock_get_url

# Register all modules in sys.modules BEFORE any imports
sys.modules["homeassistant"] = homeassistant
sys.modules["homeassistant.core"] = core
sys.modules["homeassistant.const"] = const
sys.modules["homeassistant.config_entries"] = config_entries
sys.modules["homeassistant.components"] = components
sys.modules["homeassistant.components.switch"] = components_switch
sys.modules["homeassistant.components.button"] = components_button
sys.modules["homeassistant.components.http"] = components_http
sys.modules["homeassistant.helpers"] = helpers
sys.modules["homeassistant.helpers.entity"] = entity
sys.modules["homeassistant.helpers.entity_registry"] = entity_registry
sys.modules["homeassistant.helpers.entity_platform"] = entity_platform
sys.modules["homeassistant.helpers.network"] = network
