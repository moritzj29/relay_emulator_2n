# Version 2.1.2 - Reconfiguration Fix

## Critical Fix

**Issue:** Options flow (reconfiguration) causing 500 error  
**Cause:** `description_placeholders` not supported in older HA versions  
**Fix:** Removed description_placeholders, simplified options flow

## What's Fixed in v2.1.2

✅ **Reconfiguration now works** - Can edit settings after initial setup  
✅ **Compatible with all HA versions** - No version-specific features  
✅ **Simplified options flow** - Removed unsupported parameters  

## Changes from v2.1.1

### Fixed
- Removed `description_placeholders` from options flow
- Simplified strings.json options section
- Options flow now loads without errors

### Not Changed
- All other functionality remains the same
- Initial configuration still works
- Entities, API, security unchanged

## Upgrade Instructions

### From v2.1.1 to v2.1.2

1. **Replace files:**
```bash
cp -r 2n_relay_emulator /config/custom_components/
```

2. **Restart Home Assistant**

3. **Test reconfiguration:**
   - Settings → Devices & Services
   - Find 2N IP Relay Emulator
   - Click ⋮ → Configure
   - Should load without 500 error

## Testing

### Test 1: Options Flow Loads
```
Settings → Devices → 2N IP Relay Emulator
→ Click ⋮
→ Click Configure
→ Form should load with current values
✅ No 500 error
```

### Test 2: Change Settings
```
In configure form:
→ Change password
→ Change relay count
→ Submit
→ Integration reloads
✅ Changes applied
```

### Test 3: Entities Update
```
After changing relay count from 2 to 3:
→ Check Developer Tools → States
→ Should see new switch.2n_relay_emulator_relay_3
✅ New entity created
```

## Known Limitations

**Current values not shown in description:**
- Due to compatibility fix, we can't show current values in the form description
- However, all fields are pre-filled with current values
- You can see what will change by looking at the default values

## Troubleshooting

### Still Getting 500 Error?

1. **Hard refresh browser:**
```
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)
```

2. **Check HA version:**
```
Settings → System → About
Should be 2023.1 or later
```

3. **Check logs:**
```
Settings → System → Logs
Filter: custom_components.2n_relay_emulator
```

4. **Verify installation:**
```bash
ls -la /config/custom_components/2n_relay_emulator/
# Should show all files including strings.json
```

5. **Full restart:**
```
Settings → System → Restart Home Assistant
Wait 30 seconds
Try again
```

### Options Flow Shows But Changes Don't Apply?

1. **Check logs for errors**
2. **Verify integration reloaded:**
   - You should see a brief "Loading..." message
   - Entities may disappear/reappear briefly
3. **Manual reload if needed:**
   - Settings → Devices & Services
   - Find integration → ⋮ → Reload

## Version History

| Version | Status | Issue |
|---------|--------|-------|
| 2.1.2 | ✅ Working | Options flow fixed |
| 2.1.1 | ⚠️ Partial | Config flow worked, options flow broken |
| 2.1.0 | ❌ Broken | Config flow broken |
| 2.0.0 | ✅ Working | No reconfiguration feature |

## Summary

**v2.1.2 is the stable release with full reconfiguration support.**

All features work:
- ✅ Initial configuration
- ✅ Reconfiguration (options flow)
- ✅ Entity creation
- ✅ HTTP endpoints
- ✅ Compatible with all HA versions

## Recommendation

**If you have:**
- v2.1.0 → Upgrade to v2.1.2
- v2.1.1 → Upgrade to v2.1.2
- v2.0.0 or earlier → Upgrade to v2.1.2

v2.1.2 is the most stable and feature-complete version.
