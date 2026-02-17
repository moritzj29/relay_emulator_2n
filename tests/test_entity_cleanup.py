"""Tests for entity cleanup functionality when relay/button counts change."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from custom_components.relay_emulator_2n import async_cleanup_orphaned_entities
from custom_components.relay_emulator_2n.const import (
    DOMAIN,
    CONF_RELAY_COUNT,
    CONF_BUTTON_COUNT,
)


class DummyHass:
    """Dummy Home Assistant instance for testing."""
    pass


class DummyEntry:
    """Dummy config entry for testing."""
    def __init__(self, entry_id, data):
        self.entry_id = entry_id
        self.data = data


class DummyEntityRegistry:
    """Mock entity registry for testing."""
    def __init__(self):
        self.entities = {}  # Track registered entities
        self.removed = []   # Track removed entity IDs

    def add_entity(self, entity_type, unique_id, entity_id):
        """Register an entity."""
        key = (entity_type, DOMAIN, unique_id)
        self.entities[key] = entity_id

    def async_get_entity_id(self, entity_type, domain, unique_id):
        """Get entity ID from registry."""
        key = (entity_type, domain, unique_id)
        return self.entities.get(key)

    def async_remove(self, entity_id):
        """Remove an entity."""
        self.removed.append(entity_id)


@pytest.mark.asyncio
async def test_cleanup_decrease_relay_count():
    """Test cleanup when decreasing relay count from 4 to 2."""
    hass = DummyHass()
    entry = DummyEntry("test_entry_1", {
        CONF_RELAY_COUNT: 4,
        CONF_BUTTON_COUNT: 0,
    })

    # Create mock entity registry with existing entities
    registry = DummyEntityRegistry()
    registry.add_entity("switch", "test_entry_1_relay_1", "switch.relay_1")
    registry.add_entity("switch", "test_entry_1_relay_2", "switch.relay_2")
    registry.add_entity("switch", "test_entry_1_relay_3", "switch.relay_3")
    registry.add_entity("switch", "test_entry_1_relay_4", "switch.relay_4")

    with patch("custom_components.relay_emulator_2n.er.async_get", return_value=registry):
        # Cleanup: from 4 to 2 relays
        await async_cleanup_orphaned_entities(hass, entry, new_relay_count=2, new_button_count=0)

    # Verify relays 3 and 4 were removed
    assert len(registry.removed) == 2
    assert "switch.relay_3" in registry.removed
    assert "switch.relay_4" in registry.removed


@pytest.mark.asyncio
async def test_cleanup_decrease_button_count():
    """Test cleanup when decreasing button count from 3 to 1."""
    hass = DummyHass()
    entry = DummyEntry("test_entry_2", {
        CONF_RELAY_COUNT: 0,
        CONF_BUTTON_COUNT: 3,
    })

    # Create mock entity registry with existing entities
    registry = DummyEntityRegistry()
    registry.add_entity("button", "test_entry_2_button_1", "button.button_1")
    registry.add_entity("button", "test_entry_2_button_2", "button.button_2")
    registry.add_entity("button", "test_entry_2_button_3", "button.button_3")

    with patch("custom_components.relay_emulator_2n.er.async_get", return_value=registry):
        # Cleanup: from 3 to 1 button
        await async_cleanup_orphaned_entities(hass, entry, new_relay_count=0, new_button_count=1)

    # Verify buttons 2 and 3 were removed
    assert len(registry.removed) == 2
    assert "button.button_2" in registry.removed
    assert "button.button_3" in registry.removed


@pytest.mark.asyncio
async def test_cleanup_increase_relay_count():
    """Test that no cleanup happens when increasing relay count."""
    hass = DummyHass()
    entry = DummyEntry("test_entry_3", {
        CONF_RELAY_COUNT: 2,
        CONF_BUTTON_COUNT: 0,
    })

    # Create mock entity registry with existing entities
    registry = DummyEntityRegistry()
    registry.add_entity("switch", "test_entry_3_relay_1", "switch.relay_1")
    registry.add_entity("switch", "test_entry_3_relay_2", "switch.relay_2")

    with patch("custom_components.relay_emulator_2n.er.async_get", return_value=registry):
        # Increase from 2 to 4 relays - no cleanup needed
        await async_cleanup_orphaned_entities(hass, entry, new_relay_count=4, new_button_count=0)

    # Verify no entities were removed
    assert len(registry.removed) == 0


@pytest.mark.asyncio
async def test_cleanup_mixed_counts_decrease_relays():
    """Test cleanup when decreasing relays but keeping buttons same."""
    hass = DummyHass()
    entry = DummyEntry("test_entry_4", {
        CONF_RELAY_COUNT: 3,
        CONF_BUTTON_COUNT: 2,
    })

    # Create mock entity registry with both relays and buttons
    registry = DummyEntityRegistry()
    # Relays
    registry.add_entity("switch", "test_entry_4_relay_1", "switch.relay_1")
    registry.add_entity("switch", "test_entry_4_relay_2", "switch.relay_2")
    registry.add_entity("switch", "test_entry_4_relay_3", "switch.relay_3")
    # Buttons
    registry.add_entity("button", "test_entry_4_button_1", "button.button_1")
    registry.add_entity("button", "test_entry_4_button_2", "button.button_2")

    with patch("custom_components.relay_emulator_2n.er.async_get", return_value=registry):
        # Decrease relays from 3 to 1, keep buttons at 2
        await async_cleanup_orphaned_entities(hass, entry, new_relay_count=1, new_button_count=2)

    # Verify only relay 2 and 3 were removed, buttons remain
    assert len(registry.removed) == 2
    assert "switch.relay_2" in registry.removed
    assert "switch.relay_3" in registry.removed
    assert "button.button_1" not in registry.removed
    assert "button.button_2" not in registry.removed


@pytest.mark.asyncio
async def test_cleanup_mixed_counts_decrease_both():
    """Test cleanup when decreasing both relays and buttons."""
    hass = DummyHass()
    entry = DummyEntry("test_entry_5", {
        CONF_RELAY_COUNT: 4,
        CONF_BUTTON_COUNT: 4,
    })

    # Create mock entity registry with both relays and buttons
    registry = DummyEntityRegistry()
    # Relays
    for i in range(1, 5):
        registry.add_entity("switch", f"test_entry_5_relay_{i}", f"switch.relay_{i}")
    # Buttons
    for i in range(1, 5):
        registry.add_entity("button", f"test_entry_5_button_{i}", f"button.button_{i}")

    with patch("custom_components.relay_emulator_2n.er.async_get", return_value=registry):
        # Decrease both from 4 to 2
        await async_cleanup_orphaned_entities(hass, entry, new_relay_count=2, new_button_count=2)

    # Verify 4 entities were removed (2 relays + 2 buttons)
    assert len(registry.removed) == 4
    assert "switch.relay_3" in registry.removed
    assert "switch.relay_4" in registry.removed
    assert "button.button_3" in registry.removed
    assert "button.button_4" in registry.removed


@pytest.mark.asyncio
async def test_cleanup_no_entities_to_remove():
    """Test cleanup when entity doesn't exist in registry."""
    hass = DummyHass()
    entry = DummyEntry("test_entry_6", {
        CONF_RELAY_COUNT: 3,
        CONF_BUTTON_COUNT: 0,
    })

    # Create mock entity registry with only 1 relay (simulating partial registry state)
    registry = DummyEntityRegistry()
    registry.add_entity("switch", "test_entry_6_relay_1", "switch.relay_1")
    # Relay 2 and 3 don't exist in registry

    with patch("custom_components.relay_emulator_2n.er.async_get", return_value=registry):
        # Decrease from 3 to 1 relay
        await async_cleanup_orphaned_entities(hass, entry, new_relay_count=1, new_button_count=0)

    # Verify no errors even though relay_2 and relay_3 don't exist
    assert len(registry.removed) == 0  # Only relay_1 exists, so none removed


