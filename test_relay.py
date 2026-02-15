#!/usr/bin/env python3
"""
Test script for 2N Relay Emulator (Subpath Version)
Tests all endpoints with digest authentication on Home Assistant's web server
"""

import requests
from requests.auth import HTTPDigestAuth
import sys
import time

# Configuration
HOST = "localhost"
PORT = 8123  # Home Assistant's port
SUBPATH = "2n-relay"  # Your configured subpath
USERNAME = "admin"
PASSWORD = "2n"

BASE_URL = f"http://{HOST}:{PORT}/{SUBPATH}"


def test_endpoint(name, method, path, params=None, expected_status=200):
    """Test a single endpoint."""
    url = f"{BASE_URL}/{path}"
    auth = HTTPDigestAuth(USERNAME, PASSWORD)
    
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    print(f"Method: {method}")
    print(f"URL: {url}")
    if params:
        print(f"Params: {params}")
    
    try:
        if method == "GET":
            response = requests.get(url, params=params, auth=auth, timeout=5)
        elif method == "POST":
            response = requests.post(url, params=params, auth=auth, timeout=5)
        else:
            print(f"❌ Unknown method: {method}")
            return False
        
        print(f"Status: {response.status_code}")
        print(f"Response:\n{response.text}")
        
        if response.status_code == expected_status:
            print(f"✅ Test passed!")
            return True
        else:
            print(f"❌ Test failed! Expected {expected_status}, got {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False


def test_authentication():
    """Test authentication failure."""
    url = f"{BASE_URL}/api/relay/status"
    
    print(f"\n{'='*60}")
    print("Testing: Authentication Failure (no auth)")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 401:
            print("✅ Correctly rejected unauthenticated request")
            return True
        else:
            print(f"❌ Expected 401, got {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False


def main():
    """Run all tests."""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║          2N Relay Emulator Test Suite                       ║
║               (Subpath Version)                              ║
╚══════════════════════════════════════════════════════════════╝

Target: {BASE_URL}
Username: {USERNAME}
Password: {PASSWORD}

Note: Home Assistant must be running and the integration configured
      with subpath '{SUBPATH}' for these tests to work.
""")
    
    tests = [
        # Authentication test
        ("Authentication Failure Test", test_authentication),
        
        # System info
        ("System Info", lambda: test_endpoint(
            "System Info",
            "GET",
            "api/system/info"
        )),
        
        # Relay status
        ("Relay Status", lambda: test_endpoint(
            "Relay Status",
            "GET",
            "api/relay/status"
        )),
        
        # Turn relay 1 on (GET)
        ("Turn Relay 1 ON (GET)", lambda: test_endpoint(
            "Turn Relay 1 ON via GET",
            "GET",
            "api/relay/ctrl",
            params={"relay": 1, "value": "on"}
        )),
        
        # Check status after turning on
        ("Status After ON", lambda: test_endpoint(
            "Check Status After ON",
            "GET",
            "api/relay/status"
        )),
        
        # Turn relay 1 off (POST)
        ("Turn Relay 1 OFF (POST)", lambda: test_endpoint(
            "Turn Relay 1 OFF via POST",
            "POST",
            "api/relay/ctrl",
            params={"relay": 1, "value": "off"}
        )),
        
        # Alternative path (without /api)
        ("Alternative Path - Turn Relay 2 ON", lambda: test_endpoint(
            "Turn Relay 2 ON (alternative path)",
            "GET",
            "relay/ctrl",
            params={"relay": 2, "value": "on"}
        )),
        
        # Alternative status path
        ("Alternative Status Path", lambda: test_endpoint(
            "Status via alternative path",
            "GET",
            "relay/status"
        )),
        
        # Invalid relay number
        ("Invalid Relay Number", lambda: test_endpoint(
            "Invalid Relay (99)",
            "GET",
            "api/relay/ctrl",
            params={"relay": 99, "value": "on"},
            expected_status=400
        )),
        
        # Invalid value
        ("Invalid Value", lambda: test_endpoint(
            "Invalid Value (invalid)",
            "GET",
            "api/relay/ctrl",
            params={"relay": 1, "value": "invalid"},
            expected_status=400
        )),
    ]
    
    # Run all tests
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append((test_name, False))
        
        # Small delay between tests
        time.sleep(0.5)
    
    # Print summary
    print(f"\n\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*60}\n")
    
    if passed < total:
        print("Troubleshooting tips:")
        print("1. Ensure Home Assistant is running")
        print("2. Verify the integration is configured with subpath '2n-relay'")
        print("3. Check Home Assistant logs for errors")
        print("4. Verify credentials match (admin/2n by default)")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
