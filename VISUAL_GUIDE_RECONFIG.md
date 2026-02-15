# Quick Visual Guide - Reconfiguration Feature

## How to Reconfigure Your Integration

```
┌─────────────────────────────────────────────────────────────────┐
│  Settings → Devices & Services → 2N IP Relay Emulator          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  ┌──────────────────────────────────────────────────┐           │
│  │  2N Relay Emulator (/2n-relay)                   │           │
│  │  2 entities                                       │  [⋮]  ←── Click here
│  │                                                   │           │
│  │  switch.2n_relay_emulator_relay_1                │           │
│  │  switch.2n_relay_emulator_relay_2                │           │
│  └──────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  • Delete Entry                                                 │
│  • Reload                                                        │
│  • Configure  ←── Click this                                    │
│  • System Options                                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Reconfigure 2N IP Relay Emulator                               │
│                                                                  │
│  Current configuration:                                         │
│  • Subpath: 2n-relay                                            │
│  • Relays: 2                                                    │
│  • Buttons: 0                                                   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ URL Subpath: [2n-relay                              ]     │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Username:    [admin                                 ]     │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Password:    [••••                                  ]     │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Relays:      [  2  ]  ← Number box (type directly)       │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Buttons:     [  0  ]  ← Number box (type directly)       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  [Cancel]                                        [Submit]       │
└─────────────────────────────────────────────────────────────────┘
```

## Common Changes - Quick Reference

### 1️⃣ Change Password
```
┌─────────────────────────────┐
│ Password: [MyNewP@ss123]    │ ← Type new password
└─────────────────────────────┘
                ↓
         [Submit] ← Click
                ↓
   Update 2N device with new password
```

### 2️⃣ Add More Relays
```
┌─────────────────────────────┐
│ Relays: [2] → [4]           │ ← Change from 2 to 4
└─────────────────────────────┘
                ↓
         [Submit] ← Click
                ↓
   New entities appear automatically:
   • switch.2n_relay_emulator_relay_3  ← NEW
   • switch.2n_relay_emulator_relay_4  ← NEW
```

### 3️⃣ Add Buttons
```
┌─────────────────────────────┐
│ Buttons: [0] → [2]          │ ← Change from 0 to 2
└─────────────────────────────┘
                ↓
         [Submit] ← Click
                ↓
   New entities appear:
   • button.2n_relay_emulator_button_1  ← NEW
   • button.2n_relay_emulator_button_2  ← NEW
```

### 4️⃣ Change Subpath
```
┌────────────────────────────────────┐
│ Subpath: [2n-relay]                │
│           ↓                         │
│          [building/floor1/door1]   │ ← New nested path
└────────────────────────────────────┘
                ↓
         [Submit] ← Click
                ↓
   ⚠️ IMPORTANT: Update ALL 2N device URLs!
   
   Old: http://ha:8123/2n-relay/api/relay/ctrl?relay=1&value=on
   New: http://ha:8123/building/floor1/door1/api/relay/ctrl?relay=1&value=on
```

---

## What Changes Automatically

```
┌─────────────────────────────────────────────────────────────┐
│  When you click [Submit]:                                   │
│                                                              │
│  ✓ Integration reloads (takes 2-5 seconds)                  │
│  ✓ New entities created                                     │
│  ✓ Old entities removed (if count decreased)                │
│  ✓ HTTP endpoints updated                                   │
│  ✓ Device info updated                                      │
│  ✓ Configuration saved                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## What You Need to Do Manually

```
┌─────────────────────────────────────────────────────────────┐
│  After reconfiguration:                                      │
│                                                              │
│  □ Update 2N device credentials (if changed)                │
│  □ Update 2N device URLs (if subpath changed)               │
│  □ Update automations (if entity count changed)             │
│  □ Test connectivity                                         │
│  □ Verify automations still work                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Example Workflows

### Workflow 1: Monthly Password Rotation
```
Step 1: Configure → Change Password
        ┌──────────────────────────┐
        │ Password: [NewPass_Feb]  │
        └──────────────────────────┘
        
Step 2: Submit
        [Submit] ← Click
        
Step 3: Update 2N Devices
        For each 2N device:
        • Open web interface
        • Settings → HTTP
        • Update password field
        • Save
        
Step 4: Test
        curl --digest -u admin:NewPass_Feb \
          "http://ha:8123/2n-relay/api/relay/status"
```

