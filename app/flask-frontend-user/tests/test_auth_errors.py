import tempfile
from unittest.mock import patch, MagicMock

import requests
from app import create_app


def _fake_response(status_code, json_data=None):
    response = MagicMock()
    response.status_code = status_code
    response.headers.get.return_value = 'application/json'
    response.json.return_value = json_data or {}
    return response


def _login_body(client):
                                                                                 
    client.get('/auth/login')
    with client.session_transaction() as sess:
        token = sess.get('_csrf_token', '')
    return client.post('/auth/login', data={
        'username': 'u@example.com', 'password': 'x', 'csrf_token': token,
    })


def test_wrong_credentials_shows_generic_error():
                                                                  
    with tempfile.TemporaryDirectory() as directory:
        app = create_app('testing')
        app.config.update(RATE_LIMIT_DB_PATH=f'{directory}/limits.sqlite')
        client = app.test_client()
        with patch('app.controllers.auth.requests.post') as backend_post:
            backend_post.return_value = _fake_response(
                401, {'detail': 'Incorrect email or password'}
            )
            body = _login_body(client).get_data(as_text=True)

    assert 'Niepoprawny adres e-mail lub hasło' in body, body
    assert 'Incorrect email or password' not in body, body


def test_network_error_shows_connection_error():
                                                                
    with tempfile.TemporaryDirectory() as directory:
        app = create_app('testing')
        app.config.update(RATE_LIMIT_DB_PATH=f'{directory}/limits.sqlite')
        client = app.test_client()
        with patch('app.controllers.auth.requests.post') as backend_post:
            backend_post.side_effect = requests.exceptions.ConnectionError('down')
            body = _login_body(client).get_data(as_text=True)

    assert 'Nie można połączyć się z serwerem' in body, body
