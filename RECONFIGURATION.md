# Reconfiguration Guide - 2N IP Relay Emulator

## Overview

The 2N IP Relay Emulator now supports full reconfiguration after initial setup. You can modify all settings without needing to delete and recreate the integration.

## What Can Be Reconfigured?

✅ **URL Subpath** - Change the endpoint path
✅ **Username** - Update digest auth username
✅ **Password** - Update digest auth password
✅ **Relay Count** - Add or remove relays (0-16)
✅ **Button Count** - Add or remove buttons (0-16)

## How to Reconfigure

### Step 1: Access Configuration
1. Go to **Settings** → **Devices & Services**
2. Find your **2N IP Relay Emulator** instance
3. Click the **⋮** (three dots) menu
4. Select **Configure**

### Step 2: Update Settings
The configuration dialog shows:
- Current values pre-filled
- Current configuration summary
- All fields editable

### Step 3: Save Changes
1. Modify any fields you want to change
2. Click **Submit**
3. Integration reloads automatically
4. New entities created / old entities removed as needed

## What Happens During Reconfiguration?

### Automatic Actions:
- ✅ Integration reloads immediately
- ✅ HTTP endpoints updated
- ✅ New entities created
- ✅ Removed entities cleaned up
- ✅ Device info updated
- ✅ Automations remain intact (if entity IDs unchanged)

### Manual Actions Required:
- ⚠️ Update 2N device URLs (if subpath changed)
- ⚠️ Update automations (if entity count changed)
- ⚠️ Test connectivity after changes

---

## Common Reconfiguration Scenarios

### Scenario 1: Change Credentials

**Why:** Security rotation, suspected compromise, or standardization

**Steps:**
1. Open **Configure**
2. Update **Username** and/or **Password**
3. Click **Submit**
4. Update 2N device with new credentials
5. Test authentication

**Impact:**
- ✅ No entity changes
- ✅ No URL changes
- ⚠️ Must update 2N device credentials immediately

**Example:**
```yaml
Before:
  Username: admin
  Password: 2n

After:
  Username: access_control_user
  Password: MyStr0ng!Pass#2024
```

### Scenario 2: Add More Relays/Buttons

**Why:** Expanding system, adding new doors/gates

**Steps:**
1. Open **Configure**
2. Increase **Relay Count** or **Button Count**
3. Click **Submit**
4. New entities appear automatically
5. Configure 2N devices for new relays/buttons

**Impact:**
- ✅ New entities created
- ✅ Old entities unchanged
- ✅ Existing automations unaffected

**Example:**
```yaml
Before:
  Relays: 2
  Buttons: 1
  
Entities:
  - switch.2n_relay_emulator_relay_1
  - switch.2n_relay_emulator_relay_2
  - button.2n_relay_emulator_button_1

After:
  Relays: 4
  Buttons: 3
  
Entities:
  - switch.2n_relay_emulator_relay_1  ← Unchanged
  - switch.2n_relay_emulator_relay_2  ← Unchanged
  - switch.2n_relay_emulator_relay_3  ← NEW
  - switch.2n_relay_emulator_relay_4  ← NEW
  - button.2n_relay_emulator_button_1  ← Unchanged
  - button.2n_relay_emulator_button_2  ← NEW
  - button.2n_relay_emulator_button_3  ← NEW
```

### Scenario 3: Remove Unused Relays/Buttons

**Why:** Simplification, decommissioned doors

**Steps:**
1. Open **Configure**
2. Decrease **Relay Count** or **Button Count**
3. Click **Submit**
4. Removed entities disappear
5. Update automations if they referenced removed entities

**Impact:**
- ⚠️ Entities removed (from highest number down)
- ⚠️ Automations may break if they used removed entities
- ✅ Lower-numbered entities unaffected

