import hashlib
import hmac
import os

from fastapi.testclient import TestClient
from app.main import app
from app.models.device import Device
from app.db.session import SessionLocal


def test_claim_is_authenticated_secret_once_and_atomically_available():
    client = TestClient(app)
    credentials = {"email": "hub-claim@example.com", "password": "secret-password"}
    response = client.post("/api/v1/auth/register", json=credentials)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    device_id = "hub-claim-test-001"
    with SessionLocal() as db:
        db.add(Device(device_id=device_id, name="ADE Hub", user_id=None))
        db.commit()
    key = os.environ["DEVICE_CLAIM_KEY"]
    proof = hmac.new(key.encode(), device_id.encode(), hashlib.sha256).hexdigest()
    claimed = client.post("/api/v1/devices/claim", json={"device_id": device_id, "claim_proof": proof}, headers={**headers, "X-Device-Claim-Proof": proof})
    assert claimed.status_code == 201
    secret = claimed.json()["device_secret"]
    assert len(secret) >= 32
    assert client.post("/api/v1/devices/claim", json={"device_id": device_id, "claim_proof": proof}, headers={**headers, "X-Device-Claim-Proof": proof}).status_code == 409
    assert client.post("/api/v1/auth/device/login", json={"device_id": device_id, "device_secret": secret}).status_code == 200
    assert client.post("/api/v1/devices/claim", json={"device_id": device_id, "claim_proof": "x" * 64}, headers={**headers, "X-Device-Claim-Proof": "x" * 64}).status_code == 403
