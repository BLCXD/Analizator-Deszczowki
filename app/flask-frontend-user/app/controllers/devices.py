"""
Devices controller for Analizator Deszczówki.
"""
import secrets
import requests
import hmac
from urllib.parse import quote
from flask import render_template, session, jsonify, request, redirect, url_for, current_app
from app.controllers.base import create_blueprint
from app.services.api_client import api_client, APIError

devices_bp = create_blueprint('devices', __name__)


def _runner_request(method, path, **kwargs):
    if not current_app.config.get('ENABLE_MOCK_SIMULATOR'):
        raise RuntimeError('Mock simulator is disabled')
    token = current_app.config.get('MOCK_RUNNER_TOKEN', '')
    if len(token) < 32:
        raise RuntimeError('Mock simulator is not configured')
    return requests.request(
        method,
        current_app.config['MOCK_RUNNER_URL'].rstrip('/') + path,
        headers={'Authorization': f'Bearer {token}'},
        timeout=3,
        **kwargs,
    )


@devices_bp.route('/')
def index():
                               
    if not session.get('authenticated'):
        return redirect(url_for('auth.login'))

    session['device_form_csrf'] = secrets.token_urlsafe(32)
    return render_template(
        'devices.html', active_page='devices', authenticated=True,
        mock_enabled=current_app.config.get('ENABLE_MOCK_SIMULATOR', False),
    )


@devices_bp.route('/<device_id>')
def detail(device_id):
                             
    if not session.get('authenticated'):
        return redirect(url_for('auth.login'))

    return render_template('devices/detail.html', device_id=device_id, active_page='devices', authenticated=True)


@devices_bp.route('/api/list')
def device_list():
                                              
    if not session.get('authenticated'):
        return jsonify({'error': 'Authentication required'}), 401

    try:
        response = api_client.get('/api/v1/devices/')
        devices_data = response

        mock_agents = {}
        if current_app.config.get('ENABLE_MOCK_SIMULATOR'):
            try:
                runner_response = _runner_request('GET', '/api/agents')
                if runner_response.ok:
                    mock_agents = runner_response.json().get('agents', {})
            except requests.RequestException:
                current_app.logger.warning('Mock runner status is unavailable')

        formatted_devices = []
        for device in devices_data:
            formatted_devices.append({
                'id': device.get('id'),
                'device_id': device.get('device_id'),
                'name': device.get('name'),
                'location': device.get('location'),
                'status': device.get('status', 'unknown'),
                'is_active': device.get('is_active', False),
                'mock_agent_known': device.get('device_id') in mock_agents,
                'mock_running': mock_agents.get(device.get('device_id'), False),
                'last_seen': device.get('last_seen')
            })
        return jsonify({'devices': formatted_devices})
    except APIError as e:
        current_app.logger.error(f"Failed to fetch devices: {e.message}")
        return jsonify({'error': 'Failed to fetch devices'}), e.status_code or 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error fetching devices: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@devices_bp.route('/api/<device_id>', methods=['DELETE'])
def delete_device_proxy(device_id):
                                                                           
    if not session.get('authenticated'):
        return jsonify({'error': 'Authentication required'}), 401

    try:
        api_client.delete(f'/api/v1/devices/{quote(device_id, safe="")}')
        if current_app.config.get('ENABLE_MOCK_SIMULATOR'):
            try:
                _runner_request('POST', '/api/agents/delete', json={'device_id': device_id})
            except requests.RequestException:
                current_app.logger.warning('Could not remove mock process for deleted device')
        return jsonify({'success': True})
    except APIError as exc:
        current_app.logger.error(f"Failed to delete device: {exc.message}")
        return jsonify({'error': exc.message}), exc.status_code or 500


@devices_bp.route('/api/unpair/<device_id>', methods=['POST'])
def unpair_device_proxy(device_id):
    if not session.get('authenticated'):
        return jsonify({'error': 'Authentication required'}), 401
    try:
        api_client.post(f'/api/v1/devices/{quote(device_id, safe="")}/unpair')
        return jsonify({'success': True})
    except APIError as exc:
        return jsonify({'error': exc.message}), exc.status_code or 500


@devices_bp.route('/api/code/<device_id>', methods=['POST'])
def generate_code_proxy(device_id):
    if not session.get('authenticated'):
        return jsonify({'error': 'Authentication required'}), 401
    try:
        response = api_client.post(f'/api/v1/devices/{quote(device_id, safe="")}/code', data={})
        return jsonify(response), 200
    except APIError as exc:
        return jsonify({'error': exc.message}), exc.status_code or 400


