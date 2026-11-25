import tempfile
from unittest.mock import patch

from app.rate_limit import SQLiteRateLimiter, request_bucket
from app import create_app


def test_auth_rate_limit_is_shared_and_expires():
    with tempfile.TemporaryDirectory() as directory:
        path = f'{directory}/limits.sqlite'
        first_worker = SQLiteRateLimiter(path)
        second_worker = SQLiteRateLimiter(path)
        bucket = request_bucket('test-secret', '192.0.2.1', 'login')

        assert first_worker.hit(bucket, 2, 60, now=100) == (True, 0)
        assert second_worker.hit(bucket, 2, 60, now=101) == (True, 0)
        assert first_worker.hit(bucket, 2, 60, now=102) == (False, 58)
        assert second_worker.hit(bucket, 2, 60, now=160) == (True, 0)


def test_rate_limit_bucket_does_not_store_client_address():
    one = request_bucket('secret', '192.0.2.1', 'login')
    two = request_bucket('secret', '192.0.2.2', 'login')
    other_route = request_bucket('secret', '192.0.2.1', 'register')

    assert one != two
    assert one != other_route
    assert '192.0.2.1' not in one


def test_login_and_registration_are_throttled_before_backend_calls():
    with tempfile.TemporaryDirectory() as directory:
        app = create_app('testing')
        app.config.update(
            RATE_LIMIT_DB_PATH=f'{directory}/limits.sqlite',
            AUTH_RATE_LIMIT=1,
            AUTH_RATE_WINDOW_SECONDS=300,
        )
        client = app.test_client()
        with patch('app.controllers.auth.requests.post') as backend_post:
            first = client.post('/auth/login', data={})
            second = client.post('/auth/login', data={})
            register = client.post('/auth/register', data={})

        assert first.status_code == 400
        assert second.status_code == 429
        assert int(second.headers['Retry-After']) > 0
        assert register.status_code == 400
        backend_post.assert_not_called()
