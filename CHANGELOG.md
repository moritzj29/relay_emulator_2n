# Changelog - 2N IP Relay Emulator v2.0

## Major Update: Using Home Assistant's Built-in Web Server

### What Changed?

**Version 1.0 (Original):**
- Ran a separate HTTP server on a dedicated port (e.g., 8080)
- Required port configuration and firewall rules
- Separate from Home Assistant's web infrastructure

**Version 2.0 (Current):**
- Uses Home Assistant's built-in HTTP server
- Registers routes on a configurable subpath (e.g., `/2n-relay`)
- No separate port needed - uses HA's existing port (8123 or 443)

### Why This Is Better

✅ **Simpler Networking**
- No additional ports to open in firewall
- No port forwarding configuration
- Works with existing HA network setup

✅ **Better Security**
- Leverages HA's SSL/TLS configuration
- No separate HTTP server to secure
- Integrated with HA's security model

✅ **Remote Access Built-in**
- Automatically works with Nabu Casa Cloud
- Works with existing DuckDNS/Let's Encrypt setup
- No additional configuration for external access

✅ **Reverse Proxy Friendly**
- Works seamlessly with nginx, Apache, Caddy
- No additional proxy configuration needed
- Respects HA's existing proxy settings

✅ **Easier Management**
- Single port to monitor
- Integrated with HA's logging
- Standard HA troubleshooting applies

### Migration from v1.0 to v2.0

If you were using the old version with a separate port:

**Old URL format:**
```
http://192.168.1.100:8080/api/relay/ctrl?relay=1&value=on
```

**New URL format:**
```
http://192.168.1.100:8123/2n-relay/api/relay/ctrl?relay=1&value=on
```

**Changes needed:**
1. Remove old integration instance
2. Install new version
3. Add new integration with subpath configuration
4. Update 2N device URLs to use HA's port + subpath
5. Remove any firewall rules for the old port (optional)

### Configuration Changes

**Old Configuration:**
- Port: 8080 (required)
- Username: admin
- Password: 2n
- Relay Count: 2

**New Configuration:**
- Subpath: 2n-relay (required, alphanumeric + dashes/underscores)
- Username: admin
- Password: 2n
- Relay Count: 2

### Technical Implementation Details

**Old Approach (v1.0):**
```python
# Created a separate aiohttp application
self.app = web.Application()
self.runner = web.AppRunner(self.app)
self.site = web.TCPSite(self.runner, "0.0.0.0", port)
await self.site.start()
```

**New Approach (v2.0):**
```python
# Registers view with HA's HTTP server
view = TwoNRelayView(hass, entry, subpath, username, password, relay_count)
hass.http.register_view(view)
```

### URL Structure

**Multiple instances can coexist on different subpaths:**

Instance 1 (front door):
```
http://YOUR_HA:8123/front-door/api/relay/ctrl?relay=1&value=on
```

Instance 2 (garage):
```
http://YOUR_HA:8123/garage/api/relay/ctrl?relay=1&value=on
```

Instance 3 (basement):
```
http://YOUR_HA:8123/basement/api/relay/ctrl?relay=1&value=on
```

### Supported Endpoints

All endpoints now under `/{subpath}/`:

```
GET/POST  /{subpath}/api/relay/ctrl?relay=X&value=on|off
GET       /{subpath}/api/relay/status
GET       /{subpath}/api/system/info
GET/POST  /{subpath}/relay/ctrl?relay=X&value=on|off  (alternative)
GET       /{subpath}/relay/status  (alternative)
```

### SSL/HTTPS Support

With HA's SSL configuration:
```
https://YOUR_HA:443/2n-relay/api/relay/ctrl?relay=1&value=on
```

With Nabu Casa:
```
https://your-id.ui.nabu.casa/2n-relay/api/relay/ctrl?relay=1&value=on
```

### Backward Compatibility

**Not backward compatible** - URLs must be updated.

However, the API response format and authentication method remain identical, so only the URL needs to change in your 2N device configuration.

### Testing

Updated test script works with the new subpath approach:

```bash
python3 test_relay.py

# Configure at top of script:
HOST = "localhost"
PORT = 8123  # HA's port
SUBPATH = "2n-relay"  # Your configured subpath
```

### Troubleshooting

**Common issues and solutions:**

1. **404 Not Found**
   - Check subpath is configured correctly
   - Verify integration is loaded (Settings → Integrations)
   - Check HA logs for registration errors

2. **401 Unauthorized**
   - Verify digest auth credentials match
   - Check that 2N device is using "Digest" not "Basic" auth

3. **Connection Refused**
   - Verify Home Assistant is running
   - Check you're using HA's correct port (8123 or 443)
   - Test with curl first before configuring 2N device

4. **Subpath Already in Use**
   - Choose a different subpath for the instance
   - Remove old instance if no longer needed

### Debug Logging

Enable detailed logging:

```yaml
logger:
  default: info
  logs:
    custom_components.2n_relay_emulator: debug
    homeassistant.components.http: debug  # For HTTP server issues
```

### Performance

**Comparison:**

v1.0 (Separate server):
- Extra HTTP server overhead
- Additional TCP socket
- Separate request handling

v2.0 (Integrated):
- Uses HA's existing HTTP infrastructure
- Single HTTP server handling all requests
- Better resource utilization

### Future Considerations

This architecture provides a foundation for:
- Better integration with HA's authentication system (future)
- Support for HA's user permissions (future)
- Integration with HA's audit logging (future)
- Potential UI for monitoring relay activity (future)

### Conclusion

Version 2.0 represents a significant architectural improvement that makes the integration more maintainable, more secure, and easier to deploy while maintaining full compatibility with 2N devices.
