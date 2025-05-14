import os
import pymongo
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv('DB_NAME', 'qr_database')

# MongoDB client
client = None
db = None

def init_db_connection():
    """Initialize MongoDB connection"""
    global client, db
    try:
        client = pymongo.MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        
        # Create collections if they don't exist
        if 'qr_scans' not in db.list_collection_names():
            db.create_collection('qr_scans')
        
        if 'short_urls' not in db.list_collection_names():
            db.create_collection('short_urls')
        
        print(f"Connected to MongoDB: {DB_NAME}")
        return True
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
        return False

def get_db():
    """Get MongoDB database instance"""
    global db
    if db is None:
        init_db_connection()
    return db

# Analytics functions
def store_scan(qr_id, url="", user_agent=None, ip_address=None):
    """Store QR code scan in database"""
    try:
        db = get_db()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        db.qr_scans.insert_one({
            'qr_id': qr_id,
            'url': url,
            'timestamp': timestamp,
            'user_agent': user_agent,
            'ip_address': ip_address
        })
        
        return True
    except Exception as e:
        print(f"Error storing scan: {str(e)}")
        return False

def get_scans(qr_id=None):
    """Get QR code scans from database"""
    try:
        db = get_db()
        
        # If qr_id is provided, filter by it
        query = {'qr_id': qr_id} if qr_id else {}
        
        scans = list(db.qr_scans.find(query).sort('timestamp', -1))
        
        # Convert ObjectId to string for JSON serialization
        for scan in scans:
            if '_id' in scan:
                scan['_id'] = str(scan['_id'])
        
        return scans
    except Exception as e:
        print(f"Error retrieving scans: {str(e)}")
        return []

# URL Shortener functions
def store_url(short_id, original_url, short_url=None):
    """Store URL in database"""
    try:
        db = get_db()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
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
        print(f"Error storing URL: {str(e)}")
        return False

def get_url(short_id):
    """Get URL from database"""
    try:
        db = get_db()
        result = db.short_urls.find_one({'short_id': short_id})
        
        if result:
            # Increment scan count
            db.short_urls.update_one(
                {'short_id': short_id},
                {'$inc': {'scans': 1}}
            )
            
            # Convert ObjectId to string for JSON serialization
            if '_id' in result:
                result['_id'] = str(result['_id'])
            
            return result
        
        return None
    except Exception as e:
        print(f"Error retrieving URL: {str(e)}")
        return None

def get_all_urls():
    """Get all URLs from database"""
    try:
        db = get_db()
        urls = list(db.short_urls.find().sort('created_at', -1))
        
        # Convert ObjectId to string for JSON serialization
        for url in urls:
            if '_id' in url:
                url['_id'] = str(url['_id'])
        
        return urls
    except Exception as e:
        print(f"Error retrieving URLs: {str(e)}")
        return []

def update_url(short_id, new_url):
    """Update URL in database"""
    try:
        db = get_db()
        result = db.short_urls.update_one(
            {'short_id': short_id},
            {'$set': {'original_url': new_url}}
        )
        
        return result.modified_count > 0
    except Exception as e:
        print(f"Error updating URL: {str(e)}")
        return False
