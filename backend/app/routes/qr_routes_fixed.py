from flask import Blueprint, request, jsonify
import io
import base64
from PIL import Image
import qrcode
import cloudinary
from app.utils.qr_utils import generate_qr_code, add_logo_to_qr, add_frame_and_text
from app.utils.analytics_utils import log_qr_scan, get_analytics_data

qr_bp = Blueprint('qr', __name__)

@qr_bp.route('/generate', methods=['POST'])
def generate():
    """Generate QR code with customization options"""
    try:
        data = request.json
        
        if not data or 'data' not in data:
            return jsonify({'error': 'No data provided'}), 400
        
        qr_data = data['data']
        options = data.get('options', {})
        
        # Generate basic QR code
        qr_img = generate_qr_code(
            qr_data,
            error_correction=options.get('error_correction', 'M'),
            version=options.get('version'),
            box_size=options.get('box_size', 10),
            border=options.get('border', 4)
        )
        
        # Add logo if provided
        if options.get('logo'):
            logo_options = options['logo']
            logo_data = logo_options.get('data')
            
            if logo_data:
                # Decode base64 logo data
                logo_bytes = base64.b64decode(logo_data.split(',')[1] if ',' in logo_data else logo_data)
                logo_img = Image.open(io.BytesIO(logo_bytes))
                
                # Add logo to QR code
                qr_img = add_logo_to_qr(
                    qr_img,
                    logo_img,
                    size_ratio=logo_options.get('size', 0.2),
                    position=logo_options.get('position', 'center'),
                    shape=logo_options.get('shape', 'square'),
                    border=logo_options.get('border', True)
                )
        
        # Add frame and text if provided
        if options.get('frame'):
            frame_options = options['frame']
            
            qr_img = add_frame_and_text(
                qr_img,
                text=frame_options.get('text', ''),
                font_size=frame_options.get('font_size', 20),
                frame_color=frame_options.get('color', '#000000'),
                padding=frame_options.get('padding', 20)
            )
        
        # Convert to base64 for response
        buffered = io.BytesIO()
        qr_img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # Upload to Cloudinary if requested
        cloudinary_url = None
        if options.get('upload', False):
            upload_result = cloudinary.uploader.upload(
                f"data:image/png;base64,{img_str}",
                folder="qr_codes"
            )
            cloudinary_url = upload_result['secure_url']
        
        response = {
            'image': f"data:image/png;base64,{img_str}",
            'url': cloudinary_url
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@qr_bp.route('/analytics', methods=['GET'])
def analytics():
    """Get all QR code analytics data"""
    try:
        data = get_analytics_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@qr_bp.route('/analytics/<qr_id>', methods=['GET'])
def qr_analytics(qr_id):
    """Get analytics data for a specific QR code"""
    try:
        data = get_analytics_data(qr_id)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@qr_bp.route('/scan/<qr_id>', methods=['POST'])
def scan(qr_id):
    """Log a QR code scan"""
    try:
        data = request.json or {}
        user_agent = request.headers.get('User-Agent', '')
        ip_address = request.remote_addr
        
        scan_data = log_qr_scan(qr_id, user_agent, ip_address, data)
        
        return jsonify({'success': True, 'scan_id': scan_data.get('_id')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
