import requests
import time
import os
import sys

from raspberry.ad_agent.api_client import ADAPIClient
from raspberry.ad_agent.db import MeasurementQueueDB
from raspberry.ad_agent.measurements import MeasurementProcessor

BASE_URL = "http://localhost:8000"
TEST_PASSWORD = "testpass1234"

def log_step(step_num, description):
    print(f"\n{step_num}. {description}")
    print("-" * 50)

def log_result(success, message):
    if success:
        print(f"   ✓ {message}")
    else:
        print(f"   ✗ {message}")
    return success

def make_request(method, endpoint, data=None, token=None, expected_status=200):
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        if method == "GET":
            resp = requests.get(url, headers=headers)
        elif method == "POST":
            if isinstance(data, dict):
                headers["Content-Type"] = "application/json"
                resp = requests.post(url, json=data, headers=headers)
            else:
                headers["Content-Type"] = "application/x-www-form-urlencoded"
                resp = requests.post(url, data=data, headers=headers)
        elif method == "PUT":
            headers["Content-Type"] = "application/json"
            resp = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")

        if resp.status_code == expected_status:
            try:
                return True, resp.json() if resp.content else {}
            except ValueError:
                return True, {}
        else:
            try:
                error_detail = resp.json().get("detail", resp.text)
            except (AttributeError, TypeError, ValueError):
                error_detail = resp.text
            return False, f"HTTP {resp.status_code}: {error_detail}"
    except Exception as e:
        return False, f"Request error: {e}"

def test_user_registration():
    log_step(1, "User registration")
    unique_email = f"e2e-{time.time_ns()}@test.com"
    success, result = make_request(
        "POST",
        "/api/v1/auth/register",
        {
            "email": unique_email,
            "password": TEST_PASSWORD,
            "full_name": "E2E Test User"
        }
    )
    if success and "access_token" in result:
        print(f"   Got token: {result['access_token'][:10]}...")
        return result["access_token"], unique_email
    else:
        print(f"   Failed to register user: {result}")
        return None, None

def test_user_login(email, password):
    log_step(2, "User login")
    success, result = make_request(
        "POST",
        "/api/v1/auth/login",
        data=f"username={email}&password={password}",
        expected_status=200
    )
    if success and "access_token" in result:
        return result["access_token"]
    else:
        print(f"   Failed to login: {result}")
        return None

def test_device_registration(user_token, device_id, device_name):
    log_step(3, "Device registration")
    success, result = make_request(
        "POST",
        "/api/v1/devices/",
        {
            "device_id": device_id,
            "name": device_name
        },
        token=user_token,
        expected_status=201
    )
    if success and "id" in result:
        return result["id"], result
    else:
        print(f"   Failed to register device: {result}")
        return None, None

def test_generate_pairing_code(user_token, device_id):
    log_step(4, "Generate pairing code")
    success, result = make_request(
        "POST",
        f"/api/v1/devices/{device_id}/code",
        token=user_token
    )
    if success and "device_code" in result:
        return result["device_code"]
    else:
        print(f"   Failed to generate pairing code: {result}")
        return None

def test_pair_device(user_token, device_id, device_code):
    log_step(5, "Pair device")
    success, result = make_request(
        "POST",
        "/api/v1/devices/pair",
        {
            "device_id": device_id,
            "device_code": device_code
        },
        token=user_token
    )
    if success and "device_secret" in result:
        return result["device_secret"]
    else:
        print(f"   Failed to pair device: {result}")
        return None

def test_device_authentication(device_id, device_secret):
    log_step(6, "Device authentication")
    success, result = make_request(
        "POST",
        "/api/v1/devices/auth",
        {
            "device_id": device_id,
            "device_secret": device_secret
        }
    )
    if success and "access_token" in result:
        return result["access_token"]
    else:
        print(f"   Failed to authenticate device: {result}")
        return None

def test_heartbeat(device_token, device_id):
    log_step(7, "Heartbeat")
    success, result = make_request(
        "POST",
        f"/api/v1/devices/{device_id}/heartbeat",
        token=device_token
    )
    if success:
        return True
    else:
        print(f"   Failed to send heartbeat: {result}")
        return False

def test_send_measurement(device_token, measurement_data):
    log_step(8, "Send measurement")
    success, result = make_request(
        "POST",
        "/api/v1/measurements/",
        measurement_data,
        token=device_token,
        expected_status=201
    )
    if success and "id" in result:
        return result["id"]
    else:
        print(f"   Failed to send measurement: {result}")
        return None

