from fastapi.testclient import TestClient

from app.main import app
from app.db.session import SessionLocal
from app.models.user import User
from app.db.base import Base
from app.db.session import engine
from app.models import device, measurement, password_reset, push_subscription

Base.metadata.create_all(bind=engine)


def test_admin_can_manage_global_devices_and_users(monkeypatch):
    client = TestClient(app)
    admin_token = client.post("/api/v1/auth/register", json={"email": "admin-test@example.com", "password": "admin-password-long"})
    db = SessionLocal()
    admin = db.query(User).filter_by(email="admin-test@example.com").first()
    admin.is_admin = True
    db.commit()
    db.close()
    admin_token = client.post("/api/v1/auth/login", data={"username": "admin-test@example.com", "password": "admin-password-long"})
    assert admin_token.status_code == 200
    headers = {"Authorization": f"Bearer {admin_token.json()['access_token']}"}

    normal = client.post("/api/v1/auth/register", json={"email": "normal-admin-test@example.com", "password": "normal-password-long"})
    normal_headers = {"Authorization": f"Bearer {normal.json()['access_token']}"}
    assert client.get("/api/v1/admin/users", headers=normal_headers).status_code == 403

    device_id = "admin-managed-device"
    with SessionLocal() as db:
        owner = db.query(User).filter_by(email="normal-admin-test@example.com").first()
        owner_id = owner.id
        from app.models.device import Device
        db.add(Device(device_id=device_id, name="Owned device", user_id=owner.id))
        db.commit()
    listed = client.get("/api/v1/admin/devices", headers=headers)
    assert listed.status_code == 200 and any(row["device_id"] == device_id for row in listed.json())
    assert client.put(f"/api/v1/admin/devices/{device_id}", json={"name": "Updated globally"}, headers=headers).json()["name"] == "Updated globally"
    assert client.patch(f"/api/v1/admin/users/{owner_id}/active", params={"is_active": "false"}, headers=headers).json()["is_active"] is False
    assert client.delete(f"/api/v1/admin/devices/{device_id}", headers=headers).status_code == 204


def test_admin_lists_user_devices_and_deletes_user_without_deleting_devices():
    client = TestClient(app)
    admin = client.post("/api/v1/auth/register", json={"email": "admin-delete@example.com", "password": "admin-password-long"})
    with SessionLocal() as db:
        admin_user = db.query(User).filter_by(email="admin-delete@example.com").one()
        admin_user.is_admin = True
        db.commit()
        admin_id = admin_user.id
    admin = client.post("/api/v1/auth/login", data={"username": "admin-delete@example.com", "password": "admin-password-long"})
    headers = {"Authorization": f"Bearer {admin.json()['access_token']}"}
    client.post("/api/v1/auth/register", json={"email": "user-delete@example.com", "password": "user-password-long"})
    with SessionLocal() as db:
        user_id = db.query(User).filter_by(email="user-delete@example.com").one().id
        owner_device = device.Device(device_id="user-delete-device", name="Keep device", user_id=user_id)
        db.add(owner_device)
        db.commit()

    devices = client.get(f"/api/v1/admin/users/{user_id}/devices", headers=headers)
    assert devices.status_code == 200
    assert [row["device_id"] for row in devices.json()] == ["user-delete-device"]
    assert client.delete(f"/api/v1/admin/users/{admin_id}", headers=headers).status_code == 400
    assert client.delete(f"/api/v1/admin/users/{user_id}", headers=headers).status_code == 204
    with SessionLocal() as db:
        assert db.query(User).filter_by(id=user_id).first() is None
        retained = db.query(device.Device).filter_by(device_id="user-delete-device").one()
        assert retained.user_id is None
