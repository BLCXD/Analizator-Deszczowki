import secrets
from fastapi.testclient import TestClient
from app.main import app


def test_measurement_stream_requires_scoped_ticket_and_delivers_events():
    client = TestClient(app)
    email = f"stream-{secrets.token_hex(4)}@example.com"
    response = client.post("/api/v1/auth/register", json={"email": email, "password": "Rainwater-Test-2026"})
    assert response.status_code == 200
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    device_id = f"stream-device-{secrets.token_hex(4)}"
    created = client.post("/api/v1/devices/", json={"device_id": device_id, "name": "Stream test"}, headers=headers)
    assert created.status_code == 201

    assert client.get(f"/api/v1/devices/{device_id}/stream-ticket").status_code == 401
    ticket_response = client.get(f"/api/v1/devices/{device_id}/stream-ticket", headers=headers)
    assert ticket_response.status_code == 200
    ticket = ticket_response.json()["ticket"]

    with client.websocket_connect(
        f"/api/v1/measurements/ws/{device_id}",
        subprotocols=["ad-stream", f"ticket.{ticket}"],
    ) as websocket:
        measurement = client.post("/api/v1/measurements/", json={
            "measurement_id": f"stream-measurement-{secrets.token_hex(4)}",
            "device_id": device_id,
            "ec": 720,
            "water_quality_turbidity": 1.6,
        }, headers=headers)
        assert measurement.status_code == 201
        event = websocket.receive_json()
        assert event["type"] == "measurement"
        assert event["device_id"] == device_id
        assert event["data"]["ec"] == 720
