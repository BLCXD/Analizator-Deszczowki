import secrets
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import engine
from app.main import app
from app.models.password_reset import PasswordResetToken
from app.models.user import User
from app.api.v1.auth import _send_password_reset_email


Base.metadata.create_all(bind=engine)
client = TestClient(app)


def test_password_reset_email_is_generic_and_token_is_one_time():
    email = f'reset-{secrets.token_hex(6)}@example.com'
    old_password = 'Initial-Rain-Password-2026'
    new_password = 'New-Rain-Password-2026'
    assert client.post('/api/v1/auth/register', json={
        'email': email, 'password': old_password,
    }).status_code == 200

    with patch('app.api.v1.auth._send_password_reset_email', return_value=True) as send_email:
        response = client.post('/api/v1/auth/password-reset/request', json={'email': email})
    assert response.status_code == 202
    assert response.json() == {'message': 'Jeśli konto istnieje, wysłaliśmy instrukcję resetu hasła.'}
    assert email not in response.text
    assert send_email.call_args.args[0] == email
    token = send_email.call_args.args[1]

    from app.db.session import SessionLocal
    with SessionLocal() as db:
        user = db.query(User).filter_by(email=email).one()
        stored = db.query(PasswordResetToken).filter_by(user_id=user.id).first()
        assert stored is not None
        assert token not in stored.token_hash

    changed = client.post('/api/v1/auth/password-reset/confirm', json={
        'token': token, 'new_password': new_password,
    })
    assert changed.status_code == 200
    assert client.post('/api/v1/auth/password-reset/confirm', json={
        'token': token, 'new_password': 'Another-Rain-Password-2026',
    }).status_code == 400
    assert client.post('/api/v1/auth/login', data={
        'username': email, 'password': old_password,
    }).status_code == 401
    assert client.post('/api/v1/auth/login', data={
        'username': email, 'password': new_password,
    }).status_code == 200


def test_password_reset_request_does_not_reveal_unknown_email():
    response = client.post('/api/v1/auth/password-reset/request', json={
        'email': f'unknown-{secrets.token_hex(6)}@example.com',
    })
    assert response.status_code == 202
    assert response.json() == {'message': 'Jeśli konto istnieje, wysłaliśmy instrukcję resetu hasła.'}


def test_reset_link_uses_fragment_so_proxy_access_logs_never_receive_token():
    with patch.dict('os.environ', {
        'PUBLIC_APP_URL': 'https://ad.example.com',
    }):
        with patch('app.api.v1.auth.notify_user', return_value=True) as send:
            assert _send_password_reset_email('user@example.com', 'one-time-token')
    assert send.call_args.args[0] == 'user@example.com'
    assert 'https://ad.example.com/auth/password-reset/confirm#token=one-time-token' == send.call_args.kwargs['action'][1]


def test_reset_email_accepts_app_url_alias():
    with patch.dict('os.environ', {'PUBLIC_APP_URL': '', 'APP_URL': 'https://ad.example.net'}):
        with patch('app.api.v1.auth.notify_user', return_value=True) as send:
            assert _send_password_reset_email('user@example.com', 'one-time-token')
    assert 'https://ad.example.net/auth/password-reset/confirm#token=one-time-token' == send.call_args.kwargs['action'][1]
