# Example Configurations for 2N IP Relay Emulator

## 2N Device Configuration Examples

### 2N IP Verso Configuration

1. Go to: **Configuration → Hardware → Switches**
2. Add new switch:
   - **Name**: Home Assistant Relay 1
   - **Type**: HTTP
   - **URL**: `http://192.168.1.100:8123/2n-relay/api/relay/ctrl?relay=1&value=on`
   - **HTTP Method**: GET
   - **Authentication**: Digest
   - **Username**: admin
   - **Password**: 2n

### 2N Indoor Touch Configuration

1. Go to: **Settings → Door opening**
2. Configure HTTP door opening:
   - **Enable HTTP door opening**: Yes
   - **URL**: `http://192.168.1.100:8123/2n-relay/relay/ctrl?relay=1&value=on`
   - **Authentication**: Digest
   - **Username**: admin
   - **Password**: 2n
   - **Timeout**: 5 seconds

### 2N IP Force Configuration

1. Go to: **Hardware → Switches → Switch 1**
2. Configure:
   - **Type**: HTTP
   - **URL on**: `http://192.168.1.100:8123/2n-relay/api/relay/ctrl?relay=1&value=on`
   - **URL off**: `http://192.168.1.100:8123/2n-relay/api/relay/ctrl?relay=1&value=off`
   - **Auth type**: Digest
   - **Username**: admin
   - **Password**: 2n

## URL Examples for Different Scenarios

### Local Network
```
http://192.168.1.100:8123/2n-relay/api/relay/ctrl?relay=1&value=on
```

### Using Hostname
```
http://homeassistant.local:8123/2n-relay/api/relay/ctrl?relay=1&value=on
```

### With SSL/HTTPS
```
https://192.168.1.100:8123/2n-relay/api/relay/ctrl?relay=1&value=on
```

### With Nabu Casa Cloud
```
https://your-instance-id.ui.nabu.casa/2n-relay/api/relay/ctrl?relay=1&value=on
```

### With DuckDNS
```
https://yourdomain.duckdns.org:8123/2n-relay/api/relay/ctrl?relay=1&value=on
```

## Home Assistant Automation Examples

### Example 1: Basic Door Unlock

```yaml
automation:
  - id: 'front_door_unlock_via_2n'
    alias: "Unlock Front Door via 2N"
    trigger:
      - platform: state
        entity_id: switch.2n_relay_emulator_relay_1
        to: "on"
    action:
      - service: lock.unlock
        target:
          entity_id: lock.front_door
      - delay:
          seconds: 5
      - service: lock.lock
        target:
          entity_id: lock.front_door
      - service: switch.turn_off
        target:
          entity_id: switch.2n_relay_emulator_relay_1
```

### Example 2: Multiple Doors

```yaml
automation:
  # Front door - Relay 1
  - id: 'front_door_unlock'
    alias: "Unlock Front Door"
    trigger:
      - platform: state
        entity_id: switch.2n_relay_emulator_relay_1
        to: "on"
    action:
      - service: lock.unlock
        target:
          entity_id: lock.front_door
      - delay: "00:00:05"
      - service: lock.lock
        target:
          entity_id: lock.front_door

  # Garage - Relay 2
  - id: 'garage_door_open'
    alias: "Open Garage Door"
    trigger:
      - platform: state
        entity_id: switch.2n_relay_emulator_relay_2
        to: "on"
    action:
      - service: cover.open_cover
        target:
          entity_id: cover.garage_door
```

### Example 3: With Notifications

```yaml
automation:
  - id: 'door_access_notify'
    alias: "Notify on Door Access"
    trigger:
      - platform: state
        entity_id: switch.2n_relay_emulator_relay_1
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "Front Door"
          message: "Door unlocked via 2N intercom at {{ now().strftime('%H:%M') }}"
      - service: lock.unlock
        target:
          entity_id: lock.front_door
      - delay: "00:00:05"
      - service: lock.lock
        target:
          entity_id: lock.front_door
```

### Example 4: Time-based Access

```yaml
automation:
  - id: 'time_restricted_access'
    alias: "Business Hours Door Access"
    trigger:
      - platform: state
        entity_id: switch.2n_relay_emulator_relay_1
        to: "on"
    condition:
      - condition: time
        after: "07:00:00"
        before: "22:00:00"
    action:
      - service: lock.unlock
        target:
          entity_id: lock.front_door
      - delay: "00:00:05"
      - service: lock.lock
        target:
          entity_id: lock.front_door
    mode: single
```

## Testing Commands

### Basic Testing
```bash
# Turn relay on
curl --digest -u admin:2n "http://localhost:8123/2n-relay/api/relay/ctrl?relay=1&value=on"

# Turn relay off
curl --digest -u admin:2n "http://localhost:8123/2n-relay/api/relay/ctrl?relay=1&value=off"

# Get status
curl --digest -u admin:2n "http://localhost:8123/2n-relay/api/relay/status"

# System info
curl --digest -u admin:2n "http://localhost:8123/2n-relay/api/system/info"
```

### Test with Python
```python
import requests
from requests.auth import HTTPDigestAuth

url = "http://localhost:8123/2n-relay/api/relay/ctrl"
params = {"relay": 1, "value": "on"}
auth = HTTPDigestAuth("admin", "2n")

response = requests.get(url, params=params, auth=auth)
print(response.text)
```

### Test from Different Network
```bash
# Replace with your Home Assistant's external URL
curl --digest -u admin:2n "https://your-id.ui.nabu.casa/2n-relay/api/relay/status"
```

## Dashboard Card Example

```yaml
type: entities
title: 2N Access Control
entities:
  - entity: switch.2n_relay_emulator_relay_1
    name: Front Door
    icon: mdi:door
  - entity: switch.2n_relay_emulator_relay_2
    name: Garage Door
    icon: mdi:garage
```

## Script Example

```yaml
script:
  test_door_unlock:
    alias: "Test Door Unlock"
    sequence:
      - service: switch.turn_on
        target:
          entity_id: switch.2n_relay_emulator_relay_1
      - delay: "00:00:03"
      - service: switch.turn_off
        target:
          entity_id: switch.2n_relay_emulator_relay_1
```
