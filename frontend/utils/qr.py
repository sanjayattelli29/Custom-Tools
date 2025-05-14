import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import io
import base64
import json
import uuid
import svglib.svglib as svg
from reportlab.graphics import renderPM
import math
from datetime import datetime
import os
import cloudinary
from cloudinary import uploader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

def generate_qr_code(data, error_correction=qrcode.constants.ERROR_CORRECT_M, version=None, box_size=10, border=4):
    """Generate QR code with specified error correction and parameters"""
    qr = qrcode.QRCode(
        version=version,
        error_correction=error_correction,
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

def add_logo_to_qr(qr_img, logo_img, size_ratio=0.2, position='center', shape='square', border=True, border_color='white', opacity=1.0):
    """Add logo to QR code with advanced customization"""
    # Convert to RGBA if not already
    qr_img = qr_img.convert("RGBA")
    
    # Resize logo
    qr_width, qr_height = qr_img.size
    logo_size = int(min(qr_width, qr_height) * size_ratio)
    logo_img = logo_img.resize((logo_size, logo_size), Image.LANCZOS)
    
    # Convert logo to RGBA if not already
    if logo_img.mode != 'RGBA':
        logo_img = logo_img.convert('RGBA')
    
    # Apply shape mask if needed
    if shape == 'circle':
        # Create a circular mask
        mask = Image.new('L', (logo_size, logo_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, logo_size, logo_size), fill=255)
        
        # Apply the mask
        logo_img.putalpha(mask)
    
    # Apply border if needed
    if border:
        # Create a slightly larger background for the border
        border_size = int(logo_size * 1.1)
        border_img = Image.new('RGBA', (border_size, border_size), border_color)
        
        # Paste the logo onto the border
        border_x = (border_size - logo_size) // 2
        border_y = (border_size - logo_size) // 2
        border_img.paste(logo_img, (border_x, border_y), logo_img if logo_img.mode == 'RGBA' else None)
        
        # Update logo_img and logo_size
        logo_img = border_img
        logo_size = border_size
    
    # Apply opacity if needed
    if opacity < 1.0:
        # Create a new image with the same size and mode
        opacity_img = Image.new('RGBA', logo_img.size, (0, 0, 0, 0))
        
        # Blend the logo with the transparent image
        logo_img = Image.blend(opacity_img, logo_img, opacity)
    
    # Calculate position
    if position == 'center':
        pos_x = (qr_width - logo_size) // 2
        pos_y = (qr_height - logo_size) // 2
    elif position == 'top-left':
        pos_x = qr_width // 4 - logo_size // 2
        pos_y = qr_height // 4 - logo_size // 2
    elif position == 'top-right':
        pos_x = 3 * qr_width // 4 - logo_size // 2
        pos_y = qr_height // 4 - logo_size // 2
    elif position == 'bottom-left':
        pos_x = qr_width // 4 - logo_size // 2
        pos_y = 3 * qr_height // 4 - logo_size // 2
    elif position == 'bottom-right':
        pos_x = 3 * qr_width // 4 - logo_size // 2
        pos_y = 3 * qr_height // 4 - logo_size // 2
    else:  # Default to center
        pos_x = (qr_width - logo_size) // 2
        pos_y = (qr_height - logo_size) // 2
    
    # Paste the logo onto the QR code
    qr_img.paste(logo_img, (pos_x, pos_y), logo_img if logo_img.mode == 'RGBA' else None)
    
    return qr_img

def add_frame_and_text(qr_img, frame_color, text, text_color, frame_style='square', frame_width=50, 
                      font_size=20, font_family=None, text_position='bottom', include_logo=False, logo_url=None, add_timestamp=False):
    """Add frame and text to QR code with advanced customization"""
    # Convert to RGB if not already
    if qr_img.mode != 'RGB':
        qr_img = qr_img.convert('RGB')
    
    # Get QR code dimensions
    qr_width, qr_height = qr_img.size
    
    # Calculate new dimensions with frame
    new_width = qr_width + 2 * frame_width
    new_height = qr_height + 2 * frame_width
    
    # Add extra height for text if needed
    text_height = 0
    if text:
        text_height = font_size + 20  # Add some padding
        if text_position in ['top', 'bottom']:
            new_height += text_height
        else:  # left or right
            new_width += text_height
    
    # Create new image with frame
    if frame_style == 'square':
        framed_img = Image.new('RGB', (new_width, new_height), frame_color)
    elif frame_style == 'rounded':
        framed_img = Image.new('RGB', (new_width, new_height), frame_color)
        # We'll apply rounded corners later
    else:  # circle
        framed_img = Image.new('RGB', (new_width, new_height), frame_color)
        # We'll apply circular mask later
    
    # Paste QR code onto frame
    paste_x = frame_width
    paste_y = frame_width
    
    # Adjust paste position if text is at the top
    if text and text_position == 'top':
        paste_y += text_height
    
    framed_img.paste(qr_img, (paste_x, paste_y))
    
    # Add text if provided
    if text:
        try:
            # Try to load the specified font, fall back to default if not available
            if font_family:
                try:
                    font = ImageFont.truetype(font_family, font_size)
                except IOError:
                    font = ImageFont.load_default()
            else:
                # Use default font
                font = ImageFont.load_default()
            
            draw = ImageDraw.Draw(framed_img)
            
            # Calculate text position
            text_width, text_height_actual = draw.textsize(text, font=font)
            
            if text_position == 'bottom':
                text_x = (new_width - text_width) // 2
                text_y = qr_height + 2 * frame_width - text_height_actual // 2
            elif text_position == 'top':
                text_x = (new_width - text_width) // 2
                text_y = (text_height - text_height_actual) // 2
            elif text_position == 'left':
                text_x = (frame_width - text_width) // 2
                text_y = (new_height - text_height_actual) // 2
                # Rotate text for left position
                framed_img = framed_img.rotate(90, expand=True)
            elif text_position == 'right':
                text_x = qr_width + frame_width + (frame_width - text_width) // 2
                text_y = (new_height - text_height_actual) // 2
                # Rotate text for right position
                framed_img = framed_img.rotate(270, expand=True)
            
            # Add timestamp if requested
            if add_timestamp:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                timestamp_width, timestamp_height = draw.textsize(timestamp, font=ImageFont.load_default())
                
                if text_position in ['top', 'bottom']:
                    timestamp_x = new_width - timestamp_width - 10
                    timestamp_y = text_y + (text_height_actual if text_position == 'top' else -timestamp_height - 5)
                else:
                    timestamp_x = text_x
                    timestamp_y = text_y + text_height_actual + 5
                
                draw.text((timestamp_x, timestamp_y), timestamp, fill=text_color, font=ImageFont.load_default())
            
            # Draw the main text
            draw.text((text_x, text_y), text, fill=text_color, font=font)
            
        except Exception as e:
            print(f"Error adding text: {str(e)}")
    
    # Apply rounded corners if needed
    if frame_style == 'rounded':
        # Create a mask with rounded corners
        mask = Image.new('L', (new_width, new_height), 0)
        draw = ImageDraw.Draw(mask)
        radius = frame_width
        draw.rounded_rectangle([(0, 0), (new_width, new_height)], radius, fill=255)
        
        # Apply the mask
        framed_img.putalpha(mask)
    
    # Apply circular mask if needed
    if frame_style == 'circle':
        # Create a circular mask
        mask = Image.new('L', (new_width, new_height), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, new_width, new_height), fill=255)
        
        # Apply the mask
        framed_img.putalpha(mask)
    
    return framed_img

