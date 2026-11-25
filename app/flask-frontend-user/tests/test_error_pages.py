from app import create_app


def test_browser_404_renders_custom_page_with_status():
    response = create_app('testing').test_client().get('/missing-page', headers={'Accept': 'text/html'})

    assert response.status_code == 404
    assert response.mimetype == 'text/html'
    assert 'Nie znaleziono strony' in response.get_data(as_text=True)


def test_browser_502_renders_custom_page_without_leaking_error():
    app = create_app('testing')

    @app.get('/test-upstream-error')
    def upstream_error():
        from flask import abort
        abort(502, description='private upstream detail')

    response = app.test_client().get('/test-upstream-error', headers={'Accept': 'text/html'})
    body = response.get_data(as_text=True)

    assert response.status_code == 502
    assert response.mimetype == 'text/html'
    assert 'Problem z połączeniem' in body
    assert 'private upstream detail' not in body


def test_unhandled_browser_error_renders_custom_500_without_traceback():
    app = create_app('testing')

    @app.get('/test-unhandled-error')
    def unhandled_error():
        raise RuntimeError('private exception detail')

    response = app.test_client().get('/test-unhandled-error', headers={'Accept': 'text/html'})
    body = response.get_data(as_text=True)

    assert response.status_code == 500
    assert response.mimetype == 'text/html'
    assert 'Coś poszło nie tak' in body
    assert 'private exception detail' not in body


def test_api_errors_remain_json():
    response = create_app('testing').test_client().get('/api/unknown')

    assert response.status_code == 404
    assert response.get_json() == {'error': 'Not found'}


def test_gateway_error_page_is_available_to_caddy_and_frontend():
    response = create_app('testing').test_client().get('/static/error-pages/gateway.html')

    assert response.status_code == 200
    assert 'Serwis chwilowo niedostępny' in response.get_data(as_text=True)