def test_get_latest_measurement(user_token, device_id):
    log_step(9, "Get latest measurement")
    success, result = make_request(
        "GET",
        f"/api/v1/measurements/{device_id}/latest",
        token=user_token
    )
    if success:
        return result
    else:
        print(f"   Failed to get latest measurement: {result}")
        return None

def test_get_measurement_history(user_token, device_id, limit=10):
    log_step(10, "Get measurement history")
    success, result = make_request(
        "GET",
        f"/api/v1/measurements/{device_id}?limit={limit}",
        token=user_token
    )
    if success:
        return result
    else:
        print(f"   Failed to get measurement history: {result}")
        return None

def test_offline_queue_and_recovery(device_id, device_secret, user_token):
    log_step(11, "Backend unavailable → agent queue → retry")
    queue_path = f"/tmp/ad-e2e-queue-{time.time_ns()}.sqlite"
    queue = MeasurementQueueDB(queue_path)
    measurement_id = f"e2e-queue-{time.time_ns()}"
    measurement = {
        "measurement_id": measurement_id,
        "device_id": device_id,
        "temperature": 25.0,
        "water_quality_turbidity": 0.3,
        "water_quality_ph": 7.0,
        "humidity": 50,
        "raw_data": '{"test":"offline"}',
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    try:
        if not queue.add_measurement(measurement):
            print("   Could not add measurement to the agent queue")
            return False

        offline_client = ADAPIClient("http://127.0.0.1:1", device_id, device_secret)
        MeasurementProcessor(queue, offline_client).process_queue()
        stats = queue.get_stats()
        if stats["unsent"] != 1 or stats["max_retries"] != 1:
            print(f"   Offline retry did not preserve the measurement: {stats}")
            return False

        processor = MeasurementProcessor(queue, ADAPIClient(BASE_URL, device_id, device_secret))
        for _ in range(5):
            processor.process_queue()
            stats = queue.get_stats()
            if stats["sent"] == 1:
                break
            time.sleep(1)

        if stats["unsent"] != 0 or stats["sent"] != 1:
            print(f"   Backend did not acknowledge the queued measurement: {stats}")
            return False

        history = test_get_measurement_history(user_token, device_id, limit=100)
        if not history or not any(row.get("measurement_id") == measurement_id for row in history):
            print("   Synced measurement is missing from backend history")
            return False

        print("   Agent queue retried the measurement and backend history contains it")
        return True
    finally:
        if os.path.exists(queue_path):
            os.remove(queue_path)

def test_idempotency_same_measurement_id():
    log_step(12, "Idempotency test - same measurement_id")
    print("   Sending same measurement twice...")

    measurement_data = {
        "device_id": "e2e-test-device-001",
        "temperature": 22.5,
        "water_quality_turbidity": 0.5,
        "water_quality_ph": 7.2,
        "humidity": 60,
        "raw_data": "{\"test\":\"idempotency\"}",
        "measurement_id": f"e2e-idem-{time.time_ns()}"
    }

    user_token, _ = test_user_registration()
    if not user_token:
        print("   Failed to create user for idempotency test")
        return False

    device_id_str = f"idempotent-test-device-{time.time_ns()}"
    internal_id, _ = test_device_registration(user_token, device_id_str, "Idempotency Test Device")
    if not internal_id:
        print("   Failed to create device for idempotency test")
        return False

    pairing_code = test_generate_pairing_code(user_token, device_id_str)
    if not pairing_code:
        print("   Failed to generate pairing code")
        return False

    device_secret = test_pair_device(user_token, device_id_str, pairing_code)
    if not device_secret:
        print("   Failed to pair device")
        return False

    device_token = test_device_authentication(device_id_str, device_secret)
    if not device_token:
        print("   Failed to authenticate device")
        return False

    measurement_data["device_id"] = device_id_str

    success1, result1 = make_request(
        "POST",
        "/api/v1/measurements/",
        measurement_data,
        token=device_token,
        expected_status=201
    )

    if not success1:
        print(f"   First send failed: {result1}")
        return False

    first_id = result1.get("id")
    print(f"   First measurement sent with ID: {first_id}")

    url = f"{BASE_URL}/api/v1/measurements/"
    headers = {}
    if device_token:
        headers["Authorization"] = f"Bearer {device_token}"
    headers["Content-Type"] = "application/json"
    resp = requests.post(url, json=measurement_data, headers=headers)
    if resp.status_code < 200 or resp.status_code >= 300:
        print(f"   Second send failed: HTTP {resp.status_code}: {resp.text}")
        return False
    try:
        resp_data = resp.json()
    except ValueError:
        print(f"   Second send response is not JSON: {resp.text}")
        return False
    second_id = resp_data.get("id")
    if second_id is None:
        print(f"   Second send response missing ID: {resp_data}")
        return False
    print(f"   Second measurement sent with ID: {second_id}")

    if first_id == second_id:
        print("   Same ID returned - idempotency working correctly")
        return True
    else:
        print("   Different IDs returned - idempotency not working")
        return False

def main():
    print("=" * 60)
    print("E2E CHECKS FOR ANALIZATOR DESZCZÓWEK (AD)")
    print("=" * 60)

    all_passed = True

    try:
        print(f"\nChecking backend at {BASE_URL}...")
        for i in range(15):
            success, _ = make_request("GET", "/health")
            if success:
                print("Backend is healthy!")
                break
            time.sleep(2)
        else:
            print("Backend is unavailable; start it using the project run instructions")
            return False

        user_token, user_email = test_user_registration()
        if not user_token:
            all_passed = False
            print("❌ User registration failed")
        else:
            print("✅ User registration successful")

        login_token = test_user_login(user_email, TEST_PASSWORD)
        if not login_token:
            all_passed = False
            print("❌ User login failed")
        else:
            print("✅ User login successful")

        device_id = f"e2e-device-{time.time_ns()}"
        internal_id, _ = test_device_registration(
            login_token,
            device_id,
            "E2E Test Device"
        )
        if not internal_id:
            all_passed = False
            print("❌ Device registration failed")
        else:
            print("✅ Device registration successful")

        pairing_code = test_generate_pairing_code(login_token, device_id)
        if not pairing_code:
            all_passed = False
            print("❌ Pairing code generation failed")
        else:
            print("✅ Pairing code generation successful")

        device_secret = test_pair_device(login_token, device_id, pairing_code)
        if not device_secret:
            all_passed = False
            print("❌ Device pairing failed")
        else:
            print("✅ Device pairing successful")

        device_token = test_device_authentication(device_id, device_secret)
        if not device_token:
            all_passed = False
            print("❌ Device authentication failed")
        else:
            print("✅ Device authentication successful")

        if not test_heartbeat(device_token, device_id):
            all_passed = False
            print("❌ Heartbeat failed")
        else:
            print("✅ Heartbeat successful")

        measurement_data = {
            "device_id": device_id,
            "temperature": 22.5,
            "water_quality_turbidity": 0.5,
            "water_quality_ph": 7.2,
            "humidity": 60,
            "raw_data": "{\"test\":\"e2e\"}",
            "measurement_id": f"e2e-{time.time_ns()}"
        }

        measurement_id = test_send_measurement(device_token, measurement_data)
        if not measurement_id:
            all_passed = False
            print("❌ Measurement sending failed")
        else:
            print("✅ Measurement sending successful")

        latest_measurement = test_get_latest_measurement(login_token, device_id)
        if not latest_measurement:
            all_passed = False
            print("❌ Getting latest measurement failed")
        else:
            print("✅ Getting latest measurement successful")

        history = test_get_measurement_history(login_token, device_id)
        if not history:
            all_passed = False
            print("❌ Getting measurement history failed")
        else:
            print("✅ Getting measurement history successful")

        if device_secret and login_token and test_offline_queue_and_recovery(device_id, device_secret, login_token):
            print("✅ Agent queue recovery and backend sync successful")
        else:
            all_passed = False
            print("❌ Agent queue recovery and backend sync failed")

        if not test_idempotency_same_measurement_id():
            all_passed = False
            print("❌ Idempotency test failed")
        else:
            print("✅ Idempotency test successful")

    except Exception as e:
        print(f"\n❌ Unexpected error during E2E test: {e}")
        all_passed = False
    finally:
        print("\nE2E verification finished; backend services remain running.")

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All E2E checks passed.")
        print("✅ User registration")
        print("✅ Login")
        print("✅ Device registration")
        print("✅ Pairing")
        print("✅ Device authentication")
        print("✅ Heartbeat")
        print("✅ Measurement creation and ingestion")
        print("✅ Raspberry Pi agent queue and API client")
        print("✅ Backend history contains the saved measurements")
        print("✅ Latest measurement retrieval")
        print("✅ Measurement history retrieval")
        print("✅ Unavailable backend → agent SQLite queue → retry")
        print("✅ Agent queue is empty after confirmed sync")
        print("✅ API failure increments retry count")
        print("✅ Duplicate measurement requests return the same record ID")
    else:
        print("❌ SOME E2E TESTS FAILED! Please check the logs above.")
    print("=" * 60)

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
