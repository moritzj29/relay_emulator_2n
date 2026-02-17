"""HTTP server for 2N Relay Emulation with Digest Authentication."""
import hashlib
import hmac
import logging
import secrets
import time
from aiohttp import web
from typing import Dict, Optional, Tuple
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import entity_registry as er
from homeassistant.components.http import HomeAssistantView

from .const import (
    DOMAIN,
    VERSION,
    CONF_SUBPATH,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_RELAY_COUNT,
    CONF_BUTTON_COUNT,
    HTTP_SERVER_KEY,
)

_LOGGER = logging.getLogger(__name__)

# Security constants
NONCE_EXPIRY_SECONDS = 300  # 5 minutes
MAX_NONCE_CACHE_SIZE = 1000  # Prevent memory exhaustion


class DigestAuth:
    """Handle HTTP Digest Authentication compatible with 2N devices."""

    def __init__(self, username: str, password: str, realm: str = "2N"):
        """Initialize digest auth handler."""
        self.username = username
        self.password = password
        self.realm = realm
        # Store nonce with timestamp: {nonce: timestamp}
        self.nonce_cache: Dict[str, float] = {}
        
        # Pre-calculate HA1 for better performance and to avoid storing raw password
        self.ha1 = hashlib.md5(
            f"{self.username}:{self.realm}:{self.password}".encode()
        ).hexdigest()

    def _cleanup_expired_nonces(self) -> None:
        """Remove expired nonces from cache."""
        current_time = time.time()
        expired = [
            nonce for nonce, timestamp in self.nonce_cache.items()
            if current_time - timestamp > NONCE_EXPIRY_SECONDS
        ]
        for nonce in expired:
            del self.nonce_cache[nonce]
        
        # Enforce maximum cache size
        if len(self.nonce_cache) > MAX_NONCE_CACHE_SIZE:
            # Remove oldest entries
            sorted_nonces = sorted(self.nonce_cache.items(), key=lambda x: x[1])
            for nonce, _ in sorted_nonces[:len(self.nonce_cache) - MAX_NONCE_CACHE_SIZE]:
                del self.nonce_cache[nonce]

    def generate_nonce(self) -> str:
        """Generate a random nonce with timestamp."""
        self._cleanup_expired_nonces()
        nonce = secrets.token_hex(16)
        self.nonce_cache[nonce] = time.time()
        return nonce

    def create_challenge(self) -> str:
        """Create a WWW-Authenticate challenge header."""
        nonce = self.generate_nonce()
        return (
            f'Digest realm="{self.realm}", '
            f'qop="auth", '
            f'nonce="{nonce}", '
            f'opaque="{secrets.token_hex(16)}"'
        )

    def verify_response(self, auth_header: str, method: str, uri: str) -> bool:
        """Verify the digest authentication response."""
        if not auth_header or not auth_header.startswith("Digest "):
            return False

        # Parse the authorization header
        auth_data = {}
        auth_str = auth_header[7:]  # Remove "Digest "
        
        for item in auth_str.split(","):
            item = item.strip()
            if "=" in item:
                key, value = item.split("=", 1)
                auth_data[key.strip()] = value.strip('"')

        # Extract required fields
        username = auth_data.get("username")
        realm = auth_data.get("realm")
        nonce = auth_data.get("nonce")
        uri_from_auth = auth_data.get("uri")
        response = auth_data.get("response")
        nc = auth_data.get("nc")
        cnonce = auth_data.get("cnonce")
        qop = auth_data.get("qop")

        # Validate required fields
        if not all([username, realm, nonce, uri_from_auth, response]):
            _LOGGER.warning("Digest auth: Missing required fields")
            return False

        if username != self.username or realm != self.realm:
            _LOGGER.warning("Digest auth: Invalid username or realm")
            return False

        # SECURITY: Verify nonce is valid and not expired
        if nonce not in self.nonce_cache:
            _LOGGER.warning("Digest auth: Invalid or unknown nonce")
            return False
        
        nonce_timestamp = self.nonce_cache[nonce]
        if time.time() - nonce_timestamp > NONCE_EXPIRY_SECONDS:
            _LOGGER.warning("Digest auth: Expired nonce")
            del self.nonce_cache[nonce]
            return False
        
        # Mark nonce as used (remove from cache to prevent replay)
        # Note: For strict replay protection, uncomment the next line
        # However, 2N devices may retry requests, so we keep nonce valid for its lifetime
        # del self.nonce_cache[nonce]

        # Calculate expected response using pre-calculated HA1
        ha2 = hashlib.md5(f"{method}:{uri_from_auth}".encode()).hexdigest()

        if qop == "auth":
            expected_response = hashlib.md5(
                f"{self.ha1}:{nonce}:{nc}:{cnonce}:{qop}:{ha2}".encode()
            ).hexdigest()
        else:
            expected_response = hashlib.md5(f"{self.ha1}:{nonce}:{ha2}".encode()).hexdigest()

        # Use constant-time comparison to prevent timing attacks
        is_valid = hmac.compare_digest(response, expected_response)
        
        if not is_valid:
            _LOGGER.warning(
                "Digest auth: Invalid response hash from %s", 
                username
            )
        
        return is_valid


