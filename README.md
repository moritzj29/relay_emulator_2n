# 2N IP Relay Emulator for Home Assistant

A Home Assistant custom component that emulates a 2N IP relay unit, providing HTTP endpoints compatible with 2N access control units (intercoms, door readers, etc.). This allows you to replace physical 2N IP relays with virtual ones controlled by Home Assistant.

**NEW:** Now uses Home Assistant's built-in web server on the same port - no separate port needed!

## Features

- **Drop-in replacement** for 2N IP relay units
- **Uses Home Assistant's HTTP server** - no separate port configuration needed
- **Dedicated subpath** - access at `http://homeassistant:8123/your-subpath/`
- **HTTP Digest Authentication** compatible with 2N devices
- **Multiple relay support** (1-8 relays per instance)
- **2N-compatible API endpoints**
- **Home Assistant switch integration** - control relays from HA UI, automations, or HTTP
- **Multiple instances** - run multiple emulators on different subpaths

## Supported Endpoints

The emulator provides the following 2N-compatible endpoints under your configured subpath:

### Relay Control
- `GET/POST /{subpath}/api/relay/ctrl?relay=X&value=on`
- `GET/POST /{subpath}/api/relay/ctrl?relay=X&value=off`
- `GET/POST /{subpath}/relay/ctrl?relay=X&value=on` (alternative path)
- `GET/POST /{subpath}/relay/ctrl?relay=X&value=off` (alternative path)

### Relay Status
- `GET /{subpath}/api/relay/status` - Returns status of all relays
- `GET /{subpath}/relay/status` (alternative path)

### System Information
- `GET /{subpath}/api/system/info` - Returns system information

All endpoints support HTTP Digest Authentication as expected by 2N devices.

## Installation

### Manual Installation

1. Copy the `2n_relay_emulator` folder to your `custom_components` directory:
   ```
   /config/custom_components/2n_relay_emulator/
   ```

2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ ADD INTEGRATION**
3. Search for "2N IP Relay Emulator"
4. Configure the integration:
   - **URL Subpath**: Path where endpoints will be available (default: `2n-relay`)
     - Example: `2n-relay` → access at `http://YOUR_HA:8123/2n-relay/`
   - **Username**: Username for digest authentication (default: `admin`)
   - **Password**: Password for digest authentication (default: `2n`)
   - **Number of Relays**: How many virtual relays to create (1-8, default: 2)

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
http://YOUR_HA_IP:8123/2n-relay/api/relay/ctrl?relay=1&value=on
```

**Example for 2N Indoor Touch:**
- URL: `http://192.168.1.100:8123/2n-relay/api/relay/ctrl?relay=1&value=on`
- Authentication: Digest
- Username: `admin`
- Password: `2n`

**Important:** Use your Home Assistant's IP/hostname and port (typically 8123).

### Testing with curl

```bash
# Turn relay 1 on
curl --digest -u admin:2n "http://localhost:8123/2n-relay/api/relay/ctrl?relay=1&value=on"

# Get status
curl --digest -u admin:2n "http://localhost:8123/2n-relay/api/relay/status"
```

## Advantages

✅ **No separate port** - uses HA's existing HTTP server  
✅ **Works with SSL** - automatically uses HA's SSL configuration  
✅ **Nabu Casa compatible** - works with Home Assistant Cloud  
✅ **Simpler networking** - no additional firewall rules needed  

## License

MIT License
