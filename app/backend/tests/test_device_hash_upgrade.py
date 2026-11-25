import hashlib
import hmac
import secrets

from fastapi.testclient import TestClient

from app.core.config import DEVICE_SECRET_SALT
from app.db.session import SessionLocal
from app.main import app
from app.models.device import Device


client = TestClient(app)


def test_unsalted_device_secret_hash_upgrades_after_valid_authentication():
    email = f'device-hash-{secrets.token_hex(6)}@example.com'
    user = client.post('/api/v1/auth/register', json={
        'email': email, 'password': 'Device-Owner-Password-2026',
    })
    assert user.status_code == 200
    headers = {'Authorization': f"Bearer {user.json()['access_token']}"}
    device_id = f'device-{secrets.token_hex(8)}'
    assert client.post('/api/v1/devices/', json={
        'device_id': device_id, 'name': 'Hash migration test',
    }, headers=headers).status_code == 201
    code = client.post(f'/api/v1/devices/{device_id}/code', headers=headers)
    paired = client.post('/api/v1/devices/pair', json={
        'device_id': device_id, 'device_code': code.json()['device_code'],
    }, headers=headers)
    assert paired.status_code == 200
    secret = paired.json()['device_secret']

    with SessionLocal() as db:
        device = db.query(Device).filter_by(device_id=device_id).one()
        device.device_secret_hash = hashlib.sha256(secret.encode()).hexdigest()
        db.commit()

    login = client.post('/api/v1/auth/device/login', json={
        'device_id': device_id, 'device_secret': secret,
    })
    assert login.status_code == 200
    expected = hmac.new(DEVICE_SECRET_SALT.encode(), secret.encode(), hashlib.sha256).hexdigest()
    with SessionLocal() as db:
        assert db.query(Device).filter_by(device_id=device_id).one().device_secret_hash == expected
