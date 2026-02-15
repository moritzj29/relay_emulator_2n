# Version 2.1.5 - Number Box Inputs 🎨

## What's New

✨ **Number box inputs are back!** - Type numbers directly instead of using sliders

Now that the core options flow is working (fixed in v2.1.4), we can safely add the nicer number selector UI.

## Changes from v2.1.4

### Added
- ✅ Number box selectors for relay count
- ✅ Number box selectors for button count
- ✅ Direct number input (type the number)
- ✅ Min/Max validation (0-16)

### UI Improvement

**Before (v2.1.4) - Slider:**
```
Relays: [━━●━━━━━━━━━━━━━] (hard to set exact numbers)
```

**After (v2.1.5) - Number Box:**
```
Relays: [ 4 ] ↑↓  (type the number directly)
```

### Still Stable
- ✅ Options flow works correctly
- ✅ Reconfiguration functional
- ✅ All features from v2.1.4 preserved

## Compatibility

**This feature requires:**
- Home Assistant 2023.8 or later (for NumberSelector with BOX mode)

**If you have older HA:**
- Use v2.1.4 instead (still has sliders, but works)
- Or upgrade Home Assistant

## Installation

```bash
# Remove old version
rm -rf /config/custom_components/2n_relay_emulator

# Install v2.1.5
cp -r 2n_relay_emulator /config/custom_components/

# Restart Home Assistant
```

## What You'll See

### Initial Configuration
```
┌────────────────────────────────────────┐
│ 2N IP Relay Emulator Setup            │
├────────────────────────────────────────┤
│ URL Subpath: [2n-relay          ]     │
│ Username:    [admin              ]     │
│ Password:    [••••               ]     │
│ Relays:      [  2  ] ↑↓               │ ← Number box!
│ Buttons:     [  0  ] ↑↓               │ ← Number box!
│                                        │
│ [Cancel]               [Submit]        │
└────────────────────────────────────────┘
```

### Reconfiguration
```
┌────────────────────────────────────────┐
│ Reconfigure 2N IP Relay Emulator       │
├────────────────────────────────────────┤
│ URL Subpath: [2n-relay          ]     │
│ Username:    [admin              ]     │
│ Password:    [••••               ]     │
│ Relays:      [  2  ] ↑↓               │ ← Type new number
│ Buttons:     [  1  ] ↑↓               │ ← Or use arrows
│                                        │
│ [Cancel]               [Submit]        │
└────────────────────────────────────────┘
```

## Usage

**Three ways to input numbers:**
1. **Type directly:** Click in box, type `4`, press Enter
2. **Use arrows:** Click ↑ to increment, ↓ to decrement
3. **Use keyboard:** Arrow keys work too

**Validation:**
- Minimum: 0
- Maximum: 16
- Must be integer
- Invalid input rejected

## Benefits Over Sliders

✅ **Faster** - Type `16` instantly vs dragging slider  
✅ **Precise** - Exact number, no guessing  
✅ **Keyboard-friendly** - Tab, type, enter  
✅ **Better UX** - Industry standard for numeric input  
✅ **Accessible** - Screen readers work better  

## Troubleshooting

### Number Boxes Don't Appear?

**Check Home Assistant version:**
```
Settings → System → About
Version: Must be 2023.8 or later
```

**If older:**
- Upgrade HA to 2023.8+
- Or use v2.1.4 (has sliders, still works)

### Still Shows Sliders?

1. **Clear browser cache:**
   ```
   Ctrl+Shift+R (Windows/Linux)
   Cmd+Shift+R (Mac)
   ```

2. **Force refresh:**
   - Close browser tab
   - Clear cache
   - Reopen HA

3. **Check console for errors:**
   - F12 → Console
   - Look for JavaScript errors

### Can't Type Numbers?

1. **Click inside the box** (not just the label)
2. **Try arrow buttons** if typing doesn't work
3. **Use keyboard arrows** after clicking box

## Version Comparison

| Version | Config Flow | Options Flow | Input Type |
|---------|-------------|--------------|------------|
| 2.1.5 | ✅ | ✅ | Number Box |
| 2.1.4 | ✅ | ✅ | Slider |
| 2.1.3 | ✅ | ❌ | Slider |
| 2.1.2 | ✅ | ❌ | Slider |
| 2.1.1 | ✅ | ❌ | Slider |
| 2.1.0 | ❌ | ❌ | Number Box |

## Migration Path

**From v2.1.4 to v2.1.5:**
- ✅ Drop-in replacement
- ✅ No configuration changes needed
- ✅ Just better UI

**From earlier versions:**
- Upgrade to v2.1.5 directly
- All fixes included

## Technical Details

### Implementation

```python
# Number selector configuration
selector.NumberSelector(
    selector.NumberSelectorConfig(
        min=0,           # Minimum value
        max=16,          # Maximum value
        mode=selector.NumberSelectorMode.BOX,  # Box mode (not slider)
    )
)
```

### Fallback Behavior

If NumberSelector fails for any reason, Home Assistant will:
1. Fall back to text input (you can still type)
2. Validation still works (0-16 range)
3. Integration remains functional

## Recommendation

**Use v2.1.5 if:**
- ✅ Home Assistant 2023.8 or later
- ✅ You want better UX
- ✅ You prefer typing numbers

**Use v2.1.4 if:**
- ⚠️ Home Assistant 2023.7 or earlier
- ⚠️ NumberSelector causes issues
- ⚠️ You prefer sliders (some people do!)

## Summary

v2.1.5 adds the **quality of life improvement** of number box inputs while maintaining all the **stability and functionality** of v2.1.4.

Both initial configuration and reconfiguration now have a better user experience with direct number input.

**This is the recommended version for most users.** 🎉
