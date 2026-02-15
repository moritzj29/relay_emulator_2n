# Changelog - 2N IP Relay Emulator

## Version 2.1.0 (Current) - 2024-02-15

### ✨ New Features
- **Full Reconfiguration Support** - All settings now editable after initial setup
  - Change URL subpath
  - Update username and password
  - Modify relay count (add/remove entities dynamically)
  - Modify button count (add/remove entities dynamically)
  - No need to delete and recreate integration

### 🔧 Improvements
- Options flow handler for reconfiguration UI
- Automatic integration reload after reconfiguration
- Current values pre-filled in reconfiguration dialog
- Validation for subpath conflicts during reconfiguration
- Better user feedback during reconfiguration process

### 📚 Documentation
- New RECONFIGURATION.md guide
- Detailed scenarios for common reconfiguration needs
- Best practices and troubleshooting

### 🎯 Use Cases Enabled
- Monthly credential rotation for security
- Expanding system by adding more doors/gates
- Reorganizing with nested path structure
- Converting between relay and button types
- Simplifying by removing unused entities

---

## Version 2.0.0 - 2024-02-15

### ✨ Major Features
- **Button Platform Added** - Momentary triggers alongside switches
  - Stateless button entities for door strikes
  - API: `/api/button/trigger?button=N`
  - Configure 0-16 buttons per instance

- **Nested Subpath Support** - Hierarchical URL organization
  - Support for forward slashes in subpaths
  - Examples: `2n/door1`, `building/floor2/entrance`
  - Better organization for complex installations

- **Number Box Input** - Replaced sliders with number inputs
  - Direct numeric entry (0-16)
  - More precise configuration
  - Better UX for larger installations

### 🔒 Security Enhancements
- Nonce expiry (5-minute window)
- Replay attack protection
- Automatic nonce cache cleanup
- Maximum cache size enforcement (1000 nonces)
- Pre-calculated HA1 hash (password not stored in memory)
- Enhanced authentication logging

### 🔧 Improvements
- Increased max entities: 8 → 16 relays, 16 buttons (32 total)
- Better password storage (options dict for encryption support)
- Improved digest authentication implementation
- Better error messages and validation

### 📚 Documentation
- Comprehensive FEATURES_V2.md guide
- QUICK_REFERENCE_V2.md for fast lookup
- SECURITY.md with best practices
- Performance analysis documentation

---

## Version 1.0.0 - Initial Release

### ✨ Features
- HTTP Digest Authentication compatible with 2N devices
- Switch entities (relays) for door control
- Support for 1-8 relays per instance
- 2N-compatible API endpoints:
  - `/api/relay/ctrl?relay=N&value=on|off`
  - `/api/relay/status`
  - `/api/system/info`
- Simple subpath configuration (no nesting)
- Uses Home Assistant's built-in HTTP server
- No separate port required

### 🔒 Security
- HTTP Digest Authentication (RFC 2617)
- MD5 hashing (required by spec)
- Basic nonce validation

---

## Version History Summary

| Version | Date | Key Features |
|---------|------|--------------|
| 2.1.0 | 2024-02-15 | ✅ Full reconfiguration support |
| 2.0.0 | 2024-02-15 | ✅ Buttons, nested paths, number inputs, security |
| 1.0.0 | 2024-02-15 | ✅ Initial release with relay support |

---

## Migration Guides

### From 2.0.0 to 2.1.0
✅ **No migration needed** - Drop-in replacement
- All configurations work as-is
- New reconfiguration UI available automatically
- No breaking changes

### From 1.0.0 to 2.0.0
⚠️ **Architectural changes** - See CHANGELOG.md in v2.0 package
- Port-based → Subpath-based (different URL structure)
- Existing instances may need reconfiguration
- Update 2N device URLs after upgrade

---

## Upcoming Features (Planned)

### Version 2.2.0 (Proposed)
- [ ] Multiple authentication realms support
- [ ] Per-relay/button custom names
- [ ] Last triggered timestamp for buttons
- [ ] Rate limiting per IP address
- [ ] Integration with HA's user system (optional)

### Version 3.0.0 (Future)
- [ ] Web UI for testing/monitoring
- [ ] Statistics and usage tracking
- [ ] Advanced automation triggers
- [ ] Multi-tenancy support
- [ ] API key authentication option

---

## Deprecation Notices

### None Currently
All features remain supported and maintained.

---

## Known Issues

### Version 2.1.0
- None reported

### Version 2.0.0
- None reported

### Version 1.0.0
- Nonces not properly validated (Fixed in 2.0.0)
- No replay protection (Fixed in 2.0.0)
- Unbounded nonce cache (Fixed in 2.0.0)

---

## Upgrade Instructions

### For All Versions

**From HACS:**
1. Update in HACS
2. Restart Home Assistant
3. Existing configurations preserved

**Manual Installation:**
1. Replace files in `/config/custom_components/2n_relay_emulator/`
2. Restart Home Assistant
3. Verify in Integrations page

### Post-Upgrade Checklist
- [ ] Verify integration loaded (check logs)
- [ ] Test authentication from 2N device
- [ ] Check entities are responsive
- [ ] Verify automations still work
- [ ] Test reconfiguration UI (v2.1.0+)

---

## Breaking Changes

### Version 2.1.0
**None** - Fully backward compatible

### Version 2.0.0
**None** - Backward compatible with v1.0
- New features optional
- Existing relay configurations work unchanged

### Version 1.0.0
**N/A** - Initial release

---

## Security Advisories

### SA-2024-001 - Nonce Replay Vulnerability (Fixed in 2.0.0)
**Severity:** Medium  
**Affected:** v1.0.0  
**Fixed:** v2.0.0  
**Details:** Nonces were accepted even when invalid, allowing replay attacks  
**Action:** Upgrade to v2.0.0 or later

---

## Contributors

### Version 2.1.0
- Reconfiguration feature implementation
- Enhanced options flow
- Documentation updates

### Version 2.0.0
- Button platform implementation
- Nested path support
- Security hardening
- Comprehensive documentation

### Version 1.0.0
- Initial implementation
- Core functionality
- HTTP Digest Auth integration

---

## Support

### Reporting Issues
1. Check TROUBLESHOOTING.md first
2. Review SECURITY.md for security questions
3. Open GitHub issue with:
   - Version number
   - Home Assistant version
   - Configuration (sanitized)
   - Logs (sanitized)
   - Steps to reproduce

### Feature Requests
1. Check planned features list
2. Open GitHub discussion
3. Describe use case
4. Explain expected behavior

---

## License

MIT License - See LICENSE file for details

---

## Acknowledgments

- Home Assistant community for integration framework
- 2N Systems for API compatibility requirements
- Contributors and testers

---

**Last Updated:** February 15, 2024  
**Current Version:** 2.1.0