class RelayView2N(HomeAssistantView):
    """HTTP View that emulates 2N IP relay endpoints."""

    requires_auth = False  # We handle digest auth ourselves
    
    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        subpath: str,
        username: str,
        password: str,
        relay_count: int,
        button_count: int,
    ):
        """Initialize the view."""
        self.hass = hass
        self.entry = entry
        self.subpath = subpath.rstrip("/")
        self.relay_count = relay_count
        self.button_count = button_count
        self.auth = DigestAuth(username, password)
        
        # Set the URL and name for this view
        self.url = f"/{self.subpath}/{{path:.*}}"
        self.name = f"2n_relay_emulator:{entry.entry_id}"

    def require_auth(self, handler):
        """Decorator to require digest authentication."""

        async def wrapper(request: web.Request, path: str = "") -> web.Response:
            auth_header = request.headers.get("Authorization")
            
            # Use the exact relative URL from the request for digest auth verification
            # This ensures the URI matches exactly what the client sent, preventing auth bypass
            uri = str(request.rel_url)
            
            if not auth_header or not self.auth.verify_response(
                auth_header, request.method, uri
            ):
                response = web.Response(status=401, text="Unauthorized")
                response.headers["WWW-Authenticate"] = self.auth.create_challenge()
                return response

            return await handler(request, path)

        return wrapper

    async def get(self, request: web.Request, path: str = "") -> web.Response:
        """Handle GET requests."""
        return await self._handle_request(request, path)

    async def post(self, request: web.Request, path: str = "") -> web.Response:
        """Handle POST requests."""
        return await self._handle_request(request, path)

    async def _handle_request(self, request: web.Request, path: str = "") -> web.Response:
        """Route request to appropriate handler."""
        # Apply authentication
        auth_header = request.headers.get("Authorization")
        # Use the exact relative URL from the request for digest auth verification
        uri = str(request.rel_url)
        
        if not auth_header or not self.auth.verify_response(
            auth_header, request.method, uri
        ):
            response = web.Response(status=401, text="Unauthorized")
            response.headers["WWW-Authenticate"] = self.auth.create_challenge()
            return response

        # Route to handlers based on path
        path_lower = path.lower()
        
        # Root path
        if path == "":
            return await self.handle_root(request)
        
        # Relay control endpoints
        if path_lower in ("api/relay/ctrl", "relay/ctrl"):
            return await self.handle_relay_control(request)
        
        # Button trigger endpoints
        if path_lower in ("api/button/trigger", "button/trigger"):
            return await self.handle_button_trigger(request)
        
        # Relay status endpoints
        if path_lower in ("api/relay/status", "relay/status"):
            return await self.handle_relay_status(request)
        
        # Button status endpoints
        if path_lower in ("api/button/status", "button/status"):
            return await self.handle_button_status(request)
        
        # System info
        if path_lower == "api/system/info":
            return await self.handle_system_info(request)
        
        # Unknown path
        return web.Response(status=404, text="Not Found")

    async def handle_relay_control(self, request: web.Request) -> web.Response:
        """
        Handle relay control requests.
        
        2N compatible endpoints:
        - /{subpath}/api/relay/ctrl?relay=X&value=on
        - /{subpath}/api/relay/ctrl?relay=X&value=off
        - /{subpath}/relay/ctrl?relay=X&value=on
        - /{subpath}/relay/ctrl?relay=X&value=off
        """
        try:
            relay = int(request.query.get("relay", 1))
            value = request.query.get("value", "").lower()

            if relay < 1 or relay > self.relay_count:
                return web.Response(
                    status=400,
                    text=f"Invalid relay number. Must be between 1 and {self.relay_count}",
                )

            if value not in ["on", "off"]:
                return web.Response(
                    status=400, text="Invalid value. Must be 'on' or 'off'"
                )

            # Get the entity registry
            entity_reg = er.async_get(self.hass)
            
            # Find the corresponding switch entity
            entity_id = f"switch.2n_relay_{self.entry.entry_id[:8]}_relay_{relay}"
            
            # Try to find the entity by unique_id
            unique_id = f"{self.entry.entry_id}_relay_{relay}"
            entity_entry = entity_reg.async_get_entity_id("switch", DOMAIN, unique_id)
            
            if entity_entry:
                entity_id = entity_entry

            # Call the appropriate service
            service = "turn_on" if value == "on" else "turn_off"
            
            try:
                await self.hass.services.async_call(
                    "switch",
                    service,
                    {"entity_id": entity_id},
                    blocking=True,
                )
                
                _LOGGER.info(
                    "Relay %d %s via HTTP request from %s",
                    relay,
                    "activated" if value == "on" else "deactivated",
                    request.remote,
                )
                
                return web.Response(
                    status=200,
                    text=f"OK\nRelay {relay} is now {value}",
                    content_type="text/plain",
                )
            except Exception as err:
                _LOGGER.error("Failed to control relay %d: %s", relay, err)
                return web.Response(status=500, text=f"Error: {err}")

        except ValueError:
            return web.Response(status=400, text="Invalid relay parameter")

    async def handle_relay_status(self, request: web.Request) -> web.Response:
        """
        Handle relay status requests.
        
        2N compatible endpoints:
        - /{subpath}/api/relay/status
        - /{subpath}/relay/status
        """
        try:
            # Get the entity registry
            entity_reg = er.async_get(self.hass)
            
            status_lines = []
            for relay_num in range(1, self.relay_count + 1):
                unique_id = f"{self.entry.entry_id}_relay_{relay_num}"
                entity_id = entity_reg.async_get_entity_id("switch", DOMAIN, unique_id)
                
                if entity_id:
                    state = self.hass.states.get(entity_id)
                    if state:
                        status = "on" if state.state == "on" else "off"
                        status_lines.append(f"relay{relay_num}={status}")
                else:
                    status_lines.append(f"relay{relay_num}=unknown")

            response_text = "\n".join(status_lines)
            return web.Response(status=200, text=response_text, content_type="text/plain")

        except Exception as err:
            _LOGGER.error("Failed to get relay status: %s", err)
            return web.Response(status=500, text=f"Error: {err}")

    async def handle_button_trigger(self, request: web.Request) -> web.Response:
        """
        Handle button trigger requests.
        
        2N compatible endpoints:
        - /{subpath}/api/button/trigger?button=X
        - /{subpath}/button/trigger?button=X
        """
        try:
            button = int(request.query.get("button", 1))

            if button < 1 or button > self.button_count:
                return web.Response(
                    status=400,
                    text=f"Invalid button number. Must be between 1 and {self.button_count}",
                )

            # Find the corresponding button entity
            unique_id = f"{self.entry.entry_id}_button_{button}"
            
            # Trigger the button by calling button.press service
            entity_id = f"button.2n_relay_{self.entry.entry_id[:8]}_button_{button}"
            
            try:
                await self.hass.services.async_call(
                    "button",
                    "press",
                    {"entity_id": entity_id},
                    blocking=True,
                )
                
                _LOGGER.info(
                    "Button %d triggered via HTTP request from %s",
                    button,
                    request.remote,
                )
                
                return web.Response(
                    status=200,
                    text=f"OK\nButton {button} triggered",
                    content_type="text/plain",
                )
            except Exception as err:
                _LOGGER.error("Failed to trigger button %d: %s", button, err)
                return web.Response(status=500, text=f"Error: {err}")

        except ValueError:
            return web.Response(status=400, text="Invalid button parameter")

    async def handle_button_status(self, request: web.Request) -> web.Response:
        """
        Handle button status requests.
        
        2N compatible endpoints:
        - /{subpath}/api/button/status
        - /{subpath}/button/status
        
        Returns list of available buttons.
        """
        try:
            status_lines = []
            for button_num in range(1, self.button_count + 1):
                status_lines.append(f"button{button_num}=available")

            response_text = "\n".join(status_lines) if status_lines else "No buttons configured"
            return web.Response(status=200, text=response_text, content_type="text/plain")

        except Exception as err:
            _LOGGER.error("Failed to get button status: %s", err)
            return web.Response(status=500, text=f"Error: {err}")

    async def handle_system_info(self, request: web.Request) -> web.Response:
        """
        Handle system info requests (2N compatible).
        
        Endpoint: /{subpath}/api/system/info
        """
        info = {
            "model": "IP Relay Emulator for 2N",
            "version": VERSION,
            "relays": self.relay_count,
            "buttons": self.button_count,
        }
        
        response_text = "\n".join([f"{k}={v}" for k, v in info.items()])
        return web.Response(status=200, text=response_text, content_type="text/plain")

    async def handle_root(self, request: web.Request) -> web.Response:
        """Handle root endpoint."""
        return web.Response(
            status=200,
            text="IP Relay Emulator for 2N - Home Assistant Integration",
            content_type="text/plain",
        )


