# Version 2.1.1 - Bugfix Release

## Critical Bug Fixes

### Issue 1: Config Flow Error (500 Internal Server Error)
**Problem:** Integration configuration failed with "500 Internal Server Error"

**Cause:** 
- Used `selector.NumberSelector` which is not available in all Home Assistant versions
- Incompatible selector API

**Fix:**
- Replaced with standard `vol.All(vol.Coerce(int), vol.Range(min=0, max=16))`
- Now works with all Home Assistant versions

**Impact:** Integration can now be configured and reconfigured properly

### Issue 2: No Entities Created When Count is 0
**Problem:** If relay_count or button_count is 0, entity creation might fail

**Cause:**
- Missing check for 0 count in switch.py

**Fix:**
- Added proper handling: `if relay_count > 0:` before creating entities
- Both switch.py and button.py now handle 0 counts gracefully

**Impact:** Can now configure instances with 0 relays or 0 buttons

---

## Changes in v2.1.1

### Fixed
- ✅ Config flow no longer crashes (removed selector dependency)
- ✅ Options flow (reconfiguration) works correctly
- ✅ Entities created properly even with 0 count
- ✅ Number inputs now use standard sliders (compatible with all HA versions)

### Not Changed
- Configuration structure (still supports all v2.1.0 features)
- Entity naming and behavior
- HTTP endpoints
- Authentication

---

## Upgrade Instructions

### From v2.1.0 to v2.1.1

**If you have a working installation:**
1. Replace files in `/config/custom_components/2n_relay_emulator/`
2. Restart Home Assistant
3. Test reconfiguration (Settings → Devices → Configure)

**If you had v2.1.0 but couldn't configure:**
1. Delete non-working integration instance (if any)
2. Install v2.1.1 files
3. Restart Home Assistant  
4. Add integration fresh
5. Configure normally

**If upgrading from v2.0.0 or earlier:**
- Follow normal upgrade process
- v2.1.1 includes all v2.1.0 features plus bug fixes

---

## Testing the Fix

### Test 1: Initial Configuration
```
Settings → Devices & Services → Add Integration
→ Search "2N IP Relay Emulator"
→ Should load configuration form successfully
→ Fill in details and submit
→ Should create integration and entities
```

### Test 2: Reconfiguration
```
Settings → Devices & Services → 2N IP Relay Emulator
→ Click ⋮ (three dots)
→ Select "Configure"
→ Should load form with current values
→ Make changes
→ Submit
→ Should apply changes successfully
```

### Test 3: Zero Counts
```
Configure with:
- Relays: 0
- Buttons: 0
→ Should work without errors
→ No entities created (expected)
→ Device shows in Devices list
→ HTTP endpoints still accessible
```

### Test 4: Number Input
```
In configuration form:
- Relay count field should accept typed numbers
- Button count field should accept typed numbers
- May show as slider or text input (depends on HA version)
- Both should work correctly
```

---

## Known Limitations

### Number Input Display
**Issue:** Input fields may display as:
- Sliders (older HA versions)
- Number boxes (newer HA versions)

**Why:** We use compatible `vol.Range()` which HA renders differently per version

**Impact:** None - both work correctly, just look different

**Workaround:** None needed - this is expected behavior

---

## Troubleshooting

### Still Getting 500 Error?

1. **Clear Browser Cache:**
   ```
   Ctrl+Shift+R (Windows/Linux)
   Cmd+Shift+R (Mac)
   ```

2. **Check Logs:**
   ```
   Settings → System → Logs
   Look for: custom_components.2n_relay_emulator
   ```

3. **Verify Files:**
   ```bash
   ls -la /config/custom_components/2n_relay_emulator/
   # Should show: __init__.py, config_flow.py, const.py, etc.
   ```

4. **Full Restart:**
   ```
   Settings → System → Restart Home Assistant
   Wait 30 seconds
   Try configuration again
   ```

### Integration Not Loading?

1. **Check manifest.json:**
   ```bash
   cat /config/custom_components/2n_relay_emulator/manifest.json
   # Should show version "2.1.1"
   ```

2. **Check for Python errors:**
   ```
   Settings → System → Logs
   Filter by: custom_components.2n_relay_emulator
   ```

3. **Verify imports:**
   - All files present?
   - No syntax errors?

### Entities Not Appearing?

1. **Check relay/button counts > 0**
2. **Check Developer Tools → States:**
   ```
   Look for: switch.2n_relay_*
   Look for: button.2n_relay_*
   ```
3. **Check integration loaded:**
   ```
   Settings → Devices & Services
   Find: 2N IP Relay Emulator
   Status: should not show errors
   ```

---

## Reporting Issues

If you still have problems:

1. **Enable Debug Logging:**
   ```yaml
   # configuration.yaml
   logger:
     default: info
     logs:
       custom_components.2n_relay_emulator: debug
   ```

2. **Reproduce the Issue**
3. **Collect Information:**
   - Home Assistant version
   - Error message (exact text)
   - Logs (from Settings → System → Logs)
   - Steps to reproduce

4. **Report:**
   - Include all information above
   - Sanitize any sensitive data (passwords, IPs)

---

## Version History

### v2.1.1 (Current) - Bugfix Release
- Fixed config flow 500 error
- Fixed entity creation with 0 counts
- Compatible number input across HA versions

### v2.1.0 - Reconfiguration Support
- Full reconfiguration capability
- Options flow implementation
- Tried to use selectors (caused issues)

### v2.0.0 - Major Features
- Button support
- Nested paths
- Security improvements

### v1.0.0 - Initial Release
- Basic relay support

---

## Migration Notes

### From v2.1.0 to v2.1.1
✅ **Drop-in replacement** - no migration needed
- Same configuration structure
- Same entity names
- Same HTTP endpoints
- Just fixes bugs

### From v2.0.0 or earlier
✅ **Compatible upgrade**
- New features available (reconfiguration)
- Existing setups continue working
- Can use new features optionally

---

## Summary

**What this release fixes:**
- Configuration form now loads correctly
- Reconfiguration works properly
- Zero-count configurations work
- Compatible with all Home Assistant versions

**What to do:**
1. Install v2.1.1
2. Restart Home Assistant
3. Test configuration
4. Enjoy working reconfiguration!
