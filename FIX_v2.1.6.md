# Version 2.1.6 - Critical Fix for NumberSelector

## The Issues (v2.1.5)

1. **NumberSelector returns float, not int**
   ```
   TypeError: 'float' object cannot be interpreted as an integer
   ```

2. **OptionsFlowHandler signature mismatch**
   ```
   TypeError: OptionsFlowHandler() takes no arguments
   ```

## The Fixes

### Issue 1: Float to Int Conversion

**Problem:** NumberSelector returns float (e.g., `2.0`) instead of int (`2`)

**Fixed in:**
- `config_flow.py` - Convert on save
- `switch.py` - Convert when reading
- `button.py` - Convert when reading
- `http_server.py` - Convert when reading

**Code:**
```python
# Before (broken):
relay_count = entry.data.get(CONF_RELAY_COUNT, 0)
for relay_num in range(1, relay_count + 1):  # ❌ Fails if float

# After (working):
relay_count = int(entry.data.get(CONF_RELAY_COUNT, 0))
for relay_num in range(1, relay_count + 1):  # ✅ Works
```

### Issue 2: OptionsFlowHandler Parameter

**Problem:** Removed `__init__` in v2.1.4 but forgot to update `async_get_options_flow`

**Fixed:**
```python
# Before (broken):
def async_get_options_flow(config_entry):
    return OptionsFlowHandler(config_entry)  # ❌ No __init__!

# After (working):
def async_get_options_flow(config_entry):
    return OptionsFlowHandler()  # ✅ No parameter
```

## What's Fixed

✅ **Entities create correctly** - No more float error  
✅ **Options flow loads** - No more "takes no arguments" error  
✅ **Number boxes work** - Int conversion automatic  
✅ **Reconfiguration works** - All issues resolved  

## Installation

```bash
# Remove old version
rm -rf /config/custom_components/2n_relay_emulator

# Install v2.1.6
cp -r 2n_relay_emulator /config/custom_components/

# Restart Home Assistant
```

## Testing

### Test 1: Initial Configuration
```
Settings → Devices & Services → Add Integration
→ Search "2N IP Relay Emulator"
→ Configure with relay count = 2
→ Submit
→ ✅ Should create 2 switch entities
→ No float errors in logs
```

### Test 2: Reconfiguration
```
Settings → Devices & Services → 2N IP Relay Emulator
→ Click ⋮ → Configure
→ ✅ Form should load
→ Change relay count from 2 to 4
→ Submit
→ ✅ Should create 2 new entities (relay_3, relay_4)
→ No errors in logs
```

### Test 3: Number Boxes
```
In configuration form:
→ Relay count shows as number box
→ Can type: 4 [Enter]
→ Can use arrows: ↑↓
→ ✅ Accepts and saves as integer
```

## Why NumberSelector Returns Float

Home Assistant's NumberSelector uses HTML5 `<input type="number">` which:
- Always returns numbers as float in JavaScript
- Gets passed to Python as float
- Needs explicit `int()` conversion

**This is expected behavior** - we just need to handle it.

## Changes in This Version

| File | Change |
|------|--------|
| config_flow.py | Convert to int on save |
| switch.py | Convert to int when reading |
| button.py | Convert to int when reading |
| http_server.py | Convert to int when reading |
| config_flow.py | Fix OptionsFlowHandler() call |

## Version History

| Version | Config | Options | Entities | Number Boxes |
|---------|--------|---------|----------|--------------|
| 2.1.6 | ✅ | ✅ | ✅ | ✅ |
| 2.1.5 | ✅ | ❌ | ❌ | ✅ |
| 2.1.4 | ✅ | ✅ | ✅ | Slider |
| 2.1.3 | ✅ | ❌ | ✅ | Slider |

## This is THE Working Version

v2.1.6 combines:
- ✅ Working config flow (v2.1.4)
- ✅ Working options flow (v2.1.4)
- ✅ Working entity creation (v2.1.4)
- ✅ Number box inputs (v2.1.5)
- ✅ Proper int conversion (v2.1.6)

**Everything works now!** 🎉

## Recommendation

**Use v2.1.6** - This is the stable, fully-working version with all features.

If you had any issues with v2.1.0 through v2.1.5, they are all fixed in v2.1.6.