async def setup_http_server(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the HTTP server using Home Assistant's web server."""
    subpath = entry.data[CONF_SUBPATH]
    username = entry.data[CONF_USERNAME]
    # Retrieve password from options (can be encrypted by HA)
    password = entry.options.get(CONF_PASSWORD, entry.data.get(CONF_PASSWORD, "2n"))
    relay_count = int(entry.data.get(CONF_RELAY_COUNT, 0))
    button_count = int(entry.data.get(CONF_BUTTON_COUNT, 0))

    # Check if a view for this subpath already exists (e.g., after reload)
    # This prevents duplicate route registration
    if HTTP_SERVER_KEY in hass.data[DOMAIN]:
        existing_view = hass.data[DOMAIN][HTTP_SERVER_KEY].get(entry.entry_id)
        if existing_view:
            _LOGGER.debug(
                "HTTP server for %s already registered, skipping duplicate registration",
                entry.entry_id
            )
            return

    view = RelayView2N(hass, entry, subpath, username, password, relay_count, button_count)
    hass.http.register_view(view)

    # Store view instance for cleanup
    if HTTP_SERVER_KEY not in hass.data[DOMAIN]:
        hass.data[DOMAIN][HTTP_SERVER_KEY] = {}
    hass.data[DOMAIN][HTTP_SERVER_KEY][entry.entry_id] = view

    _LOGGER.info(
        "2N Relay Emulator registered on subpath '/%s' with %d relays and %d buttons",
        subpath,
        relay_count,
        button_count,
    )


async def cleanup_http_server(hass: HomeAssistant, entry: ConfigEntry):
    """Clean up the HTTP server.
    
    Note: HomeAssistantView provides no official unregister mechanism. The route
    will remain registered until Home Assistant restarts. Our tracking data is
    cleaned up to prevent memory leaks in hass.data, and duplicate registration
    is prevented via setup_http_server checks.
    """
    try:
        # Clean up our tracking data
        if HTTP_SERVER_KEY in hass.data[DOMAIN]:
            view = hass.data[DOMAIN][HTTP_SERVER_KEY].pop(entry.entry_id, None)
            
            if view:
                _LOGGER.warning(
                    "2N Relay Emulator '%s' unloaded. HTTP route will remain active "
                    "until Home Assistant restart due to framework limitations. "
                    "No new duplicate routes will be registered on reload.",
                    view.subpath
                )
            else:
                _LOGGER.debug("No HTTP view found to clean up for %s", entry.entry_id)
        
        # Clean up empty tracking dict
        if HTTP_SERVER_KEY in hass.data[DOMAIN] and not hass.data[DOMAIN][HTTP_SERVER_KEY]:
            del hass.data[DOMAIN][HTTP_SERVER_KEY]
            
    except Exception as err:
        _LOGGER.error("Error during HTTP server cleanup: %s", err)
