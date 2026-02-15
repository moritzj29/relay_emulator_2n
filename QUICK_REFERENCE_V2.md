# Quick Reference - v2.0 New Features

## Version Comparison

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Relays (Switches) | ✅ Up to 8 | ✅ Up to 16 |
| Buttons (Momentary) | ❌ | ✅ Up to 16 |
| Nested Subpaths | ❌ | ✅ Yes |
| Number Input Type | Slider | Number Box |
| Max Devices per Instance | 8 | 32 (16+16) |

## Quick Setup Examples

### Example 1: Simple Door with Strike
```yaml
Configuration:
  Subpath: door1
  Relays: 1    # Main door lock
  Buttons: 1   # Door strike (quick entry)
  
URLs:
  Lock:   http://ha:8123/door1/api/relay/ctrl?relay=1&value=on
  Strike: http://ha:8123/door1/api/button/trigger?button=1
```

### Example 2: Multi-Floor Building
```yaml
Instance 1:
  Subpath: building/floor1
  Relays: 2
  Buttons: 2
  URL: http://ha:8123/building/floor1/...

Instance 2:
  Subpath: building/floor2
  Relays: 2
  Buttons: 2
  URL: http://ha:8123/building/floor2/...
```

### Example 3: Multiple Buildings
```yaml
Instance 1:
  Subpath: site-a/entrance
  Relays: 1
  Buttons: 1

Instance 2:
  Subpath: site-b/entrance
  Relays: 1
  Buttons: 1
```

## API Quick Reference

### Relays (Maintain State)
```bash
# On
GET /{subpath}/api/relay/ctrl?relay=N&value=on

# Off
GET /{subpath}/api/relay/ctrl?relay=N&value=off

# Status
GET /{subpath}/api/relay/status
```

### Buttons (Momentary Trigger)
```bash
# Trigger
GET /{subpath}/api/button/trigger?button=N

# Status
GET /{subpath}/api/button/status
```

## When to Use What?

### Use Relays For:
- ✅ Door locks (need continuous power)
- ✅ Garage doors (hold open)
- ✅ Gates (stay open until closed)
- ✅ Anything needing state tracking

### Use Buttons For:
- ✅ Door strikes (momentary unlock)
- ✅ Gate pulse triggers
- ✅ Buzzers/alarms
- ✅ One-time actions
- ✅ 2N "impulse" outputs

## Nested Path Examples

```
Simple:        2n-relay
One Level:     2n/door1
Two Levels:    building/floor2
Three Levels:  site/building/entrance
Complex:       chicago/warehouse/dock1
```

**Rules:**
- Letters, numbers, dash, underscore, forward slash only
- No consecutive slashes (//)
- No leading or trailing slashes

## Testing Commands

```bash
# Relay
curl --digest -u admin:2n \
  "http://localhost:8123/2n/door1/api/relay/ctrl?relay=1&value=on"

# Button
curl --digest -u admin:2n \
  "http://localhost:8123/2n/door1/api/button/trigger?button=1"

# Nested path
curl --digest -u admin:2n \
  "http://localhost:8123/building/floor2/entrance/api/relay/status"
```

## Configuration UI

**Relay Count:**
```
[Number Input Box]  Min: 0  Max: 16  Default: 2
```

**Button Count:**
```
[Number Input Box]  Min: 0  Max: 16  Default: 0
```

**Subpath:**
```
[Text Input]  Examples: "2n-relay", "2n/door1", "building/floor2/entrance"
```

## Entities Created

### For Relays (N relays configured):
```
switch.2n_relay_emulator_relay_1
switch.2n_relay_emulator_relay_2
...
switch.2n_relay_emulator_relay_N
```

### For Buttons (M buttons configured):
```
button.2n_relay_emulator_button_1
button.2n_relay_emulator_button_2
...
button.2n_relay_emulator_button_M
```

## Common Patterns

### Pattern 1: Door with Lock and Strike
```
Relays: 1 (lock - maintains power)
Buttons: 1 (strike - momentary pulse)
```

### Pattern 2: Gate System
```
Relays: 2 (pedestrian gate, vehicle gate)
Buttons: 1 (visitor buzzer)
```

### Pattern 3: Multi-Entry Building
```
Instance per entrance with nested path:
- building/entrance-main
- building/entrance-side
- building/entrance-delivery
```

## Automation Template

### For Button Press:
```yaml
trigger:
  - platform: event
    event_type: button_pressed
    event_data:
      entity_id: button.2n_relay_emulator_button_1
action:
  - service: lock.unlock
    target:
      entity_id: lock.door
```

### For Relay Change:
```yaml
trigger:
  - platform: state
    entity_id: switch.2n_relay_emulator_relay_1
    to: "on"
action:
  - service: cover.open_cover
    target:
      entity_id: cover.gate
```

## Migration Notes

**From v1.0 → v2.0:**
- ✅ Existing configurations work without changes
- ✅ All relay endpoints remain the same
- ✅ Can add buttons by reconfiguring
- ✅ Can change to nested paths by reconfiguring
- ✅ No breaking changes

**New Installs:**
- Start with v2.0
- Choose relay vs button based on need
- Use nested paths for organization
- Number inputs are easier to use than sliders

## Troubleshooting Quick Checks

**Buttons not appearing?**
→ Check button_count > 0 in config

**Nested path not working?**
→ Check for // or leading/trailing /

**Can't enter number?**
→ Type directly, don't use slider

**Button not triggering automation?**
→ Use event trigger, not state trigger

## Security Notes (v2.0 Improvements)

- ✅ Nonce expiry (5 minutes)
- ✅ Replay protection
- ✅ Better password storage (options dict)
- ✅ Cache management (max 1000 nonces)
- ✅ Enhanced logging

See SECURITY.md for details.
