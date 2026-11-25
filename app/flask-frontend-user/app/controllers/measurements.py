"""Authenticated browser endpoints for measurement data."""
from urllib.parse import quote

from flask import render_template, session, jsonify, current_app

from app.controllers.base import create_blueprint
from app.services.api_client import api_client, APIError

measurements_bp = create_blueprint('measurements', __name__)


def _require_login():
    if not session.get('authenticated') or not session.get('access_token'):
        return jsonify({'error': 'Authentication required'}), 401
    return None


@measurements_bp.route('/')
def index():
    if not session.get('authenticated'):
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))
    return render_template('measurements.html', active_page='measurements', authenticated=True)


@measurements_bp.route('/api/latest/<device_id>')
def latest_measurement(device_id):
    denied = _require_login()
    if denied:
        return denied
    try:
        measurement = api_client.get(f'/api/v1/measurements/{quote(device_id, safe="")}/latest')
        return jsonify(measurement)
    except APIError as exc:
        if exc.status_code == 404:
            return jsonify({'error': 'Brak pomiarów dla tego urządzenia'}), 404
        current_app.logger.warning('Latest measurement request failed with status %s', exc.status_code)
        return jsonify({'error': 'Nie udało się pobrać pomiaru'}), exc.status_code or 502


@measurements_bp.route('/api/history/<device_id>')
def measurement_history(device_id):
    denied = _require_login()
    if denied:
        return denied
    try:
        measurements = api_client.get(f'/api/v1/measurements/{quote(device_id, safe="")}?limit=500')
        return jsonify({'device_id': device_id, 'measurements': measurements})
    except APIError as exc:
        current_app.logger.warning('Measurement history request failed with status %s', exc.status_code)
        return jsonify({'error': 'Nie udało się pobrać historii pomiarów'}), exc.status_code or 502


@measurements_bp.route('/api/stream-ticket/<device_id>')
def stream_ticket(device_id):
    denied = _require_login()
    if denied:
        return denied
    try:
        ticket = api_client.get(f'/api/v1/devices/{quote(device_id, safe="")}/stream-ticket')
        return jsonify(ticket)
    except APIError as exc:
        current_app.logger.warning('WebSocket ticket request failed with status %s', exc.status_code)
        return jsonify({'error': 'Nie można uruchomić podglądu na żywo'}), exc.status_code or 502
