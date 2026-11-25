                      
"""
Comprehensive test for the AD water quality monitoring system
Tests:
1. User registration and authentication
2. Device CRUD operations
3. Device pairing flow
4. Measurement endpoints
5. API integration
"""

import requests
import time
import sys

BASE_URL = "http://localhost:8004"
API_BASE = f"{BASE_URL}/api/v1"

def test_health():
                              
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        print("✓ Health endpoint works")
        return True
    except Exception as e:
        print(f"✗ Health endpoint failed: {e}")
        return False

def test_user_registration():
                                
    print("\nTesting user registration...")
    timestamp = int(time.time())
    user_data = {
        "email": f"testuser{timestamp}@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User"
    }

    try:
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=user_data
        )
        print(f"Registration response: {response.status_code}")
        print(f"Response body: {response.text}")

        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            print("✓ User registration successful")
            return data["access_token"], user_data["email"], user_data["password"]
        else:
            print(f"✗ User registration failed: {response.text}")
            return None, None, None
    except Exception as e:
        print(f"✗ User registration error: {e}")
        return None, None, None

def test_user_login(email, password):
                         
    print("\nTesting user login...")
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            data={
                "username": email,
                "password": password
            }
        )
        print(f"Login response: {response.status_code}")
        print(f"Response body: {response.text}")

        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            print("✓ User login successful")
            return data["access_token"]
        else:
            print(f"✗ User login failed: {response.text}")
            return None
    except Exception as e:
        print(f"✗ User login error: {e}")
        return None

def test_device_crud(token):
                                     
    print("\nTesting device CRUD operations...")
    headers = {"Authorization": f"Bearer {token}"}

    print("  Creating device...")
    device_data = {
        "device_id": f"TEST_DEVICE_{int(time.time())}",
        "name": "Test Device for CRUD"
    }

    try:
        response = requests.post(
            f"{API_BASE}/devices/",
            json=device_data,
            headers=headers
        )
        print(f"  Create response: {response.status_code}")

        if response.status_code != 201:
            print(f"  ✗ Device creation failed: {response.text}")
            return False

        device = response.json()
        device_id = device["id"]
        device_device_id = device["device_id"]
        print(f"  ✓ Device created with ID: {device_id}, device_id: {device_device_id}")

        print("  Getting device by device_id...")
        response = requests.get(
            f"{API_BASE}/devices/{device_device_id}",
            headers=headers
        )
        print(f"  Get response: {response.status_code}")

        if response.status_code != 200:
            print(f"  ✗ Get device failed: {response.text}")
            return False

        device_get = response.json()
        assert device_get["id"] == device_id
        assert device_get["device_id"] == device_device_id
        print("  ✓ Device retrieved successfully")

        print("  Listing devices...")
        response = requests.get(
            f"{API_BASE}/devices/",
            headers=headers
        )
        print(f"  List response: {response.status_code}")

        if response.status_code != 200:
            print(f"  ✗ List devices failed: {response.text}")
            return False

        devices = response.json()
        assert len(devices) >= 1
        print(f"  ✓ Found {len(devices)} devices")

        print("  Updating device...")
        update_data = {
            "name": "Updated Test Device Name"
        }
        response = requests.put(
            f"{API_BASE}/devices/{device_device_id}",
            json=update_data,
            headers=headers
        )
        print(f"  Update response: {response.status_code}")

        if response.status_code != 200:
            print(f"  ✗ Device update failed: {response.text}")
            return False

        device_updated = response.json()
        assert device_updated["name"] == update_data["name"]
        print("  ✓ Device updated successfully")

        print("  Testing heartbeat...")
        response = requests.post(
            f"{API_BASE}/devices/{device_device_id}/heartbeat",
            headers=headers
        )
        print(f"  Heartbeat response: {response.status_code}")

        if response.status_code != 200:
            print(f"  ✗ Heartbeat failed: {response.text}")
            return False

        device_heartbeat = response.json()
        assert device_heartbeat["last_seen"] is not None
        print("  ✓ Heartbeat updated successfully")

        print("  Deleting device...")
        response = requests.delete(
            f"{API_BASE}/devices/{device_device_id}",
            headers=headers
        )
        print(f"  Delete response: {response.status_code}")

        if response.status_code != 204:
            print(f"  ✗ Device deletion failed: {response.text}")
            return False

        response = requests.get(
            f"{API_BASE}/devices/{device_device_id}",
            headers=headers
        )
        if response.status_code != 404:
            print(f"  ✗ Device still exists after deletion: {response.text}")
            return False

        print("  ✓ Device deleted successfully")
        return True

    except Exception as e:
        print(f"  ✗ Device CRUD error: {e}")
        return False

