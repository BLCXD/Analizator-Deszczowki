import os
import sys
import time
from unittest.mock import Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from app.main import app
from app.db.base import Base
from app.db.session import engine

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def _account_and_device(suffix):
    email = f"ai_analysis_{suffix}@example.com"
    registered = client.post('/api/v1/auth/register', json={'email': email, 'password': 'test-password-123'})
    assert registered.status_code == 200, registered.text
    headers = {'Authorization': f"Bearer {registered.json()['access_token']}"}
    device_id = f'ai-device-{suffix}'
    created = client.post('/api/v1/devices/', json={'device_id': device_id, 'name': 'AI test'}, headers=headers)
    assert created.status_code == 201, created.text
    return headers, device_id


def test_ai_analysis_sends_only_bounded_measurement_fields(monkeypatch):
    monkeypatch.setenv('NVIDIA_API_KEY', 'unit-test-key')
    headers, device_id = _account_and_device(str(time.time_ns()))
    for index in range(3):
        inserted = client.post('/api/v1/measurements/', headers=headers, json={
            'device_id': device_id,
            'measurement_id': f'ai-measurement-{time.time_ns()}-{index}',
            'water_quality_ph': 7.1,
            'raw_data': 'must not be sent to NVIDIA',
        })
        assert inserted.status_code == 201, inserted.text

    provider_response = Mock(status_code=200)
    provider_response.json.return_value = {
        'choices': [{'message': {'content': 'Podsumowanie\nOdczyty są stabilne.'}}]
    }
    provider = Mock(return_value=provider_response)
    monkeypatch.setattr('app.services.ai_analysis.httpx.post', provider)

    response = client.post(f'/api/v1/measurements/{device_id}/analysis/ai?hours=24', headers=headers)
    assert response.status_code == 200, response.text
    assert response.json()['measurement_count'] == 3
    assert response.json()['analysis'] == 'Podsumowanie\nOdczyty są stabilne.'
    sent = provider.call_args.kwargs['json']['messages'][1]['content']
    assert 'must not be sent to NVIDIA' not in sent
    assert 'measurement_id' not in sent
    assert 'device_id' not in sent
    assert provider.call_args.kwargs['headers']['Authorization'] == 'Bearer unit-test-key'
    assert provider.call_args.kwargs['json']['model'] == 'nvidia/nemotron-3.5-lightning-30b-a3b'
    assert provider.call_args.kwargs['json']['max_tokens'] == 768
    assert provider.call_args.kwargs['json']['chat_template_kwargs'] == {'enable_thinking': False}
    assert provider.call_args.kwargs['timeout'].read == 75.0


def test_ai_analysis_includes_optional_weather(monkeypatch):
    monkeypatch.setenv('NVIDIA_API_KEY', 'unit-test-key')
    headers, device_id = _account_and_device(str(time.time_ns()))
    measurement = client.post('/api/v1/measurements/', headers=headers, json={
        'device_id': device_id, 'measurement_id': f'ai-weather-{time.time_ns()}', 'rainfall_1h_mm': 2.0,
    })
    assert measurement.status_code == 201, measurement.text
    weather_response = Mock()
    weather_response.json.return_value = {'hourly': {'time': ['2026-10-25T00:00'], 'temperature_2m': [8], 'precipitation': [1.2]}}
    monkeypatch.setattr('app.api.v1.measurements.httpx.get', Mock(return_value=weather_response))
    provider_response = Mock(status_code=200)
    provider_response.json.return_value = {'choices': [{'message': {'content': 'Analiza'}, 'finish_reason': 'stop'}]}
    provider = Mock(return_value=provider_response)
    monkeypatch.setattr('app.services.ai_analysis.httpx.post', provider)

    response = client.post(f'/api/v1/measurements/{device_id}/analysis/ai?hours=24&latitude=52.2&longitude=21.0', headers=headers)
    assert response.status_code == 200, response.text
    data = provider.call_args.kwargs['json']['messages'][1]['content']
    assert 'weather_hourly' in data and 'precipitation_mm' in data
    assert 'weather_hourly' not in provider.call_args.kwargs['json']['messages'][0]['content']


