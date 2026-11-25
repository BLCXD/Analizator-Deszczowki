import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_device_pairing_flow():
\
\
\
       
    print("=== Starting device pairing flow test ===")

    print("\n1. Registering user1...")
    import time
    timestamp1 = time.time_ns()
    user1_email = f"user1_{timestamp1}@example.com"
    user1_password = "testpassword123"
    reg_response = client.post("/api/v1/auth/register", json={
        "email": user1_email,
        "password": user1_password
    })
    assert reg_response.status_code == 200, f"User1 registration failed: {reg_response.text}"
    user1_token = reg_response.json()["access_token"]
    user1_headers = {"Authorization": f"Bearer {user1_token}"}
    print(f"   User1 registered: {user1_email}")

    print("\n2. Registering user2...")
    timestamp2 = int(time.time()) + 1000
    user2_email = f"user2_{timestamp2}@example.com"
    user2_password = "testpassword456"
    reg_response2 = client.post("/api/v1/auth/register", json={
        "email": user2_email,
        "password": user2_password
    })
    assert reg_response2.status_code == 200, f"User2 registration failed: {reg_response2.text}"
    user2_token = reg_response2.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}
    print(f"   User2 registered: {user2_email}")

    print("\n3. User1 creating device...")
    device_data = {
        "device_id": f"test-device-{timestamp1}-001",
        "name": "Test Sensor Device"
    }
    create_response = client.post("/api/v1/devices/", json=device_data, headers=user1_headers)
    assert create_response.status_code == 201, f"Create device failed: {create_response.text}"
    device = create_response.json()
    device_id = device["device_id"]
    internal_device_id = device["id"]
    print(f"   Device created: {device_id} (internal ID: {internal_device_id})")

    assert "device_code" not in device or device.get("device_code") is None, "New device should not have a pairing code yet"

    print("\n4. User1 generating pairing code...")
    code_response = client.post(f"/api/v1/devices/{device_id}/code", headers=user1_headers)
    assert code_response.status_code == 200, f"Generate pairing code failed: {code_response.text}"
    code_data = code_response.json()
    pairing_code = code_data["device_code"]
    assert pairing_code is not None and len(pairing_code) > 0, "Pairing code should be generated"
    print("   One-time pairing code generated.")

    id_only_auth = client.post("/api/v1/auth/device/login", json={"device_id": device_id})
    assert id_only_auth.status_code == 422

    print("\n5. Testing that code cannot be regenerated before use...")
    try_again_response = client.post(f"/api/v1/devices/{device_id}/code", headers=user1_headers)
    assert try_again_response.status_code == 400, f"Should fail to regenerate code: {try_again_response.text}"
    print("   Correctly prevented regenerating code before use")

    print("\n6. Testing pairing with wrong code...")
    wrong_pair_data = {
        "device_id": device_id,
        "device_code": "WRONGCODE"
    }
    wrong_pair_response = client.post("/api/v1/devices/pair", json=wrong_pair_data, headers=user1_headers)
    assert wrong_pair_response.status_code == 400, f"Should fail with wrong code: {wrong_pair_response.text}"
    print("   Correctly rejected wrong pairing code")

    print("\n7. Testing that user2 cannot pair user1's device...")
    pair_data_user2 = {
        "device_id": device_id,
        "device_code": pairing_code
    }
    pair_response_user2 = client.post("/api/v1/devices/pair", json=pair_data_user2, headers=user2_headers)
    assert pair_response_user2.status_code == 400, f"User2 should not be able to pair user1's device: {pair_response_user2.text}"
    print("   Correctly prevented user2 from pairing user1's device")

    print("\n8. User1 pairing device...")
    pair_data_user1 = {
        "device_id": device_id,
        "device_code": pairing_code
    }
    pair_response = client.post("/api/v1/devices/pair", json=pair_data_user1, headers=user1_headers)
    assert pair_response.status_code == 200, f"Pair device failed: {pair_response.text}"
    pair_result = pair_response.json()
    device_secret = pair_result["device_secret"]
    assert device_secret is not None and len(device_secret) > 0, "Device secret should be returned after pairing"
    print("   Device paired successfully; the secret is not logged.")

    id_only_auth = client.post("/api/v1/auth/device/login", json={"device_id": device_id})
    assert id_only_auth.status_code == 422
    wrong_secret_auth = client.post("/api/v1/auth/device/login", json={
        "device_id": device_id,
        "device_secret": "x" * 32,
    })
    assert wrong_secret_auth.status_code == 401

    print("\n8. Verifying device ownership after pairing...")
    get_device_response = client.get(f"/api/v1/devices/{device_id}", headers=user1_headers)
    assert get_device_response.status_code == 200, f"Get device failed: {get_device_response.text}"
    paired_device = get_device_response.json()
    assert paired_device["id"] == internal_device_id, "Device ID mismatch"
    assert paired_device["device_id"] == device_id, "External device ID mismatch"
    assert "device_code" not in paired_device or paired_device.get("device_code") is None, "Paired device should not have device_code"
    assert "device_secret_hash" not in paired_device, "device_secret_hash should not be in response"
    print(f"   Device verified as paired to user1: {paired_device['device_id']}")

    print("\n9. Testing that paired device cannot generate new code...")
    try_code_again_response = client.post(f"/api/v1/devices/{device_id}/code", headers=user1_headers)
    assert try_code_again_response.status_code == 400, f"Should fail to generate code for already paired device: {try_code_again_response.text}"
    print("   Correctly prevented generating code for already paired device")

    print("\n10. Testing device authentication...")
    auth_data = {
        "device_id": device_id,
        "device_secret": device_secret
    }
    auth_response = client.post("/api/v1/auth/device/login", json=auth_data)
    assert auth_response.status_code == 200, f"Device authentication failed: {auth_response.text}"
    auth_result = auth_response.json()
    device_access_token = auth_result["access_token"]
    assert device_access_token is not None and len(device_access_token) > 0, "Device should receive access token"
    print("   Device authenticated successfully; token is not logged.")

    print("\n11. Testing device can access measurement endpoints...")
    measurement_data = {
        "measurement_id": f"pairing-{timestamp1}",
        "device_id": device_id,
        "water_quality_turbidity": 2.3,
        "water_quality_ph": 7.2,
        "temperature": 20.1,
        "humidity": 65.0,
        "raw_data": '{"test": "data"}'
    }
    meas_response = client.post("/api/v1/measurements/", json=measurement_data, headers=user1_headers)
    assert meas_response.status_code == 201, f"Create measurement failed: {meas_response.text}"

    device_headers = {"Authorization": f"Bearer {device_access_token}"}
    get_meas_response = client.get(f"/api/v1/measurements/{device_id}", headers=device_headers)
    assert get_meas_response.status_code == 200, f"Device should be able to get measurements: {get_meas_response.text}"
    measurements = get_meas_response.json()
    assert len(measurements) >= 1, "Device should see its measurements"
    print(f"   Device can access measurements: found {len(measurements)} measurement(s)")

    assert client.get("/api/v1/devices/", headers=device_headers).status_code == 403
    assert client.get("/api/v1/measurements/", headers=device_headers).status_code == 403
    assert client.get("/api/v1/auth/me", headers=device_headers).status_code == 403
    assert client.delete("/api/v1/auth/me", headers=device_headers).status_code == 403

    user2_measurements = client.get("/api/v1/measurements/", headers=user2_headers)
    assert user2_measurements.status_code == 200
    assert user2_measurements.json() == []

    user2_device = client.post("/api/v1/devices/", json={
        "device_id": f"user2-device-{timestamp1}",
        "name": "User 2 sensor",
    }, headers=user2_headers)
    assert user2_device.status_code == 201
    collision = dict(measurement_data, device_id=user2_device.json()["device_id"])
    collision_response = client.post("/api/v1/measurements/", json=collision, headers=user2_headers)
    assert collision_response.status_code == 409

    print("\n12. Testing that user2 still cannot access paired device...")
    user2_get_response = client.get(f"/api/v1/devices/{device_id}", headers=user2_headers)
    assert user2_get_response.status_code == 404, f"User2 should not be able to access user1's device: {user2_get_response.text}"
    print("   Correctly prevented user2 from accessing user1's device")

    print("\n13. Testing that user2 cannot pair already paired device...")
    pair_attempt2_response = client.post("/api/v1/devices/pair", json=pair_data_user2, headers=user2_headers)
    assert pair_attempt2_response.status_code == 400, f"User2 should not be able to pair already paired device: {pair_attempt2_response.text}"
    print("   Correctly prevented user2 from pairing already paired device")

    print("\n=== All device pairing tests passed! ===")
    print("✅ Device pairing flow working correctly:")
    print("   - Users can create devices")
    print("   - Unpaired devices can generate one-time pairing codes")
    print("   - Pairing codes can be used to associate devices with users")
    print("   - Device ownership is protected (other users cannot take over devices)")
    print("   - Paired devices cannot generate new pairing codes")
    print("   - Devices can authenticate using their secret")
    print("   - Authenticated devices can access their own measurement data")
    print("   - Pairing codes are single-use")
    print("   - Device secrets are only shown once after pairing")

if __name__ == "__main__":
    test_device_pairing_flow()
