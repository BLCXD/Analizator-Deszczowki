import os
import tempfile
from unittest.mock import patch

os.environ.setdefault('SECRET_KEY', 'test-only-secret')
os.environ.setdefault('FLASK_ENV', 'testing')

from app import app
from app.services.api_client import APIError


def test_ai_analysis_requires_csrf_and_forwards_authenticated_request():
    client = app.test_client()
    with client.session_transaction() as session:
        session['authenticated'] = True
        session['access_token'] = 'private-user-token'
        session['username'] = 'ai@example.test'
    page = client.get('/analytics/')
    assert page.status_code == 200
    with client.session_transaction() as session:
        csrf = session['analytics_csrf']

    with tempfile.TemporaryDirectory() as directory, patch.dict(app.config, {
        'RATE_LIMIT_DB_PATH': f'{directory}/limits.sqlite',
        'AI_ANALYSIS_RATE_LIMIT': 5,
        'AI_ANALYSIS_RATE_WINDOW_SECONDS': 3600,
    }), patch('app.controllers.analytics.api_client.post', return_value={
        'analysis': 'Stabilny przebieg.', 'measurement_count': 4, 'period_hours': 24,
    }) as backend_post:
        denied = client.post('/analytics/api/ai/device-1?hours=24')
        assert denied.status_code == 400
        assert backend_post.call_count == 0

        response = client.post('/analytics/api/ai/device-1?hours=24', headers={'X-CSRF-Token': csrf})
        assert response.status_code == 200
        assert response.json['analysis'] == 'Stabilny przebieg.'
        backend_post.assert_called_once_with('/api/v1/measurements/device-1/analysis/ai', params={'hours': 24}, timeout=85)


def test_ai_analysis_forwards_weather_coordinates_and_validates_them():
    client = app.test_client()
    with client.session_transaction() as session:
        session['authenticated'] = True
        session['access_token'] = 'private-user-token'
        session['username'] = 'ai-weather@example.test'
    client.get('/analytics/')
    with client.session_transaction() as session:
        csrf = session['analytics_csrf']
    headers = {'X-CSRF-Token': csrf}
    with tempfile.TemporaryDirectory() as directory, patch.dict(app.config, {'RATE_LIMIT_DB_PATH': f'{directory}/limits.sqlite'}),\
            patch('app.controllers.analytics.api_client.post', return_value={'analysis': 'OK'}) as backend_post:
        response = client.post('/analytics/api/ai/device-1?hours=24&latitude=52.2&longitude=21', headers=headers)
        assert response.status_code == 200
        assert backend_post.call_args.kwargs['params'] == {'hours': 24, 'latitude': 52.2, 'longitude': 21.0}
        for query in ('latitude=52.2', 'latitude=91&longitude=21'):
            invalid = client.post(f'/analytics/api/ai/device-1?{query}', headers=headers)
            assert invalid.status_code == 400
        assert backend_post.call_count == 1


def test_ai_analysis_forwards_city():
    client = app.test_client()
    with client.session_transaction() as session:
        session['authenticated'] = True
        session['access_token'] = 'private-user-token'
        session['username'] = 'ai-city@example.test'
    client.get('/analytics/')
    with client.session_transaction() as session:
        csrf = session['analytics_csrf']
    with tempfile.TemporaryDirectory() as directory, patch.dict(app.config, {'RATE_LIMIT_DB_PATH': f'{directory}/limits.sqlite'}),\
            patch('app.controllers.analytics.api_client.post', return_value={'analysis': 'OK'}) as backend_post:
        response = client.post('/analytics/api/ai/device-1?hours=24&city=Warszawa', headers={'X-CSRF-Token': csrf})
        assert response.status_code == 200
        assert backend_post.call_args.kwargs['params'] == {'hours': 24, 'city': 'Warszawa'}


def test_ai_analysis_maps_configuration_and_ownership_errors():
    client = app.test_client()
    with client.session_transaction() as session:
        session['authenticated'] = True
        session['access_token'] = 'private-user-token'
        session['username'] = 'ai-errors@example.test'
    client.get('/analytics/')
    with client.session_transaction() as session:
        csrf = session['analytics_csrf']

    with tempfile.TemporaryDirectory() as directory, patch.dict(app.config, {
        'RATE_LIMIT_DB_PATH': f'{directory}/limits.sqlite',
    }), patch('app.controllers.analytics.api_client.post', side_effect=APIError('internal provider detail', 503)):
        response = client.post('/analytics/api/ai/device-1', headers={'X-CSRF-Token': csrf})
    assert response.status_code == 503
    assert 'AI' in response.json['error']
    assert 'internal provider detail' not in response.json['error']


def test_ai_analysis_enforces_per_account_hourly_limit():
    client = app.test_client()
    with client.session_transaction() as session:
        session['authenticated'] = True
        session['access_token'] = 'private-user-token'
        session['username'] = 'ai-limit@example.com'
    client.get('/analytics/')
    with client.session_transaction() as session:
        csrf = session['analytics_csrf']

    with tempfile.TemporaryDirectory() as directory, patch.dict(app.config, {
        'RATE_LIMIT_DB_PATH': f'{directory}/limits.sqlite',
        'AI_ANALYSIS_RATE_LIMIT': 5,
        'AI_ANALYSIS_RATE_WINDOW_SECONDS': 3600,
    }), patch('app.controllers.analytics.api_client.post', return_value={'analysis': 'OK'}) as backend_post:
        for _ in range(5):
            response = client.post('/analytics/api/ai/device-1', headers={'X-CSRF-Token': csrf})
            assert response.status_code == 200
        limited = client.post('/analytics/api/ai/device-1', headers={'X-CSRF-Token': csrf})
    assert limited.status_code == 429
    assert limited.headers['Retry-After']
    assert backend_post.call_count == 5
