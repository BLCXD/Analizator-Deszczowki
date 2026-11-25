import tempfile

from app.core.rate_limit import RateLimiter, request_bucket


def test_rate_limit_shared_and_expires():
    with tempfile.TemporaryDirectory() as directory:
        path = f'{directory}/limits.sqlite'
        first_worker = RateLimiter(path)
        second_worker = RateLimiter(path)
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


if __name__ == "__main__":
    test_rate_limit_shared_and_expires()
    test_rate_limit_bucket_does_not_store_client_address()
    print("All rate limit tests passed!")