**Example:**
```yaml
Before:
  Relays: 4
  Buttons: 3

After:
  Relays: 2
  Buttons: 1

Removed:
  - switch.2n_relay_emulator_relay_3  ← Deleted
  - switch.2n_relay_emulator_relay_4  ← Deleted
  - button.2n_relay_emulator_button_2  ← Deleted
  - button.2n_relay_emulator_button_3  ← Deleted
  
Kept:
  - switch.2n_relay_emulator_relay_1  ← Kept
  - switch.2n_relay_emulator_relay_2  ← Kept
  - button.2n_relay_emulator_button_1  ← Kept
```

**⚠️ Warning:** Check automations for broken entity references!

### Scenario 4: Change Subpath

**Why:** Reorganization, better naming, nested path adoption

**Steps:**
1. Open **Configure**
2. Update **Subpath** (e.g., `door1` → `building/floor1/door1`)
3. Click **Submit**
4. **IMPORTANT:** Update ALL 2N device URLs
5. Test new URLs

**Impact:**
- ✅ No entity changes
- ⚠️ All 2N device URLs must be updated
- ⚠️ Old URLs stop working immediately

**Example:**
```yaml
Before:
  Subpath: door1
  URL: http://ha:8123/door1/api/relay/ctrl?relay=1&value=on

After:
  Subpath: building/floor1/door1
  URL: http://ha:8123/building/floor1/door1/api/relay/ctrl?relay=1&value=on
```

**⚠️ Critical:** Update 2N devices before testing!

### Scenario 5: Convert Relays to Buttons (or vice versa)

**Why:** Better suited for use case (strike vs lock)

**Steps:**
1. Open **Configure**
2. Decrease one count, increase the other
3. Click **Submit**
4. Update automations to use new entity types
5. Update 2N device URLs (relay vs button endpoint)

**Impact:**
- ⚠️ Old entity type removed
- ⚠️ New entity type added
- ⚠️ Automations need updating
- ⚠️ 2N device URLs need updating

**Example:**
```yaml
Before:
  Relays: 2 (using relay for door strike - wrong!)
  Buttons: 0
  
After:
  Relays: 1 (main lock only)
  Buttons: 1 (door strike - correct!)

2N Device URL Changes:
  Old: http://ha:8123/door1/api/relay/ctrl?relay=2&value=on
  New: http://ha:8123/door1/api/button/trigger?button=1
```

---

## Best Practices

### ✅ Before Reconfiguring:

1. **Document Current Setup**
   - Screenshot current configuration
   - List all entity IDs used in automations
   - Note 2N device URLs

2. **Plan Changes**
   - Decide what to change
   - Check impact on automations
   - Prepare updated 2N device configs

3. **Backup**
   - Create Home Assistant backup
   - Export automations using affected entities

### ✅ During Reconfiguration:

1. **One Change at a Time** (if possible)
   - Credentials → Test → Continue
   - Counts → Test → Continue
   - Subpath → Update 2N → Test

2. **Test Immediately**
   - Verify entities appear/disappear
   - Test 2N device connectivity
   - Check automations still work

### ✅ After Reconfiguration:

1. **Update 2N Devices**
   - New credentials → Update immediately
   - New subpath → Update all URLs
   - New relays/buttons → Add new actions

2. **Verify Automations**
   - Check Developer Tools → Automations
   - Look for "unavailable" entities
   - Test triggers manually

3. **Document Changes**
   - Update documentation
   - Note new entity IDs
   - Record new URLs

---

## Troubleshooting

### Issue: "Subpath already in use"

**Cause:** Another instance uses that subpath

**Solution:**
- Choose a different subpath
- Or remove the other instance first

### Issue: Entities Not Updating

**Cause:** Integration didn't reload

**Solution:**
1. Go to **Settings** → **System** → **Restart Home Assistant**
2. Or reload integration manually:
   - Settings → Devices & Services
   - Find integration → ⋮ → **Reload**

### Issue: Automations Broken