def test_ai_analysis_geocodes_city_before_weather(monkeypatch):
    monkeypatch.setenv('NVIDIA_API_KEY', 'unit-test-key')
    headers, device_id = _account_and_device(str(time.time_ns()))
    inserted = client.post('/api/v1/measurements/', headers=headers, json={
        'device_id': device_id, 'measurement_id': f'ai-city-{time.time_ns()}',
    })
    assert inserted.status_code == 201, inserted.text
    geocode = Mock()
    geocode.json.return_value = {'results': [{'latitude': 52.2, 'longitude': 21.0}]}
    weather = Mock()
    weather.json.return_value = {'hourly': {'time': [], 'temperature_2m': [], 'precipitation': []}}
    get = Mock(side_effect=[geocode, weather])
    monkeypatch.setattr('app.api.v1.measurements.httpx.get', get)
    provider_response = Mock(status_code=200)
    provider_response.json.return_value = {'choices': [{'message': {'content': 'Analiza'}, 'finish_reason': 'stop'}]}
    monkeypatch.setattr('app.services.ai_analysis.httpx.post', Mock(return_value=provider_response))
    response = client.post(f'/api/v1/measurements/{device_id}/analysis/ai?hours=24&city=Warszawa', headers=headers)
    assert response.status_code == 200, response.text
    assert get.call_args_list[0].kwargs['params']['name'] == 'Warszawa'
    assert get.call_args_list[1].kwargs['params']['latitude'] == 52.2


def test_ai_analysis_requires_owner_and_provider_key(monkeypatch):
    owner_headers, device_id = _account_and_device(str(time.time_ns()))
    other_headers, _ = _account_and_device(f"other-{time.time_ns()}")
    measurement = client.post('/api/v1/measurements/', headers=owner_headers, json={
        'device_id': device_id,
        'measurement_id': f'ai-key-check-{time.time_ns()}',
    })
    assert measurement.status_code == 201, measurement.text
    provider = Mock()
    monkeypatch.setattr('app.services.ai_analysis.httpx.post', provider)

    denied = client.post(f'/api/v1/measurements/{device_id}/analysis/ai', headers=other_headers)
    assert denied.status_code == 403
    provider.assert_not_called()

    monkeypatch.delenv('NVIDIA_API_KEY', raising=False)
    unavailable = client.post(f'/api/v1/measurements/{device_id}/analysis/ai', headers=owner_headers)
    assert unavailable.status_code == 503
    assert 'NVIDIA' in unavailable.json()['detail']
    provider.assert_not_called()


def test_ai_analysis_maps_provider_errors_without_leaking_response(monkeypatch):
    from app.services.ai_analysis import AIAnalysisError, analyze_measurements_with_nvidia

    monkeypatch.setenv('NVIDIA_API_KEY', 'unit-test-key')
    provider_response = Mock(status_code=401, text='sensitive provider response')
    monkeypatch.setattr('app.services.ai_analysis.httpx.post', Mock(return_value=provider_response))
    try:
        analyze_measurements_with_nvidia([], 24)
        assert False, 'Expected provider error'
    except AIAnalysisError as error:
        assert error.status_code == 502
        assert 'sensitive provider response' not in str(error)

    pending_response = Mock(status_code=202)
    monkeypatch.setattr('app.services.ai_analysis.httpx.post', Mock(return_value=pending_response))
    try:
        analyze_measurements_with_nvidia([], 24)
        assert False, 'Expected pending provider response'
    except AIAnalysisError as error:
        assert error.status_code == 503
        assert 'przetwarzana' in str(error)


def test_ai_analysis_rejects_provider_truncation(monkeypatch):
    from app.services.ai_analysis import AIAnalysisError, analyze_measurements_with_nvidia

    monkeypatch.setenv('NVIDIA_API_KEY', 'unit-test-key')
    provider_response = Mock(status_code=200)
    provider_response.json.return_value = {
        'choices': [{'message': {'content': 'Niepełna analiza'}, 'finish_reason': 'length'}]
    }
    monkeypatch.setattr('app.services.ai_analysis.httpx.post', Mock(return_value=provider_response))
    try:
        analyze_measurements_with_nvidia([{'ph': 7.0}], 24)
        assert False, 'Expected truncated analysis to be rejected'
    except AIAnalysisError as error:
        assert error.status_code == 502
        assert 'ucięta' in str(error)


def test_ai_analysis_does_not_call_provider_without_measurements(monkeypatch):
    headers, device_id = _account_and_device(str(time.time_ns()))
    provider = Mock()
    monkeypatch.setenv('NVIDIA_API_KEY', 'unit-test-key')
    monkeypatch.setattr('app.services.ai_analysis.httpx.post', provider)
    response = client.post(f'/api/v1/measurements/{device_id}/analysis/ai?hours=24', headers=headers)
    assert response.status_code == 200
    assert response.json()['measurement_count'] == 0
    assert 'Brak pomiarów' in response.json()['analysis']
    provider.assert_not_called()
