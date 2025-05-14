from flask import Blueprint, request, jsonify
import cloudinary
import cloudinary.uploader
import uuid
import os

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/image', methods=['POST'])
def upload_image():
    """Upload an image to Cloudinary"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        
        if image_file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # Generate a unique ID for the image
        unique_id = uuid.uuid4().hex
        
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            image_file,
            folder="uploads",
            public_id=f"img_{unique_id}"
        )
        
        # Return the Cloudinary URL and other details
        return jsonify({
            'url': upload_result['secure_url'],
            'public_id': upload_result['public_id'],
            'format': upload_result['format'],
            'width': upload_result['width'],
            'height': upload_result['height']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@upload_bp.route('/optimize', methods=['POST'])
def optimize_image():
    """Optimize an image using Cloudinary transformations"""
    try:
        data = request.json
        
        if not data or 'url' not in data:
            return jsonify({'error': 'No image URL provided'}), 400
        
        url = data['url']
        
        # Check if it's a Cloudinary URL
        if 'cloudinary' not in url:
            return jsonify({'error': 'Not a Cloudinary URL'}), 400
        
        # Extract public_id from the URL
        parts = url.split('/')
        public_id_with_ext = parts[-1]
        public_id = os.path.splitext(public_id_with_ext)[0]
        
        # Apply transformations
        transformations = data.get('transformations', {})
        
        # Default transformations for optimization
        transform_options = {
            'fetch_format': transformations.get('format', 'auto'),
            'quality': transformations.get('quality', 'auto')
        }
        
        # Add other transformations if provided
        if 'width' in transformations:
            transform_options['width'] = transformations['width']
        
        if 'height' in transformations:
            transform_options['height'] = transformations['height']
        
        if 'crop' in transformations:
            transform_options['crop'] = transformations['crop']
        
        # Generate optimized URL
        optimized_url = cloudinary.utils.cloudinary_url(
            public_id,
            **transform_options
        )[0]
        
        return jsonify({
            'original_url': url,
            'optimized_url': optimized_url,
            'transformations': transform_options
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
