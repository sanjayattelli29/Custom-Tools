import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

def upload_image(image_data, folder="uploads", public_id=None):
    """Upload an image to Cloudinary"""
    try:
        upload_result = cloudinary.uploader.upload(
            image_data,
            folder=folder,
            public_id=public_id
        )
        return upload_result
    except Exception as e:
        print(f"Error uploading to Cloudinary: {str(e)}")
        return None

def get_image_url(public_id, **options):
    """Get a Cloudinary URL for an image with transformations"""
    try:
        return cloudinary.utils.cloudinary_url(public_id, **options)[0]
    except Exception as e:
        print(f"Error generating Cloudinary URL: {str(e)}")
        return None

def delete_image(public_id):
    """Delete an image from Cloudinary"""
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get('result') == 'ok'
    except Exception as e:
        print(f"Error deleting from Cloudinary: {str(e)}")
        return False

def optimize_image(public_id, width=None, height=None, crop=None, quality="auto", format="auto"):
    """Optimize an image using Cloudinary transformations"""
    options = {
        'fetch_format': format,
        'quality': quality
    }
    
    if width:
        options['width'] = width
    
    if height:
        options['height'] = height
    
    if crop:
        options['crop'] = crop
    
    return get_image_url(public_id, **options)