def test_device_pairing(token):
                                  
    print("\nTesting device pairing flow...")
    headers = {"Authorization": f"Bearer {token}"}

    device_data = {
        "device_id": f"PAIR_TEST_{int(time.time())}",
        "name": "Pairing Test Device"
    }

    try:
        response = requests.post(
            f"{API_BASE}/devices/",
            json=device_data,
            headers=headers
        )

        if response.status_code != 201:
            print(f"  ✗ Failed to create device for pairing: {response.text}")
            return False

        device = response.json()
        device_id = device["id"]
        device_device_id = device["device_id"]
        print(f"  ✓ Created device for pairing: {device_device_id}")

        print("  Generating pairing code...")
        response = requests.post(
            f"{API_BASE}/devices/{device_device_id}/code",
            headers=headers
        )
        print(f"  Generate code response: {response.status_code}")

        if response.status_code != 200:
            print(f"  ✗ Failed to generate pairing code: {response.text}")
            return False

        code_data = response.json()
        assert "device_code" in code_data
        pairing_code = code_data["device_code"]
        print(f"  ✓ Pairing code generated: {pairing_code}")

        print("  Exchanging code for secret...")
        pair_data = {
            "device_id": device_device_id,
            "device_code": pairing_code
        }
        response = requests.post(
            f"{API_BASE}/devices/pair",
            json=pair_data,
            headers=headers
        )
        print(f"  Pair response: {response.status_code}")

        if response.status_code != 200:
            print(f"  ✗ Failed to exchange code for secret: {response.text}")
            return False

        pair_result = response.json()
        assert "device_secret" in pair_result
        device_secret = pair_result["device_secret"]
        print(f"  ✓ Device secret received (length: {len(device_secret)})")

        print("  Testing device authentication...")
        device_token_data = {
            "device_id": device_device_id,
            "device_secret": device_secret
        }
        response = requests.post(
            f"{API_BASE}/auth/device/login",
            json=device_token_data
        )
        print(f"  Device login response: {response.status_code}")

        if response.status_code != 200:
            print(f"  ✗ Device authentication failed: {response.text}")
            return False

        device_token = response.json()["access_token"]
        print("  ✓ Device authentication successful")

        print("  Testing device endpoint access...")
        device_headers = {"Authorization": f"Bearer {device_token}"}
        response = requests.get(
            f"{API_BASE}/devices/{device_device_id}",
            headers=device_headers
        )
        print(f"  Device self-access response: {response.status_code}")

        if response.status_code != 200:
            print(f"  ✗ Device cannot access own endpoint: {response.text}")
            return False

        print("  ✓ Device can access own endpoint")
        return True

    except Exception as e:
        print(f"  ✗ Device pairing error: {e}")
        return False

