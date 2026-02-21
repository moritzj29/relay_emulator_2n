"""Tests for HTTP route lifecycle during config entry reloads."""
from types import SimpleNamespace

import pytest

from custom_components.relay_emulator_2n.const import (
    CONF_BUTTON_COUNT,
    CONF_PASSWORD,
    CONF_RELAY_COUNT,
    CONF_SUBPATH,
    CONF_USERNAME,
    DOMAIN,
    HTTP_SERVER_KEY,
)
from custom_components.relay_emulator_2n.http_server import cleanup_http_server, setup_http_server


class DummyEntry:
    """Minimal config entry test double."""

    def __init__(self, entry_id, data, options=None):
        self.entry_id = entry_id
        self.data = data
        self.options = options or {}


class DummyResource:
    """Simple router resource for tests."""

    def __init__(self, name, formatter):
        self.name = name
        self._formatter = formatter

    def get_info(self):
        return {"formatter": self._formatter}


class DummyRouter:
    """Minimal aiohttp-like router structure used by the integration."""

    def __init__(self):
        self._resources = []
        self._named_resources = {}
        self._resource_index = {}

    def named_resources(self):
        return self._named_resources

    def resources(self):
        return list(self._resources)


class DummyHTTP:
    """HTTP object exposing register_view and app.router."""

    def __init__(self):
        self.app = SimpleNamespace(router=DummyRouter())

    def register_view(self, view):
        router = self.app.router
        if view.name in router._named_resources:
            raise ValueError(f"Duplicate route name: {view.name}")
        resource = DummyResource(view.name, view.url)
        router._resources.append(resource)
        router._named_resources[view.name] = resource
        router._resource_index.setdefault(view.url, []).append(resource)


class DummyHass:
    """Minimal hass object for setup/cleanup route tests."""

    def __init__(self):
        self.http = DummyHTTP()
        self.data = {DOMAIN: {}}


@pytest.mark.asyncio
async def test_route_replaced_on_reload_from_button_to_relay():
    """Reload should remove old route and re-register route with new counts."""
    hass = DummyHass()

    entry_id = "entry_1"
    old_entry = DummyEntry(
        entry_id,
        {
            CONF_SUBPATH: "2n-relay",
            CONF_USERNAME: "admin",
            CONF_RELAY_COUNT: 0,
            CONF_BUTTON_COUNT: 1,
        },
        {CONF_PASSWORD: "2n"},
    )
    await setup_http_server(hass, old_entry)

    old_view = hass.data[DOMAIN][HTTP_SERVER_KEY][entry_id]
    assert old_view.relay_count == 0
    assert old_view.button_count == 1

    await cleanup_http_server(hass, old_entry)
    assert entry_id not in hass.http.app.router._named_resources

    new_entry = DummyEntry(
        entry_id,
        {
            CONF_SUBPATH: "2n-relay",
            CONF_USERNAME: "admin",
            CONF_RELAY_COUNT: 1,
            CONF_BUTTON_COUNT: 0,
        },
        {CONF_PASSWORD: "2n"},
    )
    await setup_http_server(hass, new_entry)

    new_view = hass.data[DOMAIN][HTTP_SERVER_KEY][entry_id]
    assert new_view.relay_count == 1
    assert new_view.button_count == 0
    assert new_view.url == "/2n-relay/{path:.*}"
    assert len(hass.http.app.router._resources) == 1
    assert new_view.name in hass.http.app.router._named_resources


@pytest.mark.asyncio
async def test_setup_replaces_existing_view_for_same_entry():
    """setup_http_server should replace stale tracked view for same entry id."""
    hass = DummyHass()
    entry_id = "entry_2"

    first_entry = DummyEntry(
        entry_id,
        {
            CONF_SUBPATH: "2n-relay",
            CONF_USERNAME: "admin",
            CONF_RELAY_COUNT: 0,
            CONF_BUTTON_COUNT: 1,
        },
        {CONF_PASSWORD: "2n"},
    )
    await setup_http_server(hass, first_entry)

    second_entry = DummyEntry(
        entry_id,
        {
            CONF_SUBPATH: "2n-relay",
            CONF_USERNAME: "admin",
            CONF_RELAY_COUNT: 1,
            CONF_BUTTON_COUNT: 0,
        },
        {CONF_PASSWORD: "2n"},
    )
    await setup_http_server(hass, second_entry)

    view = hass.data[DOMAIN][HTTP_SERVER_KEY][entry_id]
    assert view.relay_count == 1
    assert view.button_count == 0
    assert len(hass.http.app.router._resources) == 1
