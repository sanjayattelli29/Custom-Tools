import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Backend API URL
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')

def get_api_url(endpoint):
    """Get full API URL for an endpoint"""
    return f"{BACKEND_URL}/api/{endpoint}"

def handle_response(response):
    """Handle API response and return appropriate data"""
    try:
        if response.status_code in (200, 201):
            return response.json()
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return {"error": f"API Error: {response.status_code}"}
    except Exception as e:
        print(f"Error handling API response: {str(e)}")
        return {"error": str(e)}

# QR Code API functions
def generate_qr_code(data, options=None):
    """Generate QR code via API"""
    try:
        payload = {
            "data": data,
            "options": options or {}
        }
        response = requests.post(
            get_api_url("qr/generate"),
            json=payload
        )
        return handle_response(response)
    except Exception as e:
        print(f"Error generating QR code: {str(e)}")
        return {"error": str(e)}

def get_qr_analytics(qr_id=None):
    """Get QR code analytics data"""
    try:
        endpoint = f"analytics/{qr_id}" if qr_id else "analytics"
        response = requests.get(get_api_url(endpoint))
        return handle_response(response)
    except Exception as e:
        print(f"Error getting analytics: {str(e)}")
        return {"error": str(e)}

# URL Shortener API functions
def create_short_url_api(url):
    """Create short URL via API"""
    try:
        payload = {"url": url}
        response = requests.post(
            get_api_url("url/shorten"),
            json=payload
        )
        return handle_response(response)
    except Exception as e:
        print(f"Error creating short URL: {str(e)}")
        return {"error": str(e)}

def get_all_short_urls_api():
    """Get all shortened URLs via API"""
    try:
        response = requests.get(get_api_url("url/all"))
        return handle_response(response)
    except Exception as e:
        print(f"Error getting short URLs: {str(e)}")
        return {"error": str(e)}

def update_short_url_api(short_id, new_url):
    """Update short URL destination via API"""
    try:
        payload = {"new_url": new_url}
        response = requests.put(
            get_api_url(f"url/{short_id}"),
            json=payload
        )
        return handle_response(response)
    except Exception as e:
        print(f"Error updating short URL: {str(e)}")
        return {"error": str(e)}

# Cloudinary API functions
def upload_image_api(image_data):
    """Upload image to Cloudinary via API"""
    try:
        files = {'image': image_data}
        response = requests.post(
            get_api_url("upload/image"),
            files=files
        )
        return handle_response(response)
    except Exception as e:
        print(f"Error uploading image: {str(e)}")
        return {"error": str(e)}
