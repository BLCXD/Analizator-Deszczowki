"""
Admin controller for Analizator Deszczówki.
Proxies the backend admin API (/api/v1/admin/*) for the Flask dashboard.
All routes require an admin session (session['is_admin'] is True).
"""
from urllib.parse import quote
from flask import render_template, session, jsonify, request, redirect, url_for, current_app
from app.controllers.base import create_blueprint
from app.services.api_client import api_client, APIError

admin_bp = create_blueprint('admin', __name__)


def _require_admin():
                                                                                    
    if not session.get('is_admin'):
        if request.is_json:
            return jsonify({'error': 'Administrator access required'}), 403
        return redirect(url_for('auth.login'))
    return None


@admin_bp.route('/')
def index():
                                                      
    if not session.get('is_admin'):
        return redirect(url_for('auth.login'))

    users = []
    devices = []
    try:
        users = api_client.get('/api/v1/admin/users') or []
    except APIError:
        current_app.logger.exception('Failed to fetch admin users')
    try:
        devices = api_client.get('/api/v1/admin/devices') or []
    except APIError:
        current_app.logger.exception('Failed to fetch admin devices')

    return render_template(
        'admin/index.html',
        active_page='admin',
        authenticated=True,
        users=users,
        devices=devices,
    )


@admin_bp.route('/api/users')
def api_users():
                                                                  
    if not session.get('is_admin'):
        return jsonify({'error': 'Administrator access required'}), 403
    try:
        users = api_client.get('/api/v1/admin/users') or []
        return jsonify(users)
    except APIError as exc:
        return jsonify({'error': exc.message}), exc.status_code or 502


@admin_bp.route('/api/users/<int:user_id>/active', methods=['PATCH'])
def api_set_user_active(user_id):
                                                    
    if not session.get('is_admin'):
        return jsonify({'error': 'Administrator access required'}), 403
    data = request.get_json(silent=True) or {}
    is_active = bool(data.get('is_active'))
    try:
        result = api_client.patch(
            f'/api/v1/admin/users/{user_id}/active',
            params={'is_active': is_active},
        )
        return jsonify(result), 200
    except APIError as exc:
        return jsonify({'error': exc.message}), exc.status_code or 502


@admin_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Administrator access required'}), 403
    try:
        api_client.delete(f'/api/v1/admin/users/{user_id}')
        return jsonify({'success': True}), 200
    except APIError as exc:
        return jsonify({'error': exc.message}), exc.status_code or 502


@admin_bp.route('/api/devices')
def api_devices():
                                                                      
    if not session.get('is_admin'):
        return jsonify({'error': 'Administrator access required'}), 403
    try:
        devices = api_client.get('/api/v1/admin/devices') or []
        return jsonify(devices)
    except APIError as exc:
        return jsonify({'error': exc.message}), exc.status_code or 502


@admin_bp.route('/api/devices/<device_id>', methods=['PUT'])
def api_update_device(device_id):
                                                  
    if not session.get('is_admin'):
        return jsonify({'error': 'Administrator access required'}), 403
    data = request.get_json(silent=True) or {}
    payload = {}
    if 'name' in data:
        payload['name'] = data.get('name')
    if 'is_active' in data:
        payload['is_active'] = bool(data.get('is_active'))
    try:
        result = api_client.put(
            f'/api/v1/admin/devices/{quote(device_id, safe="")}',
            data=payload,
        )
        return jsonify(result), 200
    except APIError as exc:
        return jsonify({'error': exc.message}), exc.status_code or 502


@admin_bp.route('/api/devices/<device_id>', methods=['DELETE'])
def api_delete_device(device_id):
                                 
    if not session.get('is_admin'):
        return jsonify({'error': 'Administrator access required'}), 403
    try:
        api_client.delete(f'/api/v1/admin/devices/{quote(device_id, safe="")}')
        return jsonify({'success': True}), 200
    except APIError as exc:
        return jsonify({'error': exc.message}), exc.status_code or 502


@admin_bp.route('/api/users/<int:user_id>/devices')
def api_user_devices(user_id):
                                                                                  
    if not session.get('is_admin'):
        return jsonify({'error': 'Administrator access required'}), 403
    try:
        devices = api_client.get(f'/api/v1/admin/users/{user_id}/devices') or []
        if not isinstance(devices, list):
            return jsonify({'error': 'Invalid device list response'}), 502
        return jsonify(devices)
    except APIError as exc:
        return jsonify({'error': exc.message}), exc.status_code or 502


@admin_bp.route('/api/devices/<device_id>/measurements')
def api_device_measurements(device_id):
                                                                                                
    if not session.get('is_admin'):
        return jsonify({'error': 'Administrator access required'}), 403
    try:
        measurements = api_client.get(
            f'/api/v1/admin/devices/{quote(device_id, safe="")}/measurements'
        ) or []
        return jsonify(measurements)
    except APIError as exc:
        return jsonify({'error': exc.message}), exc.status_code or 502
