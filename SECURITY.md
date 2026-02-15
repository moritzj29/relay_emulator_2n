# Security Assessment & Best Practices - 2N IP Relay Emulator

## Security Overview

This document provides a comprehensive security assessment of the 2N IP Relay Emulator integration and recommended deployment practices.

## Security Improvements in Latest Version

### ✅ **Implemented Security Features**

#### 1. **Nonce Expiry & Replay Protection**
```python
NONCE_EXPIRY_SECONDS = 300  # 5 minutes
```
- Nonces now expire after 5 minutes
- Prevents replay attacks using old authentication tokens
- Invalid/expired nonces are rejected (no longer accepted "for compatibility")

#### 2. **Nonce Cache Management**
```python
MAX_NONCE_CACHE_SIZE = 1000
```
- Automatic cleanup of expired nonces
- Maximum cache size to prevent memory exhaustion
- Oldest entries removed when limit reached

#### 3. **Pre-calculated HA1 Hash**
```python
self.ha1 = hashlib.md5(f"{username}:{realm}:{password}").hexdigest()
```
- Password hash calculated once at initialization
- Raw password not stored in memory after init
- Reduces exposure time of plaintext password

#### 4. **Enhanced Logging**
- Authentication failures logged with details
- Invalid nonces, expired nonces tracked
- Helps detect attack attempts

#### 5. **Improved Password Storage** (Partial)
```python
options={
    CONF_PASSWORD: user_input[CONF_PASSWORD],
}
```
- Password stored in `options` dict instead of `data`
- Enables Home Assistant's encryption capabilities (if configured)
- Note: HA's encryption requires secret key configuration

---

## Current Security Status

### ✅ **Secure in Recommended Deployment**

**When deployed correctly (local network or VPN only):**
- ✅ HTTP Digest Authentication prevents credential interception
- ✅ Nonce-based replay protection (5-minute window)
- ✅ Integration with HA's security model
- ✅ No credentials transmitted in plaintext
- ✅ Rate limiting via HA's existing mechanisms

### 🟡 **Moderate Risk Areas**

#### 1. **Credential Storage**
**Current State:**
- Passwords stored in Home Assistant's config entry storage
- File: `.storage/core.config_entries`
- Encryption: **Depends on HA configuration**

**Risk Level:** Medium
- ✅ File system permissions protect storage
- ✅ Requires physical/root access to read
- ⚠️ Backups may contain credentials
- ⚠️ Not encrypted by default (requires secret key)

**Mitigation:**
```yaml
# configuration.yaml - Enable encryption
homeassistant:
  # This encrypts sensitive data in storage
  encryption_key: !secret encryption_key
```

#### 2. **MD5 Usage**
**Current State:**
- MD5 used for digest authentication (RFC 2617 requirement)

**Risk Level:** Low
- ⚠️ MD5 is cryptographically weak
- ✅ Required by HTTP Digest Auth spec
- ✅ Still acceptable for this use case
- ✅ Passwords never transmitted in plaintext

**Note:** Cannot be changed without breaking 2N device compatibility.

#### 3. **No HTTPS Enforcement**
**Current State:**
- Integration works over HTTP or HTTPS
- No check to enforce HTTPS usage

**Risk Level:** Varies by deployment
- ✅ Safe on local network
- ✅ Safe over VPN
- 🔴 **UNSAFE over public internet without HTTPS**

---

## Threat Model Analysis

### Local Network Deployment (Recommended)

**Threat:** Network sniffing on local LAN
- **Risk:** Low
- **Reason:** Attacker needs network access
- **Mitigation:** Digest auth prevents credential capture even if traffic intercepted

**Threat:** Config file access
- **Risk:** Medium
- **Reason:** Local users with HA access can read config
- **Mitigation:** 
  - Use HA's encryption key
  - Restrict HA file system access
  - Strong OS-level user permissions

**Threat:** Replay attacks
- **Risk:** Low
- **Reason:** 5-minute nonce expiry window
- **Mitigation:** Nonces expire and are validated

### VPN Deployment (Recommended)

**Threat:** VPN traffic interception
- **Risk:** Very Low
- **Reason:** VPN encrypts all traffic
- **Mitigation:** VPN encryption + digest auth = defense in depth

### Public Internet Exposure (NOT RECOMMENDED)

**Threat:** Credential brute force
- **Risk:** High
- **Reason:** No built-in rate limiting
- **Mitigation:** 
  - Use HA's fail2ban integration
  - Use reverse proxy with rate limiting
  - Enable HA's IP ban

**Threat:** Man-in-the-middle attacks
- **Risk:** High (without HTTPS)
- **Reason:** HTTP digest auth vulnerable to MITM
- **Mitigation:** **MUST use HTTPS**

---

## Security Best Practices

### 🔒 **Essential Security Measures**

#### 1. **Change Default Credentials**
```
DO NOT USE:
- Username: admin
- Password: 2n

INSTEAD USE:
- Username: unique_username
- Password: strong_random_password_32chars+
```

Generate strong password:
```bash
openssl rand -base64 32
```

#### 2. **Enable Home Assistant Encryption**
```yaml
# configuration.yaml
homeassistant:
  encryption_key: !secret encryption_key

# secrets.yaml (generate with: openssl rand -base64 32)
encryption_key: "YOUR_GENERATED_KEY_HERE"
```

#### 3. **Use HTTPS for External Access**
If accessible outside local network:
```yaml
# configuration.yaml
http:
  ssl_certificate: /ssl/fullchain.pem
  ssl_key: /ssl/privkey.pem
```

