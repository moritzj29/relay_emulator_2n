# 2N IP Relay Emulator v2.0 - Feature Documentation

## What's New in v2.0

### ✨ New Features

#### 1. **Button Support (Momentary Triggers)**
In addition to relays (switches), you can now configure buttons:
- **Relays (Switches)**: Maintain state (on/off) - useful for door locks
- **Buttons**: Momentary triggers with no state - useful for door strikes or gate openers

#### 2. **Nested Subpath Support**
Configure hierarchical URL paths:
- Simple: `2n-relay` → `http://ha:8123/2n-relay/...`
- Nested: `2n/door1` → `http://ha:8123/2n/door1/...`
- Deep nesting: `building/floor2/entrance` → `http://ha:8123/building/floor2/entrance/...`

#### 3. **Number Input for Configuration**
Relay and button counts now use proper number input boxes instead of sliders:
- Min: 0, Max: 16 for both relays and buttons
- More precise input
- Better UX for larger installations

---

## Button vs Relay - When to Use What?

### Use **Relays (Switches)** for:
✅ Door locks requiring continuous power
✅ Electric door openers that stay open
✅ Garage doors
✅ Gates that need "hold open" functionality
✅ Anything requiring state tracking (on/off)

### Use **Buttons** for:
✅ Electric door strikes (momentary unlock)
✅ Gate openers (pulse trigger)
✅ Momentary buzzers or alarms
✅ One-time actions that don't need state
✅ 2N "impulse" outputs

**Example Setup:**
```yaml
Configuration:
- Relays: 2 (main door lock + garage door)
- Buttons: 4 (door strike 1, door strike 2, gate, emergency release)
```

---

## API Endpoints

### Relay Endpoints (Switches)
```bash
# Turn relay on
GET/POST /{subpath}/api/relay/ctrl?relay=1&value=on

# Turn relay off
GET/POST /{subpath}/api/relay/ctrl?relay=1&value=off

# Get relay status
GET /{subpath}/api/relay/status
# Returns:
# relay1=on
# relay2=off
```

### Button Endpoints (NEW)
```bash
# Trigger button (momentary)
GET/POST /{subpath}/api/button/trigger?button=1

# Get button status (list available buttons)
GET /{subpath}/api/button/status
# Returns:
# button1=available
# button2=available
```

### System Info
```bash
GET /{subpath}/api/system/info
# Returns:
# model=2N IP Relay Emulator
# version=2.0.0
# relays=2
# buttons=4
```

---

## Configuration Examples

### Example 1: Single Door System
```
Configuration:
- Subpath: door1
- Relays: 1 (main lock)
- Buttons: 1 (strike for quick entry)

URLs:
- Lock: http://ha:8123/door1/api/relay/ctrl?relay=1&value=on
- Strike: http://ha:8123/door1/api/button/trigger?button=1
```

### Example 2: Multi-Door Building
```
Instance 1 - Front Entrance:
- Subpath: building/entrance/front
- Relays: 1
- Buttons: 2

Instance 2 - Back Entrance:
- Subpath: building/entrance/back
- Relays: 1
- Buttons: 1

Instance 3 - Garage:
- Subpath: building/garage
- Relays: 2
- Buttons: 0
```

### Example 3: Complex Installation
```
Configuration:
- Subpath: 2n/main
- Relays: 4 (front door, back door, gate, garage)
- Buttons: 6 (4x door strikes, 1x buzzer, 1x emergency)

Access:
http://ha:8123/2n/main/api/relay/ctrl?relay=1&value=on
http://ha:8123/2n/main/api/button/trigger?button=1
```

---

## Home Assistant Entities

After configuration, entities are created automatically:

### Relays (Switches)
```
switch.2n_relay_emulator_relay_1
switch.2n_relay_emulator_relay_2
...
```

**Properties:**
- State: on/off
- Can be toggled
- State persists until changed
- Visible in UI

### Buttons
```
button.2n_relay_emulator_button_1
button.2n_relay_emulator_button_2
...
```

**Properties:**
- No state (stateless)
- Press action only
- Triggers automations
- Shows last pressed time

---

## 2N Device Configuration

### For Door Locks (Use Relay)
```
2N Configuration:
- Type: HTTP Switch
- URL ON: http://ha:8123/2n/door1/api/relay/ctrl?relay=1&value=on
- URL OFF: http://ha:8123/2n/door1/api/relay/ctrl?relay=1&value=off
- Auth: Digest
- User: admin
- Pass: your_password
```

### For Door Strikes (Use Button)
```
2N Configuration:
- Type: HTTP Action
- URL: http://ha:8123/2n/door1/api/button/trigger?button=1
- Method: GET or POST
- Auth: Digest
- User: admin
- Pass: your_password
```

---

## Automation Examples

### Example 1: Button Triggers Door Unlock
```yaml
automation:
  - id: 'door_strike_pressed'
    alias: "Door Strike Button - Unlock Main Door"
    trigger:
      - platform: event
        event_type: button_pressed
        event_data:
          entity_id: button.2n_relay_emulator_button_1
    action:
      - service: lock.unlock
        target:
          entity_id: lock.front_door
      - delay:
          seconds: 5
      - service: lock.lock
        target:
          entity_id: lock.front_door
```

