import sys
import os
import time
modules_to_remove = [m for m in sys.modules if m.startswith('app')]
for m in modules_to_remove:
    del sys.modules[m]

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from app.main import app

from app.db.base import Base
from app.db.session import engine
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_measurement_crud():
    timestamp = int(time.time())
    user_email = f"measurement_test_{timestamp}@example.com"
    user_password = "testpassword"
    reg_response = client.post("/api/v1/auth/register", json={"email": user_email, "password": user_password})
    assert reg_response.status_code == 200, f"Registration failed: {reg_response.text}"
    token = reg_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    device_data = {
        "device_id": f"test-measurement-device-{timestamp}-001",
        "name": "Test Measurement Device"
    }
    device_response = client.post("/api/v1/devices/", json=device_data, headers=headers)
    assert device_response.status_code == 201, f"Create device failed: {device_response.text}"
    device = device_response.json()
    device_id = device["device_id"]
    internal_device_id = device["id"]

    measurement_data = {
        "device_id": device_id,
        "measurement_id": f"measurement-{timestamp}-001",
        "water_quality_turbidity": 2.3,
        "ec": 780.0,
        "water_quality_ph": 7.2,
        "temperature": 20.1,
        "humidity": 65.0,
        "rainfall_mm": 12.6,
        "rainfall_1h_mm": 0.28,
        "raw_data": '{"sensor_id": "ABC123"}'
    }

    response = client.post("/api/v1/measurements/", json=measurement_data, headers=headers)
    assert response.status_code == 201, f"Create measurement failed: {response.text}"
    measurement = response.json()
    assert measurement["device_id"] == device_id
    assert measurement["water_quality_turbidity"] == measurement_data["water_quality_turbidity"]
    assert measurement["ec"] == measurement_data["ec"]
    assert measurement["rainfall_mm"] == measurement_data["rainfall_mm"]
    assert measurement["rainfall_1h_mm"] == measurement_data["rainfall_1h_mm"]
    assert "water_level" not in measurement
    assert measurement["water_quality_ph"] == measurement_data["water_quality_ph"]
    assert measurement["temperature"] == measurement_data["temperature"]
    assert measurement["humidity"] == measurement_data["humidity"]
    assert measurement["raw_data"] == measurement_data["raw_data"]
    assert "id" in measurement
    assert "measurement_time" in measurement
    assert measurement["is_processed"] == False
    measurement_id = measurement["id"]

    retry_response = client.post("/api/v1/measurements/", json=measurement_data, headers=headers)
    assert retry_response.status_code == 200
    assert retry_response.json()["id"] == measurement_id

    response = client.get(f"/api/v1/measurements/{device_id}", headers=headers)
    assert response.status_code == 200, f"Get measurements failed: {response.text}"
    measurements = response.json()
    assert len(measurements) >= 1
    measurement_ids = [m["id"] for m in measurements]
    assert measurement_id in measurement_ids

    response = client.get(f"/api/v1/measurements/{device_id}/latest", headers=headers)
    assert response.status_code == 200, f"Get latest measurement failed: {response.text}"
    latest_measurement = response.json()
    assert latest_measurement["id"] == measurement_id

    trends = client.get(f"/api/v1/measurements/{device_id}/analysis/trends", headers=headers)
    assert trends.status_code == 200, trends.text
    anomalies = client.get(f"/api/v1/measurements/{device_id}/analysis/anomalies", headers=headers)
    assert anomalies.status_code == 200, anomalies.text

    from datetime import datetime, timedelta
    from datetime import timezone
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    response = client.get(
        f"/api/v1/measurements/{device_id}",
        params={"start_time": one_hour_ago.isoformat()},
        headers=headers,
    )
    assert response.status_code == 200, f"Get measurements since failed: {response.text}"
    measurements_since = response.json()
    assert len(measurements_since) >= 1

    print("All measurement tests passed!")

if __name__ == "__main__":
    test_measurement_crud()
