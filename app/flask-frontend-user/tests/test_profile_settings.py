from unittest.mock import Mock, patch

from app import app


def test_profile_displays_backend_data_and_submits_profile_update():
    client = app.test_client()
    with client.session_transaction() as session:
        session.update(authenticated=True, access_token="profile-token", username="person@example.test")

    with patch("app.controllers.settings.requests.get", return_value=Mock(
        status_code=200, json=lambda: {
            "email": "person@example.test", "first_name": "Ada", "last_name": "Nowak", "phone": "+48 123",
        }, raise_for_status=lambda: None,
    )):
        page = client.get("/settings/profile")
    assert page.status_code == 200
    assert b'class="settings-form"' not in page.data
    assert b'value="Ada"' in page.data
    assert b'value="+48 123"' in page.data
    with client.session_transaction() as session:
        csrf = session["_csrf_token"]

    with patch("app.controllers.settings.requests.patch", return_value=Mock(
        status_code=200, json=lambda: {},
    )) as backend_patch:
        response = client.post("/settings/profile", data={
            "csrf_token": csrf, "first_name": "Ada", "last_name": "Nowak", "phone": "+48 999",
            "current_password": "old-password", "new_password": "new-password-123",
            "confirm_password": "new-password-123",
        })
    assert response.status_code == 302
    assert backend_patch.call_args.kwargs["json"] == {
        "first_name": "Ada", "last_name": "Nowak", "phone": "+48 999",
        "current_password": "old-password", "new_password": "new-password-123",
    }
