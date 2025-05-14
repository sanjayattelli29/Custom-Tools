import os
import pymongo
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv('DB_NAME', 'qr_database')

# Initialize MongoDB client
def get_db_client():
    """Get MongoDB client"""
    try:
        client = pymongo.MongoClient(MONGODB_URI)
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
        return None

# Database initialization functions
def init_analytics_db():
    """Initialize the analytics database"""
    try:
        client = get_db_client()
        if not client:
            return False
        
        db = client[DB_NAME]
        if 'qr_scans' not in db.list_collection_names():
            db.create_collection('qr_scans')
        
        return True
    except Exception as e:
        print(f"Error initializing analytics DB: {str(e)}")
        return False

def init_url_db():
    """Initialize the URL shortener database"""
    try:
        client = get_db_client()
        if not client:
            return False
        
        db = client[DB_NAME]
        if 'short_urls' not in db.list_collection_names():
            db.create_collection('short_urls')
        
        return True
    except Exception as e:
        print(f"Error initializing URL DB: {str(e)}")
        return False

# Analytics functions
def log_qr_scan(qr_id, user_agent=None, ip_address=None):
    """Log QR code scan to database"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        client = get_db_client()
        if not client:
            return False
        
        db = client[DB_NAME]
        db.qr_scans.insert_one({
            'id': qr_id,
            'url': "",
            'timestamp': timestamp,
            'user_agent': user_agent,
            'ip_address': ip_address
        })
        
        return True
    except Exception as e:
        print(f"Error logging scan: {str(e)}")
        return False

def get_analytics_data():
    """Get analytics data from database"""
    try:
        client = get_db_client()
        if not client:
            return []
        
        db = client[DB_NAME]
        
        # Check if collection exists, if not initialize it
        if 'qr_scans' not in db.list_collection_names():
            init_analytics_db()
            # Add sample data for testing
            db.qr_scans.insert_one({
                'id': 'test_id',
                'url': 'https://example.com',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'user_agent': 'Mozilla/5.0',
                'ip_address': '127.0.0.1'
            })
        
        # Get data
        rows = list(db.qr_scans.find().sort('timestamp', -1))
        
        # Process data
        data = []
        for row in rows:
            # Extract device info from user agent
            device = "Unknown"
            if row.get('user_agent'):
                if "Mobile" in str(row.get('user_agent')):
                    device = "Mobile"
                elif "Tablet" in str(row.get('user_agent')):
                    device = "Tablet"
                else:
                    device = "Desktop"
            
            data.append({
                'qr_id': row.get('id'),
                'url': row.get('url'),
                'timestamp': row.get('timestamp'),
                'user_agent': row.get('user_agent'),
                'ip_address': row.get('ip_address'),
                'device': device
            })
        
        return data
    except Exception as e:
        print(f"Error retrieving analytics data: {str(e)}")
        return []

# URL Shortener database functions
def store_short_url(short_id, original_url, short_url=None):
    """Store a short URL in the database"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        client = get_db_client()
        if not client:
            return False
        
        db = client[DB_NAME]
        db.short_urls.update_one(
            {'short_id': short_id},
            {'$set': {
                'short_id': short_id,
                'original_url': original_url,
                'created_at': timestamp,
                'scans': 0,
                'short_url': short_url
            }},
            upsert=True
        )
        
        return True
    except Exception as e:
        print(f"Error storing short URL: {str(e)}")
        return False

def get_original_url(short_id):
    """Get the original URL for a short ID"""
    try:
        client = get_db_client()
        if not client:
            return None
        
        db = client[DB_NAME]
        result = db.short_urls.find_one({'short_id': short_id})
        
        if result:
            # Update scan count
            db.short_urls.update_one(
                {'short_id': short_id},
                {'$inc': {'scans': 1}}
            )
            
            return result.get('original_url')
        
        return None
    except Exception as e:
        print(f"Error retrieving short URL: {str(e)}")
        return None

def get_all_short_urls():
    """Get all shortened URLs from the database"""
    try:
        client = get_db_client()
        if not client:
            return []
        
        db = client[DB_NAME]
        short_urls = list(db.short_urls.find().sort('created_at', -1))
        
        return [(url.get('short_id'), url.get('original_url'), url.get('created_at'), 
                url.get('scans'), url.get('short_url')) for url in short_urls]
    except Exception as e:
        print(f"Error retrieving short URLs: {str(e)}")
        return []

def update_original_url(short_id, new_url):
    """Update the destination URL for a short ID"""
    try:
        client = get_db_client()
        if not client:
            return False
        
        db = client[DB_NAME]
        db.short_urls.update_one(
            {'short_id': short_id},
            {'$set': {'original_url': new_url}}
        )
        
        return True
    except Exception as e:
        print(f"Error updating URL: {str(e)}")
        return False

# Initialize databases
def init_all_databases():
    init_analytics_db()
    init_url_db()