@pytest.mark.asyncio
async def test_cleanup_zero_count():
    """Test cleanup when count goes to zero."""
    hass = DummyHass()
    entry = DummyEntry("test_entry_7", {
        CONF_RELAY_COUNT: 3,
        CONF_BUTTON_COUNT: 2,
    })

    # Create mock entity registry with entities
    registry = DummyEntityRegistry()
    # Relays
    for i in range(1, 4):
        registry.add_entity("switch", f"test_entry_7_relay_{i}", f"switch.relay_{i}")
    # Buttons
    for i in range(1, 3):
        registry.add_entity("button", f"test_entry_7_button_{i}", f"button.button_{i}")

    with patch("custom_components.relay_emulator_2n.er.async_get", return_value=registry):
        # Remove all relays and buttons
        await async_cleanup_orphaned_entities(hass, entry, new_relay_count=0, new_button_count=0)

    # Verify all entities were removed
    assert len(registry.removed) == 5
    for i in range(1, 4):
        assert f"switch.relay_{i}" in registry.removed
    for i in range(1, 3):
        assert f"button.button_{i}" in registry.removed


@pytest.mark.asyncio
async def test_cleanup_same_count():
    """Test that no cleanup happens when count stays the same."""
    hass = DummyHass()
    entry = DummyEntry("test_entry_8", {
        CONF_RELAY_COUNT: 2,
        CONF_BUTTON_COUNT: 2,
    })

    # Create mock entity registry
    registry = DummyEntityRegistry()
    registry.add_entity("switch", "test_entry_8_relay_1", "switch.relay_1")
    registry.add_entity("switch", "test_entry_8_relay_2", "switch.relay_2")
    registry.add_entity("button", "test_entry_8_button_1", "button.button_1")
    registry.add_entity("button", "test_entry_8_button_2", "button.button_2")

    with patch("custom_components.relay_emulator_2n.er.async_get", return_value=registry):
        # Same count: 2 relays and 2 buttons
        await async_cleanup_orphaned_entities(hass, entry, new_relay_count=2, new_button_count=2)

    # Verify no entities were removed
    assert len(registry.removed) == 0


@pytest.mark.asyncio
async def test_cleanup_different_entry_ids():
    """Test that cleanup only affects the specific entry."""
    hass = DummyHass()
    entry = DummyEntry("test_entry_A", {
        CONF_RELAY_COUNT: 2,
        CONF_BUTTON_COUNT: 0,
    })

    # Create mock entity registry with entities from different entries
    registry = DummyEntityRegistry()
    # Entities from entry A
    registry.add_entity("switch", "test_entry_A_relay_1", "switch.relay_1")
    registry.add_entity("switch", "test_entry_A_relay_2", "switch.relay_2")
    # Entities from entry B (should not be affected)
    registry.add_entity("switch", "test_entry_B_relay_1", "switch.relay_b_1")
    registry.add_entity("switch", "test_entry_B_relay_2", "switch.relay_b_2")

    with patch("custom_components.relay_emulator_2n.er.async_get", return_value=registry):
        # Cleanup entry A from 2 to 1 relay
        await async_cleanup_orphaned_entities(hass, entry, new_relay_count=1, new_button_count=0)

    # Verify only entry A's relay 2 was removed
    assert len(registry.removed) == 1
    assert "switch.relay_2" in registry.removed
    # Entry B's entities should not be in removed list
    assert "switch.relay_b_1" not in registry.removed
    assert "switch.relay_b_2" not in registry.removed
