import qrcode
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import json
import uuid
import os
from datetime import datetime
from app.utils.cloudinary import upload_image, get_image_url

def generate_qr(data, error_correction='M', version=None, box_size=10, border=4):
    """Generate QR code with specified parameters"""
    # Map error correction level string to qrcode constants
    error_levels = {
        'L': qrcode.constants.ERROR_CORRECT_L,
        'M': qrcode.constants.ERROR_CORRECT_M,
        'Q': qrcode.constants.ERROR_CORRECT_Q,
        'H': qrcode.constants.ERROR_CORRECT_H
    }
    
    # Default to M if not valid
    ec_level = error_levels.get(error_correction.upper(), qrcode.constants.ERROR_CORRECT_M)
    
    qr = qrcode.QRCode(
        version=version,
        error_correction=ec_level,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    # Ensure the image is in PIL Image format
    if not isinstance(img, Image.Image):
        img = img.convert('RGB')
    
    return img

def qr_to_base64(qr_img, format="PNG"):
    """Convert QR code image to base64 string"""
    buffered = io.BytesIO()
    qr_img.save(buffered, format=format)
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return f"data:image/{format.lower()};base64,{img_str}"

def upload_qr_to_cloud(qr_img, qr_id=None):
    """Upload QR code to Cloudinary"""
    # Convert PIL Image to bytes
    img_byte_arr = io.BytesIO()
    qr_img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    # Generate a unique ID if not provided
    if not qr_id:
        qr_id = str(uuid.uuid4())[:8]
    
    # Upload to Cloudinary
    result = upload_image(
        img_byte_arr,
        folder="qr_codes",
        public_id=f"qr_{qr_id}"
    )
    
    if result:
        return result['secure_url']
    return None

def format_qr_data(qr_type, content):
    """Format QR code data based on type"""
    if qr_type == "url":
        # Ensure URL has proper format
        if not content.startswith(('http://', 'https://')):
            content = 'https://' + content
        return content
    
    elif qr_type == "email":
        # Format as email link
        if '@' in content:
            return f"mailto:{content}"
        else:
            return f"mailto:example@example.com?subject=Subject&body={content}"
    
    elif qr_type == "phone":
        # Format as phone link
        return f"tel:{content.replace(' ', '')}"
    
    elif qr_type == "sms":
        # Format as SMS link
        if ':' in content:
            number, message = content.split(':', 1)
            return f"smsto:{number.strip()}:{message.strip()}"
        else:
            return f"smsto:{content.strip()}"
    
    elif qr_type == "wifi":
        # Format as WiFi network info
        try:
            # Parse JSON if provided
            if content.startswith('{') and content.endswith('}'):
                wifi_data = json.loads(content)
                ssid = wifi_data.get('ssid', '')
                password = wifi_data.get('password', '')
                security = wifi_data.get('security', 'WPA')
                
                return f"WIFI:S:{ssid};T:{security};P:{password};;"
            else:
                # Try to parse as "ssid:password:security"
                parts = content.split(':')
                if len(parts) >= 2:
                    ssid = parts[0]
                    password = parts[1]
                    security = parts[2] if len(parts) > 2 else "WPA"
                    
                    return f"WIFI:S:{ssid};T:{security};P:{password};;"
                else:
                    return content
        except Exception as e:
            print(f"Error formatting WiFi data: {str(e)}")
            return content
    
    elif qr_type == "vcard":
        # Format as vCard
        try:
            # Parse JSON if provided
            if content.startswith('{') and content.endswith('}'):
                vcard_data = json.loads(content)
                name = vcard_data.get('name', '')
                org = vcard_data.get('org', '')
                phone = vcard_data.get('phone', '')
                email = vcard_data.get('email', '')
                url = vcard_data.get('url', '')
                
                return f"""BEGIN:VCARD
VERSION:3.0
N:{name}
ORG:{org}
TEL:{phone}
EMAIL:{email}
URL:{url}
END:VCARD"""
            else:
                return content
        except Exception as e:
            print(f"Error formatting vCard data: {str(e)}")
            return content
    
    else:
        # For text or other types, use as is
        return content
