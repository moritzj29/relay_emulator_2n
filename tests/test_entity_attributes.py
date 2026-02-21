"""Tests for entity attribute URL generation."""
import pytest
from types import SimpleNamespace

from custom_components.relay_emulator_2n.switch import RelaySwitch
from custom_components.relay_emulator_2n.button import RelayButton


class DummyHass:
    """Dummy Home Assistant instance for testing."""
    pass


class DummyEntry:
    """Dummy config entry for testing."""
    def __init__(self, entry_id, data):
        self.entry_id = entry_id
        self.data = data


@pytest.mark.asyncio
async def test_relay_switch_attributes():
    """Test that RelaySwitch generates correct URL attributes."""
    hass = DummyHass()
    entry = DummyEntry("test_entry_id", {
        "subpath": "2n-relay",
        "username": "admin",
        "relay_count": 2,
    })
    
    relay = RelaySwitch(hass, entry, relay_num=1)
    
    # Get the attributes
    attrs = relay.extra_state_attributes
    
    # Verify all required attributes are present
    assert "relay_number" in attrs
    assert "relay_on_url" in attrs
    assert "relay_off_url" in attrs
    assert "relay_status_url" in attrs
    
    # Verify values
    assert attrs["relay_number"] == 1
    assert "/2n-relay/api/relay/ctrl" in attrs["relay_on_url"]
    assert "/2n-relay/api/relay/ctrl" in attrs["relay_off_url"]
    assert "/2n-relay/api/relay/status" in attrs["relay_status_url"]
    assert "relay/ctrl?relay=1&value=on" in attrs["relay_on_url"]
    assert "relay/ctrl?relay=1&value=off" in attrs["relay_off_url"]
    assert "relay/status?relay=1" in attrs["relay_status_url"]


@pytest.mark.asyncio
async def test_relay_switch_attributes_different_relay():
    """Test URL attributes for different relay numbers."""
    hass = DummyHass()
    entry = DummyEntry("test_entry_id", {
        "subpath": "2n-relay",
        "username": "admin",
        "relay_count": 3,
    })
    
    relay = RelaySwitch(hass, entry, relay_num=2)
    attrs = relay.extra_state_attributes
    
    assert attrs["relay_number"] == 2
    assert "relay=2&value=on" in attrs["relay_on_url"]
    assert "relay=2&value=off" in attrs["relay_off_url"]
    assert "relay=2" in attrs["relay_status_url"]


@pytest.mark.asyncio
async def test_relay_switch_attributes_custom_subpath():
    """Test URL attributes with custom subpath."""
    hass = DummyHass()
    entry = DummyEntry("test_entry_id", {
        "subpath": "custom-relay-path",
        "username": "admin",
        "relay_count": 1,
    })
    
    relay = RelaySwitch(hass, entry, relay_num=1)
    attrs = relay.extra_state_attributes
    
    assert "custom-relay-path" in attrs["relay_on_url"]
    assert "custom-relay-path" in attrs["relay_off_url"]
    assert "custom-relay-path" in attrs["relay_status_url"]
    assert "/custom-relay-path/api/relay/ctrl" in attrs["relay_on_url"]


@pytest.mark.asyncio
async def test_button_attributes():
    """Test that RelayButton generates correct URL attributes."""
    hass = DummyHass()
    entry = DummyEntry("test_entry_id", {
        "subpath": "2n-relay",
        "username": "admin",
        "button_count": 2,
    })
    
    button = RelayButton(hass, entry, button_num=1)
    
    # Get the attributes
    attrs = button.extra_state_attributes
    
    # Verify all required attributes are present
    assert "button_number" in attrs
    assert "button_trigger_url" in attrs
    assert "button_status_url" in attrs
    
    # Verify values
    assert attrs["button_number"] == 1
    assert "/2n-relay/api/button/trigger" in attrs["button_trigger_url"]
    assert "/2n-relay/api/button/status" in attrs["button_status_url"]
    assert "button/trigger?button=1" in attrs["button_trigger_url"]
    assert "button/status?button=1" in attrs["button_status_url"]


@pytest.mark.asyncio
async def test_button_attributes_different_button():
    """Test URL attributes for different button numbers."""
    hass = DummyHass()
    entry = DummyEntry("test_entry_id", {
        "subpath": "2n-relay",
        "username": "admin",
        "button_count": 3,
    })
    
    button = RelayButton(hass, entry, button_num=3)
    attrs = button.extra_state_attributes
    
    assert attrs["button_number"] == 3
    assert "button=3" in attrs["button_trigger_url"]
    assert "button=3" in attrs["button_status_url"]


@pytest.mark.asyncio
async def test_button_attributes_custom_subpath():
    """Test button URL attributes with custom subpath."""
    hass = DummyHass()
    entry = DummyEntry("test_entry_id", {
        "subpath": "relay-control",
        "username": "admin",
        "button_count": 1,
    })
    
    button = RelayButton(hass, entry, button_num=1)
    attrs = button.extra_state_attributes
    
    assert "relay-control" in attrs["button_trigger_url"]
    assert "relay-control" in attrs["button_status_url"]
    assert "/relay-control/api/button/trigger" in attrs["button_trigger_url"]


@pytest.mark.asyncio
async def test_relay_switch_url_format():
    """Test that generated URLs have correct format."""
    hass = DummyHass()
    entry = DummyEntry("test_entry_id", {
        "subpath": "2n-relay",
        "username": "admin",
        "relay_count": 1,
    })
    
    relay = RelaySwitch(hass, entry, relay_num=1)
    attrs = relay.extra_state_attributes
    
    # URLs should start with protocol and host
    assert attrs["relay_on_url"].startswith("http://")
    assert attrs["relay_off_url"].startswith("http://")
    assert attrs["relay_status_url"].startswith("http://")
    
    # URLs should contain /api/ path
    assert "/api/" in attrs["relay_on_url"]
    assert "/api/" in attrs["relay_off_url"]
    assert "/api/" in attrs["relay_status_url"]


@pytest.mark.asyncio
async def test_button_url_format():
    """Test that generated button URLs have correct format."""
    hass = DummyHass()
    entry = DummyEntry("test_entry_id", {
        "subpath": "2n-relay",
        "username": "admin",
        "button_count": 1,
    })
    
    button = RelayButton(hass, entry, button_num=1)
    attrs = button.extra_state_attributes
    
    # URLs should start with protocol and host
    assert attrs["button_trigger_url"].startswith("http://")
    assert attrs["button_status_url"].startswith("http://")
    
    # URLs should contain /api/ path
    assert "/api/" in attrs["button_trigger_url"]
    assert "/api/" in attrs["button_status_url"]