### Example 2: Relay Controls Gate
```yaml
automation:
  - id: 'gate_relay_control'
    alias: "Gate Relay - Open/Close Gate"
    trigger:
      - platform: state
        entity_id: switch.2n_relay_emulator_relay_1
        to: "on"
    action:
      - service: cover.open_cover
        target:
          entity_id: cover.main_gate
      - wait_for_trigger:
          - platform: state
            entity_id: switch.2n_relay_emulator_relay_1
            to: "off"
      - service: cover.close_cover
        target:
          entity_id: cover.main_gate
```

### Example 3: Button with Notification
```yaml
automation:
  - id: 'button_notify'
    alias: "Button Pressed - Send Notification"
    trigger:
      - platform: event
        event_type: button_pressed
        event_data:
          entity_id: button.2n_relay_emulator_button_1
    action:
      - service: notify.mobile_app
        data:
          title: "Door Access"
          message: "Door strike activated at {{ now().strftime('%H:%M') }}"
      - service: camera.snapshot
        target:
          entity_id: camera.front_door
        data:
          filename: "/config/www/snapshots/door_{{ now().strftime('%Y%m%d_%H%M%S') }}.jpg"
```

---

## Nested Subpath Use Cases

### Use Case 1: Multi-Building Campus
```
building1/entrance → http://ha:8123/building1/entrance/...
building1/garage   → http://ha:8123/building1/garage/...
building2/entrance → http://ha:8123/building2/entrance/...
building2/garage   → http://ha:8123/building2/garage/...
```

### Use Case 2: Floor-Based Organization
```
floor1/main-door   → http://ha:8123/floor1/main-door/...
floor1/side-door   → http://ha:8123/floor1/side-door/...
floor2/office-door → http://ha:8123/floor2/office-door/...
floor2/server-room → http://ha:8123/floor2/server-room/...
```

### Use Case 3: Location Hierarchy
```
site/location/device
↓
chicago/warehouse/dock1   → http://ha:8123/chicago/warehouse/dock1/...
chicago/warehouse/dock2   → http://ha:8123/chicago/warehouse/dock2/...
newyork/office/main       → http://ha:8123/newyork/office/main/...
```

---

## Testing

### Test Relay
```bash
# Turn on
curl --digest -u admin:2n "http://localhost:8123/2n/door1/api/relay/ctrl?relay=1&value=on"

# Turn off
curl --digest -u admin:2n "http://localhost:8123/2n/door1/api/relay/ctrl?relay=1&value=off"

# Check status
curl --digest -u admin:2n "http://localhost:8123/2n/door1/api/relay/status"
```

### Test Button
```bash
# Trigger button
curl --digest -u admin:2n "http://localhost:8123/2n/door1/api/button/trigger?button=1"

# Check available buttons
curl --digest -u admin:2n "http://localhost:8123/2n/door1/api/button/status"
```

### Test Nested Paths
```bash
# Complex nested path
curl --digest -u admin:2n "http://localhost:8123/building/floor2/entrance/api/relay/ctrl?relay=1&value=on"
```

---

## Migration from v1.0

### What Changed?
1. **Relays only** → **Relays + Buttons**
2. **Simple paths only** → **Nested paths supported**
3. **Slider input** → **Number box input**
4. **Max 8 relays** → **Max 16 relays + 16 buttons**

### Migration Steps
1. Update component files
2. Restart Home Assistant
3. Existing configurations work as-is (backward compatible)
4. To use new features, reconfigure or add new instances

### Backward Compatibility
✅ Existing relay configurations continue working
✅ URL format unchanged
✅ Authentication unchanged
✅ No breaking changes

---

## Troubleshooting

### Buttons Not Showing Up
- Check button_count > 0 in configuration
- Restart Home Assistant
- Check logs for errors

### Nested Path Not Working
- Ensure no consecutive slashes (//)
- Use only: letters, numbers, dash, underscore, forward slash
- Example valid: `2n/door1`, `building/floor2/room3`
- Example invalid: `2n//door1`, `/2n/door1`, `2n/door1/`

### Button Doesn't Trigger Automation
Use `button_pressed` event trigger:
```yaml
trigger:
  - platform: event
    event_type: button_pressed
    event_data:
      entity_id: button.2n_relay_emulator_button_1
```

---

## Best Practices

### Naming Convention for Nested Paths
```
✅ Good:
- building1/entrance
- site-chicago/dock1
- floor_2/room_201

❌ Avoid:
- Building1/ENTRANCE (inconsistent casing)
- site chicago/dock 1 (spaces)
- floor#2/room@201 (special chars)
```

### Relay vs Button Decision Tree
```
Need to maintain state? → Use Relay
Just need momentary trigger? → Use Button
Door needs to stay open? → Use Relay
Door strike (quick unlock)? → Use Button
Not sure? → Use Button (safer/simpler)
```

### Security with Nested Paths
Each instance can have different credentials:
```
Instance 1: /building1/entrance (admin:pass1)
Instance 2: /building2/entrance (admin:pass2)

→ Different 2N devices can have different passwords
→ Compromising one doesn't expose others
```

---

## Performance Notes

- Up to 16 relays + 16 buttons per instance
- Multiple instances supported (different subpaths)
- No performance impact from nested paths
- Buttons are more efficient than relays (no state tracking)

---

## Support

For issues with:
- **Buttons**: Check entity_id in Developer Tools → States
- **Nested paths**: Verify format in logs
- **Number inputs**: Should allow values 0-16

See TROUBLESHOOTING.md for detailed help.
