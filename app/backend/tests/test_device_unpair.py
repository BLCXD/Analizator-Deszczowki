import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_device_unpair_flow():
    print("=== Starting device unpair flow test ===")

    timestamp = time.time_ns()
    email = f"unpair_user_{timestamp}@example.com"
    reg_response = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "testpassword123",
    })
    assert reg_response.status_code == 200, f"Registration failed: {reg_response.text}"
    token = reg_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    device_id = f"unpair-device-{timestamp}"
    create_response = client.post("/api/v1/devices/", json={
        "device_id": device_id,
        "name": "Unpair Test Device",
    }, headers=headers)
    assert create_response.status_code == 201, f"Create device failed: {create_response.text}"

    code_response = client.post(f"/api/v1/devices/{device_id}/code", headers=headers)
    assert code_response.status_code == 200, f"Generate code failed: {code_response.text}"
    pairing_code = code_response.json()["device_code"]

    pair_response = client.post("/api/v1/devices/pair", json={
        "device_id": device_id,
        "device_code": pairing_code,
    }, headers=headers)
    assert pair_response.status_code == 200, f"Pair failed: {pair_response.text}"
    device_secret = pair_response.json()["device_secret"]

    # Zaszyfrowany secret jest w bazie, device_code jest None.
    device_get = client.get(f"/api/v1/devices/{device_id}", headers=headers)
    assert device_get.status_code == 200
    assert device_get.json().get("device_code") is None

    # Uwierzytelnienie urządzenia działa przed unpair.
    auth_before = client.post("/api/v1/auth/device/login", json={
        "device_id": device_id,
        "device_secret": device_secret,
    })
    assert auth_before.status_code == 200

    # Odłącz urządzenie.
    unpair_response = client.post(f"/api/v1/devices/{device_id}/unpair", headers=headers)
    assert unpair_response.status_code == 200, f"Unpair failed: {unpair_response.text}"
    assert unpair_response.json()["detail"] == "Device unpaired"

    # Po unpair: urządzenie nadal należy do użytkownika, ale straciło dane uwierzytelniające.
    device_get = client.get(f"/api/v1/devices/{device_id}", headers=headers)
    assert device_get.status_code == 200
    paired = device_get.json()
    assert paired["device_code"] is None

    # Uwierzytelnienie urządzenia nie działa już po unpair.
    auth_after = client.post("/api/v1/auth/device/login", json={
        "device_id": device_id,
        "device_secret": device_secret,
    })
    assert auth_after.status_code == 401, f"Device should not auth after unpair: {auth_after.text}"

    # Można wygenerować nowy kod i sparować ponownie (ponowne parowanie).
    code_again = client.post(f"/api/v1/devices/{device_id}/code", headers=headers)
    assert code_again.status_code == 200, f"Regenerate code failed: {code_again.text}"
    new_code = code_again.json()["device_code"]
    pair_again = client.post("/api/v1/devices/pair", json={
        "device_id": device_id,
        "device_code": new_code,
    }, headers=headers)
    assert pair_again.status_code == 200, f"Re-pair failed: {pair_again.text}"
    new_secret = pair_again.json()["device_secret"]

    # Nowy secret działa.
    auth_new = client.post("/api/v1/auth/device/login", json={
        "device_id": device_id,
        "device_secret": new_secret,
    })
    assert auth_new.status_code == 200

    print("=== All device unpair tests passed! ===")


if __name__ == "__main__":
    test_device_unpair_flow()