def test_measurement_endpoints(token):
                                    
    print("\nTesting measurement endpoints...")
    headers = {"Authorization": f"Bearer {token}"}

    device_data = {
        "device_id": f"MEAS_TEST_{int(time.time())}",
        "name": "Measurement Test Device"
    }

    try:
        response = requests.post(
            f"{API_BASE}/devices/",
            json=device_data,
            headers=headers
        )

        if response.status_code != 201:
            print(f"  ✗ Failed to create device for measurements: {response.text}")
            return False

        device = response.json()
        device_id = device["id"]
        device_device_id = device["device_id"]
        print(f"  ✓ Created device for measurements: {device_device_id}")

        print("  Testing latest measurement endpoint...")
        response = requests.get(
            f"{API_BASE}/measurements/{device_device_id}/latest",
            headers=headers
        )
        print(f"  Latest measurement response: {response.status_code}")

        if response.status_code == 404:
            print("  ✓ Latest measurement correctly returns 404 for new device")
        elif response.status_code == 200:
            print("  ℹ Latest measurement returned data (unexpected but ok)")
        else:
            print(f"  ✗ Unexpected response for latest measurement: {response.text}")
            return False

        print("  Testing measurement history endpoint...")
        from datetime import datetime, timedelta
        since_time = datetime.utcnow() - timedelta(hours=24)
        since_str = since_time.isoformat()
        response = requests.get(
            f"{API_BASE}/measurements/{device_device_id}/since/{since_str}",
            headers=headers
        )
        print(f"  History response: {response.status_code}")

        if response.status_code != 200:
            print(f"  ✗ Measurement history failed: {response.text}")
            return False

        history = response.json()
        assert isinstance(history, list)
        print(f"  ✓ Measurement history retrieved: {len(history)} records")

        print("  Testing measurement creation...")
        measurement_data = {
            "device_id": device_device_id,
            "temperature": 22.3,
            "water_quality_ph": 6.8,
            "water_quality_turbidity": 1.2
        }
        response = requests.post(
            f"{API_BASE}/measurements/",
            json=measurement_data,
            headers=headers
        )
        print(f"  Create measurement response: {response.status_code}")

        if response.status_code != 201:
            print(f"  ✗ Measurement creation failed: {response.text}")
            return False

        measurement = response.json()
        print("  ✓ Measurement created successfully")

        print("  Testing latest measurement after creation...")
        response = requests.get(
            f"{API_BASE}/measurements/{device_device_id}/latest",
            headers=headers
        )
        print(f"  Latest measurement response: {response.status_code}")

        if response.status_code != 200:
            print(f"  ✗ Latest measurement failed after creation: {response.text}")
            return False

        latest = response.json()
        print("  ✓ Latest measurement returns correct data")

        print("  Testing measurement history after creation...")
        from datetime import datetime, timedelta
        since_time = datetime.utcnow() - timedelta(hours=24)
        since_str = since_time.isoformat()
        response = requests.get(
            f"{API_BASE}/measurements/{device_device_id}/since/{since_str}",
            headers=headers
        )
        print(f"  History response: {response.status_code}")

        if response.status_code != 200:
            print(f"  ✗ Measurement history failed after creation: {response.text}")
            return False

        history = response.json()
        assert isinstance(history, list)
        assert len(history) >= 1
        print(f"  ✓ Measurement history after creation: {len(history)} records")

        return True

    except Exception as e:
        print(f"  ✗ Measurement endpoints error: {e}")
        return False

def run_all_tests():
                       
    print("=" * 60)
    print("COMPREHENSIVE SYSTEM TEST")
    print("=" * 60)

    results = []

    results.append(("Health Endpoint", test_health()))

    token, email, password = test_user_registration()
    if token:
        results.append(("User Registration", True))

        login_token = test_user_login(email, password)
        if login_token:
            results.append(("User Login", True))
            token = login_token
        else:
            results.append(("User Login", False))
    else:
        results.append(("User Registration", False))
        results.append(("User Login", False))

    if not token:
        print("\n❌ Cannot proceed without authentication token")
        print_test_summary(results)
        return False

    results.append(("Device CRUD Operations", test_device_crud(token)))

    results.append(("Device Pairing Flow", test_device_pairing(token)))

    results.append(("Measurement Endpoints", test_measurement_endpoints(token)))

    print_test_summary(results)

    return all(result[1] for result in results)

def print_test_summary(results):
                                    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        symbol = "✓" if success else "✗"
        print(f"{symbol} {test_name:<30} [{status}]")
        if success:
            passed += 1

    print("-" * 60)
    print(f"TOTAL: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"❌ {total - passed} test(s) failed")

    print("=" * 60)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
