import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("CLOUDINARY CREDENTIALS CHECK")
print("=" * 60)

cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME', '').strip()
api_key = os.getenv('CLOUDINARY_API_KEY', '').strip()
api_secret = os.getenv('CLOUDINARY_API_SECRET', '').strip()

print(f"CLOUDINARY_CLOUD_NAME: {repr(cloud_name)}")
print(f"CLOUDINARY_API_KEY: {repr(api_key[:20])}..." if api_key else f"CLOUDINARY_API_KEY: {repr(api_key)}")
print(f"CLOUDINARY_API_SECRET: {repr(api_secret[:20])}..." if api_secret else f"CLOUDINARY_API_SECRET: {repr(api_secret)}")

print("\n" + "=" * 60)
print("PACKAGE CHECK")
print("=" * 60)

try:
    import cloudinary_storage
    print("✓ cloudinary_storage: INSTALLED")
except ImportError as e:
    print(f"✗ cloudinary_storage: NOT INSTALLED ({e})")

try:
    import cloudinary
    print("✓ cloudinary: INSTALLED")
except ImportError as e:
    print(f"✗ cloudinary: NOT INSTALLED ({e})")

print("\n" + "=" * 60)
print("STORAGE CONFIG")
print("=" * 60)

from eBhatat_Tender.media_config import get_storage_config
cfg = get_storage_config()
print(f"USE_CLOUDINARY: {cfg['USE_CLOUDINARY']}")
print(f"Storage Backend: {cfg['STORAGES']['default']['BACKEND']}")

print("\n" + "=" * 60)
print("DIAGNOSIS")
print("=" * 60)

if not cloud_name:
    print("❌ CLOUDINARY_CLOUD_NAME is empty or missing")
if not api_key:
    print("❌ CLOUDINARY_API_KEY is empty or missing")
if not api_secret:
    print("❌ CLOUDINARY_API_SECRET is empty or missing")

if cloud_name and api_key and api_secret:
    print("✓ All credentials present")
    try:
        import cloudinary_storage, cloudinary
        print("✓ All packages installed")
        print("\n✅ CLOUDINARY SHOULD BE ENABLED!")
    except ImportError:
        print("❌ Some packages missing - need to install cloudinary and django-cloudinary-storage")
