# IP Relay Emulator for 2N devices for Home Assistant

A Home Assistant custom component that emulates a 2N IP relay unit, providing HTTP endpoints compatible with 2N access control units (intercoms, door readers, etc.). This allows you to replace physical 2N IP relays with virtual ones controlled by Home Assistant.

## Features

- **Drop-in replacement** for 2N IP relay units
- **Uses Home Assistant's HTTP server** - no separate port configuration needed
- **Dedicated subpath** - access at `http://homeassistant:8123/your-subpath/`
- **HTTP Digest Authentication** compatible with 2N devices
- **Relays and Buttons supported** (0-16 relays and 0-16 buttons per instance)
- **Multiple instances** - run multiple emulators on different subpaths

### Comparison to existing solutions

#### 2N API / custom components

Custom components exist which implement the 2N HTTP API, e.g.

- https://github.com/SVD-NL/helios2n-hass
- https://github.com/genka13/ha-2n-intercom

While using the official HTTP API is of course the best way to control the device, it has limitations in registering events in real-time. So far the above components need to actively query the device log to check for state changes. This may result in some delay until events are reflected in the Home Assistant entities.

Alternatively the 2N devices are able to actively send HTTP requests for e.g. relay activation or via automation (`SendHTTPRequest`).

**This integration does not poll the 2N device but provides an endpoint which the 2N device can trigger directly.**

#### Home Assistant Webhooks

Using the 2N Automation feature and the `SendHTTPRequest` function it is possible to trigger Home Assistant webhooks. Home Assistant webhooks are "protected" only by a randomized endpoint URL (security by obscurity). While this may be sufficient for many use cases, for access control you probably strive for some more protection.

While Home Assistant provides a protected REST API out of the box, this requires control over the request header to pass the authentication token. This is currently not supported by the 2N software (neither for relay activation nor via automation `SendHTTPRequest`).

2N devices support basic or digest authentication for HTTP requests.

**This integration protects the HTTP endpoint by simple Digest Authentication.**

## Supported Endpoints

The emulator provides the following 2N-compatible endpoints under your configured subpath:

### Relays (Maintain State)

#### Relay Control
- `GET/POST /{subpath}/api/relay/ctrl?relay=X&value=on`
- `GET/POST /{subpath}/api/relay/ctrl?relay=X&value=off`
- `GET/POST /{subpath}/relay/ctrl?relay=X&value=on` (alternative path)
- `GET/POST /{subpath}/relay/ctrl?relay=X&value=off` (alternative path)

#### Relay Status
- `GET /{subpath}/api/relay/status` - Returns status of all relays
- `GET /{subpath}/relay/status` (alternative path)

### Buttons (Momentary Trigger)

#### Button Control
- `GET /{subpath}/api/button/trigger?button=N`
- `GET /{subpath}/button/trigger?button=N`

#### Button Status
- `GET /{subpath}/api/button/status`
- `GET /{subpath}/button/status`


### System Information
- `GET /{subpath}/api/system/info` - Returns system information

All endpoints support HTTP Digest Authentication as expected by 2N devices.

## Installation

### Manual Installation

1. Copy the `relay_emulator_2n` folder to your `custom_components` directory:
   ```
   /config/custom_components/relay_emulator_2n/
   ```

2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ ADD INTEGRATION**
3. Search for "IP Relay Emulator for 2N"
4. Configure the integration:
   - **URL Subpath**: Path where endpoints will be available (default: `2n-relay`)
     - Example: `2n-relay` → access at `http://YOUR_HA:8123/2n-relay/`
     - Rules:
       - Letters, numbers, dash, underscore, forward slash only
       - No consecutive slashes (`//`)
       - No leading or trailing slashes
   - **Username**: Username for digest authentication (default: `admin`)
   - **Password**: Password for digest authentication (default: `2n`)
   - **Number of Relays**: How many virtual relays to create (0-16, default: 2)
   - **Number of Buttons**: How many virtual buttons to create (0-16, default: 0)

5. Click **Submit**

## Usage

### Home Assistant UI

After installation, you'll see switch entities for each relay:
- `switch.2n_relay_emulator_relay_1`
- `switch.2n_relay_emulator_relay_2`
- etc.

### HTTP API (from 2N devices)

Configure your 2N access unit to send HTTP requests to:

```
https://YOUR_HA_IP:8123/2n-relay/api/relay/ctrl?relay=1&value=on
```

**Example**
- URL: `https://192.168.1.100:8123/2n-relay/api/relay/ctrl?relay=1&value=on`
- Authentication: Digest
- Username: `admin`
- Password: `2n`

**Important:** Use your Home Assistant's IP/hostname and port (typically 8123). Using HTTPS is highly recommended, otherwise credentials are not encrpyted!

### Testing with curl

```bash
# Turn relay 1 on
curl --digest -u admin:2n "http://localhost:8123/2n-relay/api/relay/ctrl?relay=1&value=on"

# Get status
curl --digest -u admin:2n "http://localhost:8123/2n-relay/api/relay/status"
```

## Multiple Instances

Use different subpaths for multiple instances:

- Instance 1: `/front-door/` → 2 relays
- Instance 2: `/garage/` → 4 relays

Each accessible at: `http://YOUR_HA:8123/[subpath]/`

For each instance a different set of credentials can be specified.

## Futher security considerations

- This component is distributed as a proof-of-concept. **Please ensure to assess potential security risks when using this integration in productive environments!**
- Ensure Home Assistant is available only via HTTPS to prevent unencrypted requests.
- Credentials for accessing the HTTP endpoint are stored in the Home Assistant configuration. This is encrypted by default, but can be decrypted by everyone having filesystem access. Also ensure that config backups are encrypted!
- Consider restricting access to the HTTP endpoint on network level (segregation into VLANs, restrict accessability to certain IPs)
- For an additional layer of security consider implementing mTLS (supported by 2N).

## License

MIT License
