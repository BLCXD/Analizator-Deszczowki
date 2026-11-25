import sys
import os
import time
import secrets
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

def test_register_and_login():
    timestamp = int(time.time())
    email = f"test_{timestamp}@example.com"
    password = "testpassword"

    response = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    print(f"Registration response: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    token = data["access_token"]

    response = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    print(f"Login response: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    token2 = data["access_token"]

    headers = {"Authorization": f"Bearer {token2}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    print(f"/me response: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert data["is_active"] == True

    response = client.post("/api/v1/auth/login", data={"username": email, "password": "wrong"})
    print(f"Wrong password response: {response.status_code}")
    assert response.status_code == 401

    response = client.get("/api/v1/auth/me")
    print(f"/me without token response: {response.status_code}")
    assert response.status_code == 401


def test_delete_own_account():
    timestamp = int(time.time())
    email = f"delete_{timestamp}@example.com"
    password = "deletepassword-123"

    reg_response = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert reg_response.status_code == 200
    token = reg_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete("/api/v1/auth/me", headers=headers)
    print(f"Delete own account response: {response.status_code}")
    assert response.status_code == 204

    # Cannot log in after account deletion
    response = client.post("/api/v1/auth/login", data={"username": email, "password": password})
    print(f"Login after delete response: {response.status_code}")
    assert response.status_code == 401

    # Token no longer grants access to /me
    response = client.get("/api/v1/auth/me", headers=headers)
    print(f"/me after delete response: {response.status_code}")
    assert response.status_code == 401


def test_stream_ticket_cannot_be_used_as_user_access_token():
    client = TestClient(app)
    suffix = secrets.token_hex(4)
    victim_email = f"victim-{suffix}@example.com"
    victim = client.post("/api/v1/auth/register", json={
        "email": victim_email,
        "password": "Rainwater-Test-2026",
    })
    attacker = client.post("/api/v1/auth/register", json={
        "email": f"attacker-{suffix}@example.com",
        "password": "Rainwater-Test-2026",
    })
    assert victim.status_code == attacker.status_code == 200

    attacker_headers = {"Authorization": f"Bearer {attacker.json()['access_token']}"}
    assert client.post("/api/v1/devices/", json={
        "device_id": victim_email,
        "name": "Attacker-owned device",
    }, headers=attacker_headers).status_code == 201
    ticket = client.get(
        f"/api/v1/devices/{victim_email}/stream-ticket",
        headers=attacker_headers,
    )
    assert ticket.status_code == 200

    response = client.get("/api/v1/auth/me", headers={
        "Authorization": f"Bearer {ticket.json()['ticket']}"
    })
    assert response.status_code == 401


if __name__ == "__main__":
    test_register_and_login()
    test_delete_own_account()
    print("All tests passed!")