def create_qr_for_type(qr_type, content):
    """Create QR code data based on type with enhanced formatting"""
    # Validate and format content based on type
    formatted_data = ""
    
    if qr_type == "url":
        # Ensure URL has proper format
        if not content.startswith(('http://', 'https://')):
            content = 'https://' + content
        formatted_data = content
    
    elif qr_type == "email":
        # Format as email link
        if '@' in content:
            formatted_data = f"mailto:{content}"
        else:
            formatted_data = f"mailto:example@example.com?subject=Subject&body={content}"
    
    elif qr_type == "phone":
        # Format as phone link
        formatted_data = f"tel:{content.replace(' ', '')}"
    
    elif qr_type == "sms":
        # Format as SMS link
        if ':' in content:
            number, message = content.split(':', 1)
            formatted_data = f"smsto:{number.strip()}:{message.strip()}"
        else:
            formatted_data = f"smsto:{content.strip()}"
    
    elif qr_type == "wifi":
        # Format as WiFi network info
        try:
            # Parse JSON if provided
            if content.startswith('{') and content.endswith('}'):
                wifi_data = json.loads(content)
                ssid = wifi_data.get('ssid', '')
                password = wifi_data.get('password', '')
                security = wifi_data.get('security', 'WPA')
                
                formatted_data = f"WIFI:S:{ssid};T:{security};P:{password};;"
            else:
                # Try to parse as "ssid:password:security"
                parts = content.split(':')
                if len(parts) >= 2:
                    ssid = parts[0]
                    password = parts[1]
                    security = parts[2] if len(parts) > 2 else "WPA"
                    
                    formatted_data = f"WIFI:S:{ssid};T:{security};P:{password};;"
                else:
                    formatted_data = content
        except Exception as e:
            print(f"Error formatting WiFi data: {str(e)}")
            formatted_data = content
    
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
                
                formatted_data = f"""BEGIN:VCARD
VERSION:3.0
N:{name}
ORG:{org}
TEL:{phone}
EMAIL:{email}
URL:{url}
END:VCARD"""
            else:
                formatted_data = content
        except Exception as e:
            print(f"Error formatting vCard data: {str(e)}")
            formatted_data = content
    
    elif qr_type == "mecard":
        # Format as MeCard
        try:
            # Parse JSON if provided
            if content.startswith('{') and content.endswith('}'):
                mecard_data = json.loads(content)
                name = mecard_data.get('name', '')
                phone = mecard_data.get('phone', '')
                email = mecard_data.get('email', '')
                
                formatted_data = f"MECARD:N:{name};TEL:{phone};EMAIL:{email};;"
            else:
                formatted_data = content
        except Exception as e:
            print(f"Error formatting MeCard data: {str(e)}")
            formatted_data = content
    
    elif qr_type == "geo":
        # Format as geo location
        try:
            # Parse as "latitude,longitude"
            if ',' in content:
                lat, lon = content.split(',', 1)
                formatted_data = f"geo:{lat.strip()},{lon.strip()}"
            else:
                formatted_data = content
        except Exception as e:
            print(f"Error formatting geo data: {str(e)}")
            formatted_data = content
    
    elif qr_type == "calendar":
        # Format as calendar event
        try:
            # Parse JSON if provided
            if content.startswith('{') and content.endswith('}'):
                event_data = json.loads(content)
                summary = event_data.get('summary', '')
                start = event_data.get('start', '')
                end = event_data.get('end', '')
                location = event_data.get('location', '')
                
                formatted_data = f"""BEGIN:VEVENT
SUMMARY:{summary}
DTSTART:{start}
DTEND:{end}
LOCATION:{location}
END:VEVENT"""
            else:
                formatted_data = content
        except Exception as e:
            print(f"Error formatting calendar data: {str(e)}")
            formatted_data = content
    
    else:
        # For text or other types, use as is
        formatted_data = content
    
    # Generate QR code
    qr_img = generate_qr_code(formatted_data)
    
    # Return both the QR image and the formatted data
    return qr_img, formatted_data

