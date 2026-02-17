# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.1.1] - 2026-02-17

### Fixed
- issue with entities being not available due to the newly added attributes
- issue when entity links are broken after the number of relays or buttons has been reduced

## [3.1.0] - 2026-02-17

### Added
- add enpoint URLs as entity attributes

## [3.0.0] - 2026-02-17

### Added
- support installation via HACS

## [2.3.0] - 2026-02-17

### Added
- Improved HTTP server cleanup with attempt at route unregistration
- Enhanced error handling in async_unload_entry
- Duplicate route prevention on reload
- Better logging for HTTP server lifecycle
- Comprehensive unit tests for all endpoints
- GitHub Actions CI/CD workflows
- Release automation with git tags

### Fixed
- URI mismatch in digest authentication verification
- Missing DOMAIN import usage in relay control
- URI reconstruction security issue in digest auth
- Timing attack vulnerability using constant-time comparison
- HTTP view cleanup on reload

### Security
- Enhanced nonce cache management
- Pre-calculated HA1 hash for performance
- Implemented constant-time hash comparison (hmac.compare_digest)
- Added nonce expiry validation (5-minute window)
- Improved error handling in authentication

## [2.1.6] - 2026-02-10

### Added
- Initial comprehensive security assessment documentation
- SECURITY.md with threat model analysis
- Security best practices and deployment recommendations

### Fixed
- Nonce expiry and replay protection implementation
- Enhanced logging for authentication failures

## [2.1.0] - 2026-02-01

### Added
- HTTP Digest Authentication support
- Relay and button endpoint handlers
- Config flow for Home Assistant integration
- Entity platform support (switch, button)

### Features
- Drop-in replacement for 2N IP relay units
- Multiple subpath support
- Support for 0-16 relays and buttons per instance
- Home Assistant's HTTP server integration
