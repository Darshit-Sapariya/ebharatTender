"""
Media utilities for handling file uploads and URLs correctly.
Ensures profile pictures and documents are properly served.
"""
from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse
import os


def get_media_url(file_field):
    """
    Get the correct URL for a media file field.
    Handles both Cloudinary and filesystem storage.
    
    Args:
        file_field: ImageField or FileField object from a Django model
    
    Returns:
        str: The correct URL to access the file
    """
    if not file_field or not str(file_field):
        return None
    
    try:
        # If using Cloudinary, file_field.url will return Cloudinary URL
        if getattr(settings, 'USE_CLOUDINARY', False):
            return file_field.url
        
        # For filesystem storage, construct proper media URL
        file_name = str(file_field)
        if file_name:
            return settings.MEDIA_URL + file_name
        return None
    except Exception as e:
        print(f"Error getting media URL: {e}")
        return None


def get_profile_pic_url(profile):
    """
    Get the profile picture URL for a UserProfile instance.
    
    Args:
        profile: UserProfile instance
    
    Returns:
        str: URL to the profile picture or default placeholder
    """
    if profile.profile_pic:
        url = get_media_url(profile.profile_pic)
        if url:
            return url
    
    # Return a default avatar placeholder
    return static('images/default-avatar.png')


def get_document_url(document_field):
    """
    Get the document URL for any FileField.
    
    Args:
        document_field: FileField object
    
    Returns:
        str: URL to the document or None
    """
    return get_media_url(document_field)


def verify_media_file_exists(file_field):
    """
    Verify that a media file actually exists on the filesystem.
    
    Args:
        file_field: ImageField or FileField object
    
    Returns:
        bool: True if file exists, False otherwise
    """
    if not file_field or not str(file_field):
        return False
    
    try:
        if getattr(settings, 'USE_CLOUDINARY', False):
            # Assume Cloudinary files are always available
            return True
        
        # Check filesystem
        file_path = os.path.join(settings.MEDIA_ROOT, str(file_field))
        return os.path.exists(file_path) and os.path.isfile(file_path)
    except Exception as e:
        print(f"Error verifying media file: {e}")
        return False


def get_file_size_display(file_field):
    """
    Get a human-readable file size.
    
    Args:
        file_field: FileField object
    
    Returns:
        str: Formatted file size (e.g., "2.5 MB")
    """
    if not file_field:
        return "0 B"
    
    try:
        size = file_field.size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
    except Exception:
        return "Unknown"
