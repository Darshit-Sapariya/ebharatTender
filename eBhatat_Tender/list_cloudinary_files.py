#!/usr/bin/env python
"""
List all files uploaded to Cloudinary
"""
import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.api

load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

print("=" * 80)
print("CLOUDINARY FILES LISTING")
print("=" * 80)

try:
    # Get all resources (files) from Cloudinary
    result = cloudinary.api.resources(max_results=500)
    
    files = result.get('resources', [])
    print(f"\n✓ Total Files: {len(files)}\n")
    
    if not files:
        print("❌ No files found on Cloudinary")
    else:
        for i, file in enumerate(files, 1):
            print(f"{i}. {file['public_id']}")
            print(f"   URL: {file['secure_url']}")
            print(f"   Type: {file['type']} | Size: {file['bytes']} bytes")
            print(f"   Uploaded: {file['created_at']}")
            print()
            
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nMake sure your Cloudinary credentials are correct in .env")
