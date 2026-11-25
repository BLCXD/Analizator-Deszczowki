                      

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

import uuid

def test_auth_flow():
                                                                        

    unique_id = uuid.uuid4().hex[:8]
    email = f"flowtest_{unique_id}@example.com"
    print(f"Using email: {email}")

    print("Step 1: Registering user...")
    register_data = {
        "email": email,
        "password": "securepassword123"
    }
    register_response = client.post("/api/v1/auth/register", json=register_data)
    print(f"Register response status: {register_response.status_code}")
    print(f"Register response body: {register_response.json()}")

    assert register_response.status_code == 200, f"Registration failed: {register_response.text}"
    register_data_response = register_response.json()
    assert "access_token" in register_data_response
    token = register_data_response["access_token"]
    print(f"Received token: {token[:20]}...")

    print("\nStep 2: Logging in...")
    login_data = {
        "username": email,
        "password": "securepassword123"
    }
    login_response = client.post("/api/v1/auth/login", data=login_data)
    print(f"Login response status: {login_response.status_code}")
    print(f"Login response body: {login_response.json()}")

    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    login_data_response = login_response.json()
    assert "access_token" in login_data_response
    login_token = login_data_response["access_token"]
    print(f"Received login token: {login_token[:20]}...")


    print("\nStep 3: Accessing /auth/me with JWT...")
    headers = {"Authorization": f"Bearer {login_token}"}
    me_response = client.get("/api/v1/auth/me", headers=headers)
    print(f"/auth/me response status: {me_response.status_code}")
    print(f"/auth/me response body: {me_response.json()}")

    assert me_response.status_code == 200, f"/auth/me failed: {me_response.text}"
    me_data = me_response.json()
    assert "id" in me_data
    assert "email" in me_data
    assert me_data["email"] == email
    assert me_data["is_active"] == True
    print(f"User info: ID={me_data['id']}, Email={me_data['email']}, Active={me_data['is_active']}")

    print("\nStep 4: Testing invalid token...")
    invalid_headers = {"Authorization": "Bearer invalidtoken"}
    invalid_response = client.get("/api/v1/auth/me", headers=invalid_headers)
    print(f"Invalid token response status: {invalid_response.status_code}")
    assert invalid_response.status_code == 401, f"Should return 401 for invalid token: {invalid_response.text}"

    print("\nStep 5: Testing missing token...")
    no_token_response = client.get("/api/v1/auth/me")
    print(f"No token response status: {no_token_response.status_code}")
    assert no_token_response.status_code == 401, f"Should return 401 for missing token: {no_token_response.text}"

    print("\n✅ All auth flow tests passed!")

if __name__ == "__main__":
    test_auth_flow()