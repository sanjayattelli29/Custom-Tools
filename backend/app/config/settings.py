import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Application settings
class Config:
    # Server settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    
    # Database settings
    MONGODB_URI = os.getenv('MONGODB_URI')
    DB_NAME = os.getenv('DB_NAME', 'qr_database')
    
    # Cloudinary settings
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')
    
    # CORS settings
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
    
    # JWT settings (if needed)
    JWT_SECRET = os.getenv('JWT_SECRET', 'your_jwt_secret_key_here')
    JWT_EXPIRATION = int(os.getenv('JWT_EXPIRATION', 86400))
    
    # QR code settings
    DEFAULT_QR_SIZE = 10
    DEFAULT_QR_BORDER = 4
    DEFAULT_QR_ERROR_CORRECTION = 'M'
    
    # URL shortener settings
    BASE_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size