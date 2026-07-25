"""
Media storage configuration for eBhatat_Tender project.
Handles both local filesystem and Cloudinary storage.
"""
import os
from pathlib import Path

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent.parent

def get_storage_config():
    """
    Returns the appropriate storage configuration based on environment variables.
    By default, uses local filesystem storage. Set Cloudinary credentials in .env to use cloud storage.
    """
    
    # Get Cloudinary credentials from environment
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', '').strip()
    api_key = os.environ.get('CLOUDINARY_API_KEY', '').strip()
    api_secret = os.environ.get('CLOUDINARY_API_SECRET', '').strip()
    
    # Check if cloudinary packages are actually installed
    try:
        import cloudinary_storage
        import cloudinary
        cloudinary_available = True
    except ImportError:
        cloudinary_available = False
    
    # Determine if we should use Cloudinary
    # Must have credentials AND packages must be available
    use_cloudinary = bool(cloud_name and api_key and api_secret and cloudinary_available)
    
    # Storage configuration
    storages_config = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"
            if use_cloudinary
            else "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }
    
    # Cloudinary configuration (even if not used, it won't hurt)
    cloudinary_storage_config = {
        'CLOUD_NAME': cloud_name,
        'API_KEY': api_key,
        'API_SECRET': api_secret,
    }
    
    return {
        'STORAGES': storages_config,
        'CLOUDINARY_STORAGE': cloudinary_storage_config,
        'USE_CLOUDINARY': use_cloudinary,
    }

