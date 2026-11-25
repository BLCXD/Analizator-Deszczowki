                      

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_measurement_endpoints():
    print("=== Starting final verification of measurement endpoints ===")

    print("\n1. Registering user...")
    register_response = client.post("/api/v1/auth/register", json={
        "email": "verify_test@example.com",
        "password": "verifytest123"
    })
    assert register_response.status_code == 200, f"Registration failed: {register_response.text}"
    token = register_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"   User registered, token received: {token[:10]}...")

    print("\n2. Creating device...")
    device_response = client.post("/api/v1/devices/", json={
        "device_id": "verify-device-001",
        "name": "Verification Device"
    }, headers=headers)
    assert device_response.status_code == 201, f"Create device failed: {device_response.text}"
    device = device_response.json()
    device_id = device["device_id"]
    internal_device_id = device["id"]
    print(f"   Device created: {device_id} (internal ID: {internal_device_id})")

    print("\n3. Creating measurement...")
    measurement_data = {
        "device_id": device_id,
        "water_quality_turbidity": 1.8,
        "water_quality_ph": 6.8,
        "temperature": 18.5,
        "humidity": 70.0,
        "raw_data": '{"sensor_id": "XYZ789"}'
    }
    measurement_response = client.post("/api/v1/measurements/", json=measurement_data, headers=headers)
    assert measurement_response.status_code == 201, f"Create measurement failed: {measurement_response.text}"
    measurement = measurement_response.json()
    measurement_id = measurement["id"]
    print(f"   Measurement created: ID {measurement_id}")
    print(f"   Turbidity: {measurement['water_quality_turbidity']} NTU")
    print(f"   pH: {measurement['water_quality_ph']}")
    print(f"   Temperature: {measurement['temperature']}°C")
    print(f"   Humidity: {measurement['humidity']}%")
    print(f"   Raw data: {measurement['raw_data']}")
    print(f"   Is processed: {measurement['is_processed']}")

    print("\n4. Retrieving measurements for device...")
    get_response = client.get(f"/api/v1/measurements/{device_id}", headers=headers)
    assert get_response.status_code == 200, f"Get measurements failed: {get_response.text}"
    measurements = get_response.json()
    assert len(measurements) >= 1, "Expected at least one measurement"
    found = any(m["id"] == measurement_id for m in measurements)
    assert found, "Created measurement not found in list"
    print(f"   Found {len(measurements)} measurement(s) for device")

    print("\n5. Getting latest measurement...")
    latest_response = client.get(f"/api/v1/measurements/{device_id}/latest", headers=headers)
    assert latest_response.status_code == 200, f"Get latest measurement failed: {latest_response.text}"
    latest = latest_response.json()
    assert latest["id"] == measurement_id, "Latest measurement does not match created measurement"
    print(f"   Latest measurement ID: {latest['id']}")

    print("\n6. Marking measurement as processed...")
    process_response = client.post("/api/v1/measurements/process", json=[measurement_id], headers=headers)
    assert process_response.status_code == 200, f"Mark as processed failed: {process_response.text}"
    process_result = process_response.json()
    assert process_result["processed_count"] == 1, f"Expected 1 processed, got {process_result['processed_count']}"
    print(f"   Marked {process_result['processed_count']} measurement(s) as processed")

    print("\n7. Verifying measurement is processed...")
    verify_response = client.get(f"/api/v1/measurements/{device_id}", headers=headers)
    assert verify_response.status_code == 200, f"Get measurements after processing failed: {verify_response.text}"
    measurements_after = verify_response.json()
    for m in measurements_after:
        if m["id"] == measurement_id:
            assert m["is_processed"] == True, "Measurement not marked as processed"
            print(f"   Measurement {m['id']} is now processed: {m['is_processed']}")
            break
    else:
        assert False, "Measurement not found in list after processing"

    print("\n=== All measurement endpoint tests passed! ===")
    print("✅ Measurement table and API are working correctly.")

if __name__ == "__main__":
    test_measurement_endpoints()