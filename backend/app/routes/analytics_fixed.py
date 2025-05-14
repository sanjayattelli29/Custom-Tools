from flask import Blueprint, jsonify, request
from app.utils.analytics_utils import get_analytics_data, get_scan_count, get_unique_devices, get_scan_timeline

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/', methods=['GET'])
def get_all_analytics():
    """Get all analytics data"""
    try:
        data = get_analytics_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/<qr_id>', methods=['GET'])
def get_qr_analytics(qr_id):
    """Get analytics data for a specific QR code"""
    try:
        data = get_analytics_data(qr_id)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/count', methods=['GET'])
def get_total_scans():
    """Get total scan count"""
    try:
        qr_id = request.args.get('qr_id')
        count = get_scan_count(qr_id)
        return jsonify({'count': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/devices', methods=['GET'])
def get_devices():
    """Get device breakdown"""
    try:
        qr_id = request.args.get('qr_id')
        devices = get_unique_devices(qr_id)
        return jsonify(devices)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/timeline', methods=['GET'])
def get_timeline():
    """Get scan timeline"""
    try:
        qr_id = request.args.get('qr_id')
        timeline = get_scan_timeline(qr_id)
        return jsonify(timeline)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
