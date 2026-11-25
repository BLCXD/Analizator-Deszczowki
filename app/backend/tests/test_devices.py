import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_device_crud():
    import time
    timestamp = time.time_ns()
    user_email = f"device_test_{timestamp}@example.com"
    user_password = "testpassword"
    reg_response = client.post("/api/v1/auth/register", json={"email": user_email, "password": user_password})
    assert reg_response.status_code == 200, f"Registration failed: {reg_response.text}"
    token = reg_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    device_data = {
        "device_id": f"test-device-{timestamp}-001",
        "name": "Test Device"
    }

    response = client.post("/api/v1/devices/", json=device_data, headers=headers)
    assert response.status_code == 201, f"Create device failed: {response.text}"
    device = response.json()
    assert device["device_id"] == device_data["device_id"]
    assert device["name"] == device_data["name"]
    assert device["status"] == "unknown"
    assert "id" in device
    device_id = device["id"]

    response = client.get(f"/api/v1/devices/{device_data['device_id']}", headers=headers)
    assert response.status_code == 200, f"Get device failed: {response.text}"
    device_get = response.json()
    assert device_get["id"] == device_id
    assert device_get["device_id"] == device_data["device_id"]

    response = client.get("/api/v1/devices/", headers=headers)
    assert response.status_code == 200, f"List devices failed: {response.text}"
    devices = response.json()
    assert len(devices) >= 1
    device_ids = [d["id"] for d in devices]
    assert device_id in device_ids

    update_data = {"name": "Updated Test Device"}
    response = client.put(f"/api/v1/devices/{device_data['device_id']}", json=update_data, headers=headers)
    assert response.status_code == 200, f"Update device failed: {response.text}"
    device_updated = response.json()
    assert device_updated["name"] == update_data["name"]

    response = client.post(f"/api/v1/devices/{device_data['device_id']}/heartbeat", headers=headers)
    assert response.status_code == 200, f"Heartbeat failed: {response.text}"
    device_heartbeat = response.json()
    assert device_heartbeat["last_seen"] is not None
    status_response = client.get(f"/api/v1/devices/{device_data['device_id']}/status", headers=headers)
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "online"

    response = client.delete(f"/api/v1/devices/{device_data['device_id']}", headers=headers)
    assert response.status_code == 204, f"Delete device failed: {response.text}"

    response = client.get(f"/api/v1/devices/{device_data['device_id']}", headers=headers)
    assert response.status_code == 404, f"Device still exists after deletion: {response.text}"

    print("All device tests passed!")

if __name__ == "__main__":
    test_device_crud()