**Cause:** Entity IDs changed (count decreased)

**Solution:**
1. **Developer Tools** → **States**
2. Find new entity IDs
3. Update automations
4. Re-test

### Issue: 2N Device Can't Connect

**Cause:** URL or credentials changed

**Solution:**
1. Verify new subpath in HA
2. Update 2N device configuration:
   - URL: New subpath
   - Username: New username
   - Password: New password
3. Test with curl first:
```bash
curl --digest -u NEW_USER:NEW_PASS \
  "http://ha:8123/NEW_SUBPATH/api/relay/status"
```

### Issue: Old Entities Still Showing

**Cause:** Entity registry cache

**Solution:**
1. **Settings** → **Devices & Services**
2. Find device → Click device name
3. Select old entities → **Delete**
4. Or use **Developer Tools** → **States** to remove

---

## Advanced: Bulk Reconfiguration

If you need to reconfigure multiple instances:

### Method 1: UI (Recommended)
1. Configure each instance individually
2. Use checklist to track progress
3. Test each after reconfiguration

### Method 2: Config File (Advanced)
1. Stop Home Assistant
2. Edit `.storage/core.config_entries`
3. Find entry by `entry_id`
4. Modify `data` and `options`
5. Restart Home Assistant

**⚠️ Warning:** Direct file editing risky - backup first!

---

## Migration Scenarios

### From v1.0 to v2.0 with Reconfiguration

**Scenario:** Already have v1.0 installed with port-based setup

**Steps:**
1. Install v2.0 (overwrites v1.0 files)
2. **Don't delete old config**
3. It migrates automatically to subpath-based
4. Reconfigure if needed (change from port to subpath)

**Note:** v1.0 → v2.0 has breaking changes in how it's configured initially, but existing instances should work.

---

## Examples

### Example 1: Security Rotation

**Monthly credential rotation:**

```bash
Month 1: admin / pass_jan2024
Month 2: admin / pass_feb2024
Month 3: admin / pass_mar2024

Process:
1. Configure → Change password
2. Submit
3. Update all 2N devices
4. Test connectivity
5. Document new password
```

### Example 2: Expanding System

**Adding new door:**

```yaml
Week 1: 2 relays, 2 buttons (front + back door)
Week 2: Add side door
  → Reconfigure: 3 relays, 3 buttons
  → New entities appear
  → Configure 2N device for relay 3, button 3

Week 3: Add garage
  → Reconfigure: 4 relays, 3 buttons
  → New relay 4 appears
  → Configure 2N device for relay 4
```

### Example 3: Reorganization

**Moving to nested paths:**

```yaml
Current setup:
  - Instance 1: door1
  - Instance 2: door2
  - Instance 3: door3

New structure:
  - Instance 1: building-a/entrance
  - Instance 2: building-a/side
  - Instance 3: building-b/main

Process per instance:
1. Configure → Change subpath
2. Update 2N device URL
3. Test
4. Move to next instance
```

---

## FAQ

**Q: Will reconfiguring break my automations?**
A: Only if you remove entities that automations reference. Adding entities is safe.

**Q: Can I change everything at once?**
A: Yes, but test each change if possible. Changing credentials + subpath + counts can be complex to troubleshoot.

**Q: What if I make a mistake?**
A: Reconfigure again to fix it. Or restore from backup.

**Q: Do I need to restart HA?**
A: No - integration reloads automatically. Only restart if something doesn't work.

**Q: Can I undo changes?**
A: Yes - just reconfigure back to previous values. Or restore from backup.

**Q: Will this affect other integrations?**
A: No - only this integration reloads.

---

## Summary

✅ Full reconfiguration support
✅ All settings editable
✅ Automatic entity management
✅ No need to delete/recreate
✅ Safe and reversible

**Remember:** 
- Update 2N devices after subpath/credential changes
- Check automations after entity count changes
- Test after reconfiguration
- Keep backups before major changes
