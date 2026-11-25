"""
Dashboard controller for Analizator Deszczówki.
"""
import requests
from flask import render_template, session, jsonify, redirect, url_for, current_app
from app.controllers.base import create_blueprint
from datetime import datetime, timezone, timedelta

dashboard_bp = create_blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
                              
    if not session.get('authenticated'):
        return redirect(url_for('auth.login'))

    headers = {
        'Authorization': f"Bearer {session.get('access_token')}"
    }

    user_data = None
    devices_data = []
    alerts = []

    try:
        user_response = requests.get(
            f"{current_app.config['API_BASE_URL']}/api/v1/auth/me",
            headers=headers,
            timeout=current_app.config['API_TIMEOUT']
        )
        if user_response.status_code == 200:
            user_data = user_response.json()
    except (requests.RequestException, ValueError):
        user_data = None

    try:
        devices_response = requests.get(
            f"{current_app.config['API_BASE_URL']}/api/v1/devices/",
            headers=headers,
            timeout=current_app.config['API_TIMEOUT']
        )
        if devices_response.status_code == 200:
            devices_data = devices_response.json()
    except (requests.RequestException, ValueError):
        devices_data = []

    if devices_data:
        for device in devices_data:
            try:
                measurement_response = requests.get(
                    f"{current_app.config['API_BASE_URL']}/api/v1/measurements/{device.get('device_id')}/latest",
                    headers=headers,
                    timeout=current_app.config['API_TIMEOUT']
                )
                if measurement_response.status_code == 200:
                    measurement = measurement_response.json()
                    if not isinstance(measurement, dict):
                        raise ValueError("Invalid measurement response")
                    device['latest_measurement'] = measurement
                    measurement_time_str = measurement.get('measurement_time')
                    if not isinstance(measurement_time_str, str):
                        raise ValueError("Measurement timestamp is missing")
                    if measurement_time_str.endswith('Z'):
                        measurement_time_str = measurement_time_str[:-1] + '+00:00'
                    elif 'T' in measurement_time_str and not ('+' in measurement_time_str or '-' in measurement_time_str.split('T')[1]):
                        measurement_time_str = measurement_time_str + '+00:00'
                    measurement_time = datetime.fromisoformat(measurement_time_str)
                    now = datetime.now(timezone.utc)
                    if now - measurement_time < timedelta(minutes=5):
                        device['online'] = True
                    else:
                        device['online'] = False
                else:
                    device['latest_measurement'] = None
                    device['online'] = False
            except (requests.RequestException, ValueError, TypeError):
                device['latest_measurement'] = None
                device['online'] = False

    try:
        alerts_response = requests.get(
            f"{current_app.config['API_BASE_URL']}/api/v1/alerts/",
            headers=headers,
            timeout=current_app.config['API_TIMEOUT']
        )
        if alerts_response.status_code == 200:
            alerts = alerts_response.json()
    except (requests.RequestException, ValueError):
        alerts = []

    total_devices = len(devices_data)
    online_devices_count = sum(1 for d in devices_data if d.get('online', False))
    devices_with_problems_count = 0

    return render_template('dashboard.html',
                           active_page='dashboard',
                           authenticated=True,
                           user=user_data,
                           devices=devices_data,
                           total_devices=total_devices,
                           online_devices_count=online_devices_count,
                           devices_with_problems_count=devices_with_problems_count,
                           alerts=alerts)

@dashboard_bp.route('/dashboard')
def dashboard():
                                             
    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/api/system-status')
def system_status():
                                            
    if not session.get('authenticated'):
        return jsonify({'error': 'Authentication required'}), 401

    headers = {
        'Authorization': f"Bearer {session.get('access_token')}"
    }

    try:
        health_response = requests.get(
            f"{current_app.config['API_BASE_URL'].rstrip('/')}/health",
            timeout=min(current_app.config['API_TIMEOUT'], 5)
        )
        backend_status = 'connected' if health_response.status_code == 200 else 'error'

        user_response = requests.get(
            f"{current_app.config['API_BASE_URL']}/api/v1/auth/me",
            headers=headers,
            timeout=min(current_app.config['API_TIMEOUT'], 5)
        )
        database_status = 'connected' if user_response.status_code == 200 else 'error'
    except requests.RequestException:
        backend_status = 'error'
        database_status = 'error'

    websocket_status = 'connected'
    if backend_status == 'error':
        websocket_status = 'error'

    return jsonify({
        'status': 'ok' if backend_status == 'connected' and database_status == 'connected' else 'error',
        'backend': backend_status,
        'database': database_status,
        'websocket': websocket_status,
        'online': backend_status == 'connected' and database_status == 'connected'
    })
