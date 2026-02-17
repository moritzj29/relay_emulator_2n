import types
import asyncio
import pytest
from types import SimpleNamespace

from custom_components.relay_emulator_2n.http_server import RelayView2N


class DummyServices:
    def __init__(self):
        self.calls = []

    async def async_call(self, domain, service, data, blocking=True):
        self.calls.append((domain, service, data, blocking))
        return None


class DummyHass:
    def __init__(self):
        self.services = DummyServices()
        self.states = {}
        self.http = SimpleNamespace(app=None)


class DummyEntry:
    def __init__(self, entry_id, data):
        self.entry_id = entry_id
        self.data = data


class Registry:
    def __init__(self, mapping):
        self.mapping = mapping

    def async_get_entity_id(self, _platform, _domain, unique_id):
        return self.mapping.get(unique_id)


# ============================================================================
# Relay Control Tests
# ============================================================================

@pytest.mark.asyncio
async def test_handle_relay_control_turn_on(monkeypatch):
    hass = DummyHass()
    entry = DummyEntry("abcd1234", {"subpath": "2n-relay", "username": "admin", "relay_count": 2, "button_count": 0})

    # Map unique id to an entity id
    unique = f"{entry.entry_id}_relay_1"
    registry = Registry({unique: "switch.test_relay1"})

    # Monkeypatch the entity registry getter
    import homeassistant.helpers.entity_registry as er

    monkeypatch.setattr(er, "async_get", lambda hass_arg: registry)

    # Prepare hass state for entity
    hass.states["switch.test_relay1"] = SimpleNamespace(state="off")

    view = RelayView2N(hass, entry, entry.data["subpath"], "admin", "2n", 2, 0)

    class Req:
        def __init__(self):
            self.query = {"relay": "1", "value": "on"}
            self.remote = "127.0.0.1"

    req = Req()

    resp = await view.handle_relay_control(req)

    assert resp.status == 200
    assert "Relay 1 is now on" in resp.text
    # Ensure service call was made
    assert hass.services.calls
    domain, service, data, blocking = hass.services.calls[0]
    assert domain == "switch"
    assert service == "turn_on"
    assert data["entity_id"] == "switch.test_relay1"


@pytest.mark.asyncio
async def test_handle_relay_control_turn_off(monkeypatch):
    hass = DummyHass()
    entry = DummyEntry("abcd1234", {"subpath": "2n-relay", "username": "admin", "relay_count": 2, "button_count": 0})

    registry = Registry({f"{entry.entry_id}_relay_2": "switch.r2"})
    import homeassistant.helpers.entity_registry as er
    monkeypatch.setattr(er, "async_get", lambda hass_arg: registry)

    hass.states["switch.r2"] = SimpleNamespace(state="on")

    view = RelayView2N(hass, entry, entry.data["subpath"], "admin", "2n", 2, 0)

    class Req:
        def __init__(self):
            self.query = {"relay": "2", "value": "off"}
            self.remote = "127.0.0.1"

    req = Req()
    resp = await view.handle_relay_control(req)

    assert resp.status == 200
    assert "Relay 2 is now off" in resp.text
    assert hass.services.calls
    domain, service, _, _ = hass.services.calls[0]
    assert domain == "switch"
    assert service == "turn_off"


@pytest.mark.asyncio
async def test_handle_relay_control_invalid_relay_number(monkeypatch):
    hass = DummyHass()
    entry = DummyEntry("abcd1234", {"subpath": "2n-relay", "username": "admin", "relay_count": 2, "button_count": 0})

    registry = Registry({})
    import homeassistant.helpers.entity_registry as er
    monkeypatch.setattr(er, "async_get", lambda hass_arg: registry)

    view = RelayView2N(hass, entry, entry.data["subpath"], "admin", "2n", 2, 0)

    class Req:
        def __init__(self):
            self.query = {"relay": "5", "value": "on"}
            self.remote = "127.0.0.1"

    req = Req()
    resp = await view.handle_relay_control(req)

    assert resp.status == 400
    assert "Invalid relay number" in resp.text


