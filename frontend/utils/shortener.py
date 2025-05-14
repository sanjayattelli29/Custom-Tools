import requests
import uuid
import hashlib
from datetime import datetime
from urllib.parse import quote, urlparse
import os
from dotenv import load_dotenv
from frontend.utils.db import store_short_url, get_original_url

# Load environment variables
load_dotenv()

# Base URL for the application
BASE_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

def create_short_url(url):
    """Create a short URL using external URL shortener services"""
    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Try multiple URL shortener services in case one fails
    short_url = None
    error_message = ""
    
    # Option 1: TinyURL API
    try:
        tinyurl_api = f"https://tinyurl.com/api-create.php?url={quote(url)}"
        response = requests.get(tinyurl_api, timeout=5)
        if response.status_code == 200:
            short_url = response.text.strip()
    except Exception as e:
        error_message += f"TinyURL error: {str(e)}\n"
    
    # Option 2: Bitly-like service (is.gd)
    if not short_url:
        try:
            isgd_api = f"https://is.gd/create.php?format=simple&url={quote(url)}"
            response = requests.get(isgd_api, timeout=5)
            if response.status_code == 200:
                short_url = response.text.strip()
        except Exception as e:
            error_message += f"is.gd error: {str(e)}\n"
    
    # Option 3: v.gd service (similar to is.gd)
    if not short_url:
        try:
            vgd_api = f"https://v.gd/create.php?format=simple&url={quote(url)}"
            response = requests.get(vgd_api, timeout=5)
            if response.status_code == 200:
                short_url = response.text.strip()
        except Exception as e:
            error_message += f"v.gd error: {str(e)}\n"
    
    # Fallback to local shortener if all external services fail
    if not short_url:
        # Generate a unique short ID
        short_id = str(uuid.uuid4())[:8]
        short_url = f"{BASE_URL}/redirect/{short_id}"
        print(f"Using local shortener as fallback: {short_url}")
    
    # Store the external short URL in our database for tracking
    if short_url:
        short_id = hashlib.md5(short_url.encode()).hexdigest()[:8]
        store_short_url(short_id, url, short_url)
    
    return short_url

def get_redirect_url(short_id):
    """Get the original URL for a short ID from the database"""
    return get_original_url(short_id)
