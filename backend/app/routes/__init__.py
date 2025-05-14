# Import route blueprints
from app.routes.qr_routes import qr_bp
from app.routes.url_routes import url_bp
from app.routes.upload_routes import upload_bp

# List of all blueprints
blueprints = [qr_bp, url_bp, upload_bp]