### Workflow 2: Adding a New Door
```
Current: 2 relays (front + back door)
Goal:    3 relays (add side door)

Step 1: Configure → Change Relay Count
        ┌──────────────────────────┐
        │ Relays: [2] → [3]        │
        └──────────────────────────┘
        
Step 2: Submit
        [Submit] ← Click
        
Step 3: Verify New Entity
        Developer Tools → States
        Look for: switch.2n_relay_emulator_relay_3
        
Step 4: Configure 2N Device for Side Door
        URL: http://ha:8123/2n-relay/api/relay/ctrl?relay=3&value=on
        
Step 5: Create Automation
        trigger:
          platform: state
          entity_id: switch.2n_relay_emulator_relay_3
        action:
          service: lock.unlock
          entity_id: lock.side_door
```

### Workflow 3: Converting to Nested Paths
```
Current: door1, door2, door3 (three separate instances)
Goal:    building/floor1, building/floor2 (organized)

For each instance:

Step 1: Configure → Change Subpath
        ┌───────────────────────────────────┐
        │ Subpath: [door1]                  │
        │           ↓                        │
        │          [building/floor1]        │
        └───────────────────────────────────┘
        
Step 2: Submit
        
Step 3: Update 2N Device
        Old URL: http://ha:8123/door1/...
        New URL: http://ha:8123/building/floor1/...
        
Step 4: Test
        
Step 5: Repeat for other instances
```

---

## Troubleshooting Quick Checks

```
┌─────────────────────────────────────────────────────────────┐
│  Problem: Can't see Configure option                        │
│  Solution: Reload page, or restart HA                       │
├─────────────────────────────────────────────────────────────┤
│  Problem: Changes not applying                              │
│  Solution: Check logs, try reloading integration manually   │
├─────────────────────────────────────────────────────────────┤
│  Problem: 2N device can't connect                           │
│  Solution: Verify you updated credentials AND URL           │
├─────────────────────────────────────────────────────────────┤
│  Problem: Entities disappeared                              │
│  Solution: You decreased count - increase it back           │
├─────────────────────────────────────────────────────────────┤
│  Problem: Subpath already in use                            │
│  Solution: Choose different subpath or remove other instance│
└─────────────────────────────────────────────────────────────┘
```

---

## Visual Comparison

### Before Reconfiguration Support (v2.0)
```
Want to change something?
    ↓
Delete integration
    ↓
Lose all entities
    ↓
Lose all automations
    ↓
Recreate integration
    ↓
Recreate automations
    ↓
Reconfigure 2N devices
```

### With Reconfiguration Support (v2.1)
```
Want to change something?
    ↓
Click Configure
    ↓
Make changes
    ↓
Click Submit
    ↓
Update 2N devices (if needed)
    ↓
Done! ✓
```

---

## Entity Count Changes - Visual

### Increasing Count (2 → 4 relays)
```
Before:
┌───────────────────────────────┐
│ switch.relay_1  ✓ exists      │
│ switch.relay_2  ✓ exists      │
└───────────────────────────────┘

After:
┌───────────────────────────────┐
│ switch.relay_1  ✓ kept        │
│ switch.relay_2  ✓ kept        │
│ switch.relay_3  ★ NEW         │
│ switch.relay_4  ★ NEW         │
└───────────────────────────────┘
```

### Decreasing Count (4 → 2 relays)
```
Before:
┌───────────────────────────────┐
│ switch.relay_1  ✓ exists      │
│ switch.relay_2  ✓ exists      │
│ switch.relay_3  ✓ exists      │
│ switch.relay_4  ✓ exists      │
└───────────────────────────────┘

After:
┌───────────────────────────────┐
│ switch.relay_1  ✓ kept        │
│ switch.relay_2  ✓ kept        │
│ switch.relay_3  ✗ REMOVED     │
│ switch.relay_4  ✗ REMOVED     │
└───────────────────────────────┘

⚠️ Check automations for broken references!
```

---

## Quick Reference Card

```
╔═══════════════════════════════════════════════════════════════╗
║  RECONFIGURATION QUICK REFERENCE                              ║
╠═══════════════════════════════════════════════════════════════╣
║  Access:    Settings → Devices → ⋮ → Configure               ║
║  Changes:   • Subpath  • Username  • Password                 ║
║             • Relay count  • Button count                     ║
║  Result:    Integration reloads automatically                 ║
║  Warning:   Update 2N devices after subpath/credential change ║
╚═══════════════════════════════════════════════════════════════╝
```
