from flask import Flask, jsonify
from flask_cors import CORS
import os
from datetime import datetime
from dotenv import load_dotenv
import cloudinary
from app.routes.qr_routes import qr_bp
from app.routes.url_routes import url_bp
from app.routes.upload_routes import upload_bp
from app.utils.db_utils import init_db_connection

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure CORS
    allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
    CORS(app, resources={r"/api/*": {"origins": allowed_origins}})
    
    # Initialize database connection
    init_db_connection()
    
    # Register blueprints
    app.register_blueprint(qr_bp, url_prefix='/api/qr')
    app.register_blueprint(url_bp, url_prefix='/api/url')
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    
    # Root route
    @app.route('/')
    def index():
        return jsonify({
            "message": "QR Code Generator API",
            "version": "1.0.0",
            "status": "running"
        })
    
    return app

app = create_app()

# Add this route for health checks (important for Render.com)
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# This is used by Render.com to detect the app
@app.route('/render')
def render_info():
    return jsonify({
        "service": "QR Code Generator API",
        "version": "1.0.0",
        "render": True,
        "environment": os.getenv('FLASK_ENV', 'production')
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
