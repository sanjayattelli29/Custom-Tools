from flask import Blueprint, request, jsonify, redirect
from app.utils.shortener_utils import create_short_url, get_original_url, get_all_short_urls, update_original_url

url_bp = Blueprint('url', __name__)

@url_bp.route('/shorten', methods=['POST'])
def shorten():
    """Create a short URL"""
    try:
        data = request.json
        
        if not data or 'url' not in data:
            return jsonify({'error': 'No URL provided'}), 400
        
        url = data['url']
        short_url = create_short_url(url)
        
        if short_url:
            return jsonify({
                'original_url': url,
                'short_url': short_url
            })
        else:
            return jsonify({'error': 'Failed to create short URL'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@url_bp.route('/redirect/<short_id>', methods=['GET'])
def redirect_to_url(short_id):
    """Redirect to the original URL"""
    try:
        original_url = get_original_url(short_id)
        
        if original_url:
            return redirect(original_url)
        else:
            return jsonify({'error': 'URL not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@url_bp.route('/all', methods=['GET'])
def get_all():
    """Get all shortened URLs"""
    try:
        urls = get_all_short_urls()
        
        # Format the response
        formatted_urls = []
        for url in urls:
            formatted_urls.append({
                'short_id': url[0],
                'original_url': url[1],
                'created_at': url[2],
                'scans': url[3],
                'short_url': url[4]
            })
        
        return jsonify(formatted_urls)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@url_bp.route('/<short_id>', methods=['GET'])
def get_url(short_id):
    """Get details for a specific short URL"""
    try:
        original_url = get_original_url(short_id)
        
        if original_url:
            return jsonify({
                'short_id': short_id,
                'original_url': original_url
            })
        else:
            return jsonify({'error': 'URL not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@url_bp.route('/<short_id>', methods=['PUT'])
def update_url(short_id):
    """Update the destination URL for a short ID"""
    try:
        data = request.json
        
        if not data or 'new_url' not in data:
            return jsonify({'error': 'No new URL provided'}), 400
        
        new_url = data['new_url']
        success = update_original_url(short_id, new_url)
        
        if success:
            return jsonify({
                'short_id': short_id,
                'original_url': new_url,
                'message': 'URL updated successfully'
            })
        else:
            return jsonify({'error': 'Failed to update URL'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
