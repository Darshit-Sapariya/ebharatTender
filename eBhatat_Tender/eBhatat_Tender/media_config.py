"""
Media storage configuration for eBhatat_Tender project.
Handles both local filesystem and Cloudinary storage.

- DEBUG=True  -> Always use local filesystem (no Cloudinary needed)
- DEBUG=False -> Use Cloudinary if credentials are present, else filesystem
"""
import os
from pathlib import Path

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent.parent

def get_storage_config():
    """
    Returns the appropriate storage configuration based on environment variables.
    In DEBUG mode, always uses local filesystem storage.
    In production (DEBUG=False), uses Cloudinary if credentials are present.
    """

    # In local development (DEBUG=True), always use local filesystem
    is_debug = os.environ.get('DEBUG', 'True').lower() == 'true'

    if is_debug:
        # Local development: always use filesystem, skip Cloudinary entirely
        storages_config = {
            "default": {
                "BACKEND": "django.core.files.storage.FileSystemStorage",
            },
            "staticfiles": {
                "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
            },
        }
        return {
            'STORAGES': storages_config,
            'CLOUDINARY_STORAGE': {},
            'USE_CLOUDINARY': False,
        }

    # Production: Get Cloudinary credentials from environment
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

    # Cloudinary configuration
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