Or use Nabu Casa (automatically HTTPS):
```
https://your-id.ui.nabu.casa/2n-relay/...
```

#### 4. **Restrict Network Access**
**Firewall rules (example for UFW):**
```bash
# Allow only from local network
sudo ufw allow from 192.168.1.0/24 to any port 8123

# Or allow only specific 2N device IP
sudo ufw allow from 192.168.1.50 to any port 8123
```

#### 5. **Enable Home Assistant Authentication**
Even on local network:
```yaml
# configuration.yaml
http:
  use_x_forwarded_for: true
  trusted_proxies:
    - 192.168.1.0/24
  ip_ban_enabled: true
  login_attempts_threshold: 5
```

#### 6. **Monitor for Failed Authentication**
```yaml
# automations.yaml
- id: 'auth_failure_alert'
  alias: "Alert on Repeated Auth Failures"
  trigger:
    - platform: event
      event_type: system_log_event
      event_data:
        level: WARNING
        message: "Digest auth: Invalid"
  condition:
    - condition: template
      value_template: >
        {{ trigger.event.data.count > 5 }}
  action:
    - service: notify.admin
      data:
        title: "Security Alert"
        message: "Multiple authentication failures detected"
```

### 🌐 **Network Architecture Recommendations**

#### **Best: VLAN Isolation**
```
Internet
    ↓
 Router/Firewall
    ↓
  ├─── VLAN 10: Home Automation (HA + 2N devices)
  ├─── VLAN 20: Trusted Devices (your phone/laptop)
  └─── VLAN 30: IoT Devices (isolated)

Rules:
- VLAN 10 can communicate internally
- VLAN 20 can access VLAN 10 (HA)
- VLAN 10 cannot access other VLANs
```

#### **Good: DMZ with Firewall**
```
Internet
    ↓
 Firewall
    ↓
  ├─── DMZ: Home Assistant (strict rules)
  └─── LAN: Internal Network

Rules:
- 2N devices can only access HA on port 8123
- HA cannot initiate connections to LAN
- All external access via VPN only
```

#### **Acceptable: Home Network with VPN**
```
Internet
    ↓
VPN Server (WireGuard/OpenVPN)
    ↓
Home Network
    ↓
Home Assistant + 2N Devices

- No direct internet exposure
- All access via VPN
```

---

## Security Checklist

### Setup Checklist
- [ ] Changed default username and password
- [ ] Used strong password (32+ characters)
- [ ] Enabled Home Assistant encryption key
- [ ] Configured HTTPS (if externally accessible)
- [ ] Restricted network access to trusted IPs
- [ ] Enabled IP ban in Home Assistant
- [ ] Set up authentication failure monitoring
- [ ] Tested authentication works correctly
- [ ] Verified 2N device can authenticate
- [ ] Documented credentials in secure password manager

### Maintenance Checklist (Monthly)
- [ ] Review Home Assistant logs for auth failures
- [ ] Check for integration updates
- [ ] Verify credentials haven't been compromised
- [ ] Test authentication still working
- [ ] Review firewall rules
- [ ] Check for unauthorized relay activations

### Incident Response
If you suspect compromise:
1. Immediately change password via HA integration config
2. Review HA logs for unauthorized access
3. Check relay activation history
4. Review video footage of physical door access
5. Consider rotating all access credentials
6. Check for unauthorized config changes

---

## Comparison with Alternatives

### vs. Physical 2N IP Relay
**Security:**
- Physical: Credentials on device (harder to extract)
- Emulator: Credentials in HA storage (easier if HA compromised)
- **Winner:** Physical (slightly)

**Network:**
- Physical: Separate device/IP to protect
- Emulator: Uses HA's existing security
- **Winner:** Emulator (fewer attack surfaces)

### vs. Home Assistant Native Integration
**Security:**
- Native: Could use HA's authentication system
- Current: Separate digest auth
- **Future:** Could be enhanced to use HA auth

---

## Future Security Enhancements

### Potential Improvements:
1. **Optional HA Authentication Integration**
   - Use HA's user system instead of separate credentials
   - Leverage HA's MFA/2FA capabilities

2. **Rate Limiting**
   - Built-in rate limiting per IP
   - Automatic temporary bans

3. **SHA-256 Digest Auth** (if 2N supports)
   - Stronger than MD5
   - Requires 2N device support

4. **Audit Logging**
   - Detailed logs of all relay activations
   - Who/what/when for compliance

5. **Mutual TLS** (if 2N supports)
   - Certificate-based authentication
   - Strongest authentication method

---

## Conclusion

### ✅ **Current Security Status: GOOD for Recommended Use**

**The integration is secure when deployed correctly:**
1. ✅ Local network or VPN access only
2. ✅ Strong unique credentials used
3. ✅ Home Assistant properly secured
4. ✅ Regular security updates applied
5. ✅ Access monitoring in place

**Key Security Principles:**
- Defense in depth (multiple layers)
- Principle of least privilege (minimal access)
- Regular monitoring and updates
- Strong credential management

**Bottom Line:**
The integration provides adequate security for local/VPN deployment with proper configuration. The main security responsibility lies in securing Home Assistant itself and the network infrastructure.

---

## Getting Help

For security concerns:
1. Review this document
2. Check Home Assistant security best practices
3. Consult network security professional if exposing to internet
4. Report security vulnerabilities privately to maintainer

**Remember:** Security is a process, not a product. Regular review and updates are essential.