@devices_bp.route('/api/pair/<device_id>', methods=['POST'])
def pair_device_proxy(device_id):
    if not session.get('authenticated'):
        return jsonify({'error': 'Authentication required'}), 401
    data = request.get_json(silent=True) or {}
    device_code = data.get('device_code', '').strip()
    if not device_code:
        return jsonify({'error': 'Kod parowania jest wymagany'}), 400
    try:
        api_client.post(f'/api/v1/devices/{quote(device_id, safe="")}/pair-by-code', json={'device_code': device_code})
        return jsonify({'success': True})
    except APIError as exc:
        return jsonify({'error': exc.message}), exc.status_code or 400


@devices_bp.route('/api/status/<device_id>')
def device_status(device_id):
                                                          
    if not session.get('authenticated'):
        return jsonify({'error': 'Authentication required'}), 401

    try:
        device_response = api_client.get(f'/api/v1/devices/{device_id}')
        device_data = device_response

        try:
            measurement_response = api_client.get(f'/api/v1/measurements/{device_id}/latest')
            latest_measurement = measurement_response
        except APIError as e:
            latest_measurement = None
            if e.status_code != 404:
                current_app.logger.warning(f"No measurements found for device {device_id}: {e.message}")

        status_data = {
            'device_id': device_data.get('device_id'),
            'status': device_data.get('status', 'unknown'),
            'last_seen': device_data.get('last_seen'),
            'signal_strength': 'strong',
            'uptime': 'Unknown',
            'firmware_version': device_data.get('firmware_version', 'Unknown'),
            'sensors': {
                'water_quality_ph': 'ok' if latest_measurement and latest_measurement.get('water_quality_ph') is not None else 'unknown',
                'water_quality_turbidity': 'ok' if latest_measurement and latest_measurement.get('water_quality_turbidity') is not None else 'unknown',
                'temperature': 'ok' if latest_measurement and latest_measurement.get('temperature') is not None else 'unknown',
                'humidity': 'ok' if latest_measurement and latest_measurement.get('humidity') is not None else 'unknown'
            }
        }

        if latest_measurement:
            status_data['latest_measurement'] = {
                'timestamp': latest_measurement.get('measurement_time'),
                'ph': latest_measurement.get('water_quality_ph'),
                'turbidity': latest_measurement.get('water_quality_turbidity'),
                'temperature': latest_measurement.get('temperature'),
                'humidity': latest_measurement.get('humidity')
            }

        return jsonify(status_data)
    except APIError as e:
        current_app.logger.error(f"Failed to fetch device status for {device_id}: {e.message}")
        if e.status_code == 404:
            return jsonify({'error': 'Device not found'}), 404
        return jsonify({'error': 'Failed to fetch device status'}), e.status_code or 500
    except Exception:
        current_app.logger.exception('Unexpected error fetching device status')
        return jsonify({'error': 'Internal server error'}), 500


def _validate_mock_csrf():
    expected = session.get('device_form_csrf', '')
    supplied = request.headers.get('X-CSRF-Token', '')
    valid = bool(expected and supplied and hmac.compare_digest(expected, supplied))
    next_token = secrets.token_urlsafe(32)
    session['device_form_csrf'] = next_token
    return valid, next_token


@devices_bp.route('/api/mock/<action>/<device_id>', methods=['POST'])
def control_mock_agent(action, device_id):
    if not session.get('authenticated'):
        return jsonify({'error': 'Authentication required'}), 401
    if action not in ('start', 'stop'):
        return jsonify({'error': 'Unsupported action'}), 404
    valid, csrf_token = _validate_mock_csrf()
    if not valid:
        return jsonify({'error': 'Formularz wygasł', 'csrf_token': csrf_token}), 400
    try:
        device = api_client.get(f'/api/v1/devices/{quote(device_id, safe="")}')
        runner_response = _runner_request(
            'POST', f'/api/agents/{action}', json={'device_id': device['device_id']},
        )
        if runner_response.status_code >= 400:
            return jsonify({'error': 'Symulator nie jest już zarejestrowany. Dodaj ponownie urządzenie w trybie mock.', 'csrf_token': csrf_token}), 409
        return jsonify({'success': True, 'running': action == 'start', 'csrf_token': csrf_token})
    except APIError as exc:
        return jsonify({'error': exc.message, 'csrf_token': csrf_token}), exc.status_code or 502
    except requests.RequestException:
        current_app.logger.exception('Mock runner request failed')
        return jsonify({'error': 'Symulator jest niedostępny', 'csrf_token': csrf_token}), 502