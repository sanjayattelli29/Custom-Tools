# Import utility modules
from app.utils.db_utils import init_db_connection, store_scan, get_scans, store_url, get_url, get_all_urls, update_url
from app.utils.qr_utils import generate_qr_code, add_logo_to_qr, add_frame_and_text, create_qr_for_type
from app.utils.analytics_utils import log_qr_scan, get_analytics_data
from app.utils.shortener_utils import create_short_url, get_original_url, get_all_short_urls, update_original_url
from app.utils.cloudinary import upload_image, get_image_url, delete_image, optimize_image