def create_svg_qr(data, color='#000000', bg_color='#FFFFFF', size=300, margin=10):
    """Create SVG QR code with customization options"""
    # Generate QR code
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=margin // 10,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create SVG QR code
    factory = qrcode.image.svg.SvgFragmentImage
    svg_img = qr.make_image(fill_color=color, back_color=bg_color, image_factory=factory)
    
    # Get SVG as string
    svg_string = svg_img.to_string().decode('utf-8')
    
    # Modify SVG to add viewBox and size
    import re
    svg_string = re.sub(r'width="[^"]+"', f'width="{size}"', svg_string)
    svg_string = re.sub(r'height="[^"]+"', f'height="{size}"', svg_string)
    
    # Add viewBox if not present
    if 'viewBox' not in svg_string:
        svg_string = svg_string.replace('<svg', f'<svg viewBox="0 0 {size} {size}"')
    
    return svg_string

def upload_qr_to_cloudinary(qr_img):
    """Upload QR code image to Cloudinary and return the URL"""
    try:
        # Convert PIL Image to bytes
        img_byte_arr = io.BytesIO()
        qr_img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            img_byte_arr,
            folder="qr_codes",
            public_id=f"qr_{uuid.uuid4().hex[:8]}"
        )
        
        # Return the secure URL
        return result['secure_url']
    except Exception as e:
        print(f"Error uploading to Cloudinary: {str(e)}")
        return None
