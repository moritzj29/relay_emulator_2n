# Quick Start Guide - 2N IP Relay Emulator

## What is this?

A **drop-in replacement** for 2N IP relay units that runs in Home Assistant using the same port as Home Assistant itself - no separate port needed!

## 5-Minute Setup

### Step 1: Install

```bash
# Copy the 2n_relay_emulator folder to:
/config/custom_components/2n_relay_emulator/

# Or run the install script:
chmod +x install.sh
./install.sh
```

### Step 2: Restart Home Assistant

```
Settings → System → Restart
```

### Step 3: Add Integration

1. Go to: **Settings → Devices & Services**
2. Click: **+ ADD INTEGRATION**
3. Search: **"2N IP Relay Emulator"**
4. Configure:
   - **Subpath**: `2n-relay` (or any unique path)
   - **Username**: `admin` (default)
   - **Password**: `2n` (default)
   - **Relays**: `2` (how many you need)
5. Click **Submit**

### Step 4: Configure Your 2N Device

Your endpoints will be at: `http://YOUR_HA:8123/2n-relay/`

**Example URL:**
```
http://192.168.1.100:8123/2n-relay/api/relay/ctrl?relay=1&value=on
```

**Authentication:**
- Type: **Digest**
- Username: **admin**
- Password: **2n**

### Step 5: Test

```bash
# From terminal
curl --digest -u admin:2n "http://YOUR_HA:8123/2n-relay/api/relay/ctrl?relay=1&value=on"

# Should return:
# OK
# Relay 1 is now on
```

## URL Format for 2N Devices

```
http://[HOME_ASSISTANT_IP]:[HA_PORT]/[SUBPATH]/api/relay/ctrl?relay=[1-8]&value=[on|off]
```

**Real Examples:**

Local access:
```
http://192.168.1.100:8123/2n-relay/api/relay/ctrl?relay=1&value=on
```

With SSL:
```
https://192.168.1.100:8123/2n-relay/api/relay/ctrl?relay=1&value=on
```

With Nabu Casa:
```
https://your-id.ui.nabu.casa/2n-relay/api/relay/ctrl?relay=1&value=on
```

## Key Advantages

✅ **Uses HA's port** - No separate port to configure  
✅ **Works with SSL** - Uses HA's existing HTTPS setup  
✅ **Works with Nabu Casa** - Remote access built-in  
✅ **Simpler networking** - No additional firewall rules  

## Multiple Instances

Use different subpaths for multiple instances:

- Instance 1: `/front-door/` → 2 relays
- Instance 2: `/garage/` → 4 relays

Each accessible at: `http://YOUR_HA:8123/[subpath]/`

## Testing Commands

```bash
# Test authentication
curl --digest -u admin:2n "http://localhost:8123/2n-relay/api/relay/status"

# Turn relay on
curl --digest -u admin:2n "http://localhost:8123/2n-relay/api/relay/ctrl?relay=1&value=on"

# Turn relay off
curl --digest -u admin:2n "http://localhost:8123/2n-relay/api/relay/ctrl?relay=1&value=off"

# System info
curl --digest -u admin:2n "http://localhost:8123/2n-relay/api/system/info"
```

## Troubleshooting

### Can't find integration?
- Check `/config/custom_components/2n_relay_emulator/` exists
- Restart Home Assistant

### 2N device can't connect?
- Verify HA is accessible at the URL
- Check credentials match exactly
- Test with curl first

### Subpath already in use?
- Choose a different subpath (e.g., `2n-relay-2`)

## Next Steps

1. ✅ Install and test
2. ✅ Update 2N device URL
3. ✅ Create automations
4. ✅ Enjoy!

See **README.md** for full documentation.