@pytest.mark.asyncio
async def test_handle_relay_control_invalid_value(monkeypatch):
    hass = DummyHass()
    entry = DummyEntry("abcd1234", {"subpath": "2n-relay", "username": "admin", "relay_count": 2, "button_count": 0})

    registry = Registry({f"{entry.entry_id}_relay_1": "switch.r1"})
    import homeassistant.helpers.entity_registry as er
    monkeypatch.setattr(er, "async_get", lambda hass_arg: registry)

    view = RelayView2N(hass, entry, entry.data["subpath"], "admin", "2n", 2, 0)

    class Req:
        def __init__(self):
            self.query = {"relay": "1", "value": "invalid"}
            self.remote = "127.0.0.1"

    req = Req()
    resp = await view.handle_relay_control(req)

    assert resp.status == 400
    assert "Must be 'on' or 'off'" in resp.text


@pytest.mark.asyncio
async def test_handle_relay_control_invalid_relay_param(monkeypatch):
    hass = DummyHass()
    entry = DummyEntry("abcd1234", {"subpath": "2n-relay", "username": "admin", "relay_count": 2, "button_count": 0})

    registry = Registry({})
    import homeassistant.helpers.entity_registry as er
    monkeypatch.setattr(er, "async_get", lambda hass_arg: registry)

    view = RelayView2N(hass, entry, entry.data["subpath"], "admin", "2n", 2, 0)

    class Req:
        def __init__(self):
            self.query = {"relay": "notanumber", "value": "on"}
            self.remote = "127.0.0.1"

    req = Req()
    resp = await view.handle_relay_control(req)

    assert resp.status == 400
    assert "Invalid relay parameter" in resp.text


# ============================================================================
# Relay Status Tests
# ============================================================================

@pytest.mark.asyncio
async def test_handle_relay_status(monkeypatch):
    hass = DummyHass()
    entry = DummyEntry("abcd1234", {"subpath": "2n-relay", "username": "admin", "relay_count": 2, "button_count": 0})

    # Map unique ids to entity ids
    registry = Registry({f"{entry.entry_id}_relay_1": "switch.r1", f"{entry.entry_id}_relay_2": None})
    import homeassistant.helpers.entity_registry as er
    monkeypatch.setattr(er, "async_get", lambda hass_arg: registry)

    # Prepare hass states
    hass.states["switch.r1"] = SimpleNamespace(state="on")

    view = RelayView2N(hass, entry, entry.data["subpath"], "admin", "2n", 2, 0)

    class Req:
        def __init__(self):
            self.query = {}
            self.remote = "127.0.0.1"

    req = Req()

    resp = await view.handle_relay_status(req)

    assert resp.status == 200
    text = resp.text
    assert "relay1=on" in text
    assert "relay2=unknown" in text


@pytest.mark.asyncio
async def test_handle_relay_status_all_off(monkeypatch):
    hass = DummyHass()
    entry = DummyEntry("abcd1234", {"subpath": "2n-relay", "username": "admin", "relay_count": 3, "button_count": 0})

    registry = Registry({
        f"{entry.entry_id}_relay_1": "switch.r1",
        f"{entry.entry_id}_relay_2": "switch.r2",
        f"{entry.entry_id}_relay_3": "switch.r3",
    })
    import homeassistant.helpers.entity_registry as er
    monkeypatch.setattr(er, "async_get", lambda hass_arg: registry)

    hass.states["switch.r1"] = SimpleNamespace(state="off")
    hass.states["switch.r2"] = SimpleNamespace(state="off")
    hass.states["switch.r3"] = SimpleNamespace(state="off")

    view = RelayView2N(hass, entry, entry.data["subpath"], "admin", "2n", 3, 0)

    class Req:
        def __init__(self):
            self.query = {}

    req = Req()
    resp = await view.handle_relay_status(req)

    assert resp.status == 200
    text = resp.text
    assert "relay1=off" in text
    assert "relay2=off" in text
    assert "relay3=off" in text


# ============================================================================
# Button Trigger Tests
# ============================================================================

