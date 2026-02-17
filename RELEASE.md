# Release Process

This document describes the release process for the IP Relay Emulator for 2N integration.

## Version Management

All version numbers are centralized in [`relay_emulator_2n/const.py`](relay_emulator_2n/const.py):

```python
VERSION = "2.3.0"
```

This version is automatically used by:
- `relay_emulator_2n/manifest.json` (manual update required)
- `hacs.json` (manual update required - kept in sync with manifest.json)
- `switch.py` (device_info)
- `button.py` (device_info)
- `http_server.py` (system info endpoint)

## Semantic Versioning

We follow [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes, incompatible API changes
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes, security updates

Examples:
- Feature addition: `2.3.0` → `2.4.0`
- Bug fix: `2.3.0` → `2.3.1`
- Major refactor: `2.3.0` → `3.0.0`

## Release Checklist

### 1. Prepare the Release

1. **Update version in [`relay_emulator_2n/const.py`](relay_emulator_2n/const.py)**
   ```python
   VERSION = "X.Y.Z"
   ```

2. **Update version in [`relay_emulator_2n/manifest.json`](relay_emulator_2n/manifest.json)**
   ```json
   {
     "version": "X.Y.Z",
     ...
   }
   ```

3. **Update version in [`hacs.json`](hacs.json)** - MUST match manifest.json
   ```json
   {
     "version": "X.Y.Z",
     ...
   }
   ```

4. **Create/Update CHANGELOG.md** with release notes:
   ```markdown
   ## [X.Y.Z] - YYYY-MM-DD

   ### Added
   - New feature description

   ### Fixed
   - Bug fix description

   ### Security
   - Security fix description
   ```

4. **Create/Update CHANGELOG.md** with release notes:
   ```markdown
   ## [X.Y.Z] - YYYY-MM-DD

   ### Added
   - New feature description

   ### Fixed
   - Bug fix description

   ### Security
   - Security fix description
   ```

5. **Run tests to ensure everything passes**
   ```bash
   pytest -v
   ```

6. **Commit changes**
   ```bash
   git commit -m "chore: bump version to X.Y.Z"
   ```

### 2. Create Git Tag

```bash
git tag -a vX.Y.Z -m "Release version X.Y.Z"
git push origin vX.Y.Z
```

**Important:** Both `relay_emulator_2n/manifest.json` and `hacs.json` must be updated with the same version before tagging.

Push the tag to trigger the automated release workflow (see `.github/workflows/release.yml`):

- ✅ Runs all tests
- ✅ Creates GitHub Release
- ✅ Generates release notes from commits
- ✅ Attaches artifacts (if needed)

## Pre-Release Checklist

Before pushing a release tag:

- [ ] All tests passing (`pytest -v`)
- [ ] Code review completed
- [ ] CHANGELOG.md updated
- [ ] Version numbers updated (const.py, manifest.json, hacs.json)
- [ ] Verify manifest.json and hacs.json have matching versions
- [ ] No uncommitted changes
- [ ] Branch is up-to-date with main

## Post-Release

After a release is published:

1. Verify release is visible on GitHub
2. Test installation from release
3. Announce release (if applicable)

## Troubleshooting

### Release workflow didn't trigger
- Verify tag was pushed: `git push origin vX.Y.Z`
- Check tag format: `git tag -l` (should show `vX.Y.Z`)
- Check Actions tab for workflow status

### Need to re-release with same version
1. Delete local tag: `git tag -d vX.Y.Z`
2. Delete remote tag: `git push origin :vX.Y.Z`
3. Fix issues and recreate tag
4. Push again

### Fix in released version
Use next PATCH version for bug fixes:
- `2.3.0` (released with bug) → `2.3.1` (bug fix)
