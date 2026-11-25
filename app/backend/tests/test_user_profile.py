import time

from fastapi.testclient import TestClient
from app.main import app
from app.db.base import Base
from app.db.session import engine

Base.metadata.create_all(bind=engine)


def test_profile_update_and_password_change():
    client = TestClient(app)
    email = f"profile_{time.time_ns()}@example.com"
    password = "profile-password-123"
    token = client.post("/api/v1/auth/register", json={"email": email, "password": password}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch("/api/v1/auth/me", headers=headers, json={
        "first_name": " Anna ", "last_name": " Nowak ", "phone": "+48 123", 
    })
    assert response.status_code == 200
    assert response.json()["first_name"] == "Anna"
    assert client.get("/api/v1/auth/me", headers=headers).json()["phone"] == "+48 123"

    bad_password = client.patch("/api/v1/auth/me", headers=headers, json={
        "first_name": "Anna", "last_name": "Nowak", "phone": "+48 123",
        "current_password": "wrong-password", "new_password": "new-profile-password-123",
    })
    assert bad_password.status_code == 400

    changed = client.patch("/api/v1/auth/me", headers=headers, json={
        "first_name": "Anna", "last_name": "Nowak", "phone": "+48 123",
        "current_password": password, "new_password": "new-profile-password-123",
    })
    assert changed.status_code == 200
    assert client.post("/api/v1/auth/login", data={"username": email, "password": "new-profile-password-123"}).status_code == 200