@pytest.mark.asyncio
async def test_handle_button_trigger(monkeypatch):
    hass = DummyHass()
    entry = DummyEntry("abcd1234", {"subpath": "2n-relay", "username": "admin", "relay_count": 0, "button_count": 2})

    view = RelayView2N(hass, entry, entry.data["subpath"], "admin", "2n", 0, 2)

    class Req:
        def __init__(self):
            self.query = {"button": "1"}
            self.remote = "127.0.0.1"

    req = Req()
    resp = await view.handle_button_trigger(req)

    assert resp.status == 200
    assert "Button 1 triggered" in resp.text
    assert hass.services.calls
    domain, service, data, blocking = hass.services.calls[0]
    assert domain == "button"
    assert service == "press"


@pytest.mark.asyncio
async def test_handle_button_trigger_invalid_number(monkeypatch):
    hass = DummyHass()
    entry = DummyEntry("abcd1234", {"subpath": "2n-relay", "username": "admin", "relay_count": 0, "button_count": 2})

    view = RelayView2N(hass, entry, entry.data["subpath"], "admin", "2n", 0, 2)

    class Req:
        def __init__(self):
            self.query = {"button": "10"}
            self.remote = "127.0.0.1"

    req = Req()
    resp = await view.handle_button_trigger(req)

    assert resp.status == 400
    assert "Invalid button number" in resp.text


@pytest.mark.asyncio
async def test_handle_button_trigger_invalid_param(monkeypatch):
    hass = DummyHass()
    entry = DummyEntry("abcd1234", {"subpath": "2n-relay", "username": "admin", "relay_count": 0, "button_count": 2})

    view = RelayView2N(hass, entry, entry.data["subpath"], "admin", "2n", 0, 2)

    class Req:
        def __init__(self):
            self.query = {"button": "notanumber"}
            self.remote = "127.0.0.1"

    req = Req()
    resp = await view.handle_button_trigger(req)

    assert resp.status == 400
    assert "Invalid button parameter" in resp.text


# ============================================================================
# Button Status Tests
# ============================================================================

@pytest.mark.asyncio
async def test_handle_button_status_multiple(monkeypatch):
    hass = DummyHass()
    entry = DummyEntry("abcd1234", {"subpath": "2n-relay", "username": "admin", "relay_count": 0, "button_count": 3})

    view = RelayView2N(hass, entry, entry.data["subpath"], "admin", "2n", 0, 3)

    class Req:
        def __init__(self):
            self.query = {}

    req = Req()
    resp = await view.handle_button_status(req)

    assert resp.status == 200
    text = resp.text
    assert "button1=available" in text
    assert "button2=available" in text
    assert "button3=available" in text


@pytest.mark.asyncio
async def test_handle_button_status_no_buttons(monkeypatch):
    hass = DummyHass()
    entry = DummyEntry("abcd1234", {"subpath": "2n-relay", "username": "admin", "relay_count": 0, "button_count": 0})

    view = RelayView2N(hass, entry, entry.data["subpath"], "admin", "2n", 0, 0)

    class Req:
        def __init__(self):
            self.query = {}

    req = Req()
    resp = await view.handle_button_status(req)

    assert resp.status == 200
    assert "No buttons configured" in resp.text


# ============================================================================
# System Info & Root Endpoint Tests
# ============================================================================

@pytest.mark.asyncio
async def test_handle_system_info(monkeypatch):
    hass = DummyHass()
    entry = DummyEntry("abcd1234", {"subpath": "2n-relay", "username": "admin", "relay_count": 3, "button_count": 2})

    view = RelayView2N(hass, entry, entry.data["subpath"], "admin", "2n", 3, 2)

    class Req:
        def __init__(self):
            self.query = {}

    req = Req()
    resp = await view.handle_system_info(req)

    assert resp.status == 200
    text = resp.text
    assert "model=IP Relay Emulator for 2N" in text
    assert "relays=3" in text
    assert "buttons=2" in text


@pytest.mark.asyncio
async def test_handle_root(monkeypatch):
    hass = DummyHass()
    entry = DummyEntry("abcd1234", {"subpath": "2n-relay", "username": "admin", "relay_count": 1, "button_count": 1})

    view = RelayView2N(hass, entry, entry.data["subpath"], "admin", "2n", 1, 1)

    class Req:
        def __init__(self):
            self.query = {}

    req = Req()
    resp = await view.handle_root(req)

    assert resp.status == 200
    assert "IP Relay Emulator for 2N" in resp.text