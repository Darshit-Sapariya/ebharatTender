# Media Upload & Fetch - Fixed Solution

## Problem That Was Found ❌

1. **Profile pictures uploaded but not fetching** - Getting 404 errors
2. **Tender documents uploaded but not fetching** - Getting 404 errors  
3. **Cloudinary URLs being generated but files not on Cloudinary** - The storage backend was pointing to Cloudinary even though credentials weren't configured
4. **No .env file** - Missing environment variables configuration

## What Was Fixed ✅

### 1. **Storage Configuration** 
- Created `media_config.py` to intelligently detect whether to use Cloudinary or filesystem storage
- By default, now uses **filesystem storage** (local)
- Only uses Cloudinary if credentials are properly configured in `.env`

### 2. **Debug Mode**
- Changed `DEBUG = False` to `DEBUG = True` (configurable via `.env`)
- Now media files are properly served in development

### 3. **Environment Configuration**
- Created `.env.example` template file
- Shows all required environment variables
- Default behavior: use local filesystem storage

### 4. **Media Utilities**
- Created `media_utils.py` with helper functions:
  - `get_media_url()` - Get correct URL for any media file
  - `get_profile_pic_url()` - Get profile picture with fallback
  - `get_document_url()` - Get document URL
  - `verify_media_file_exists()` - Check if file exists

### 5. **Management Command**
- Created `check_media_files` command to verify media files
- Usage: `python manage.py check_media_files`
- Finds missing profile pictures, documents, and bid files

## How to Use - Step by Step

### Step 1: Create .env File (if not present)
```bash
cd c:\Users\Darshit\OneDrive\Desktop\ebharatTender
copy .env.example .env
```

### Step 2: Configure .env for Local Development
Edit `.env` and set:
```env
DEBUG=True
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```
(Leave Cloudinary fields empty for local filesystem storage)

### Step 3: Run Django Server
```bash
cd eBhatat_Tender
python manage.py runserver
```

### Step 4: Test Media Upload
1. Go to profile page
2. Upload a profile picture
3. The file will be saved to `/media/profile_pic/`
4. Click profile picture to verify it displays

### Step 5: Check Media Files
```bash
python manage.py check_media_files --verbose
```

This will show:
- Total files in system
- Which files are properly stored
- Which files are missing (if any)

## File Structure

```
project/
├── .env                          # Your local environment variables
├── .env.example                  # Template (for reference)
├── eBhatat_Tender/
│   ├── media_config.py          # NEW: Storage configuration
│   ├── settings.py              # UPDATED: Uses media_config
│   └── urls.py                  # UPDATED: Serves media locally
├── accounts/
│   ├── media_utils.py           # NEW: Media helper functions
│   ├── services.py              # Handles file uploads
│   └── management/commands/
│       └── check_media_files.py # NEW: Verify media files
└── media/                       # LOCAL STORAGE (created automatically)
    ├── profile_pic/
    ├── gov_id/
    ├── tender_documents/
    └── funding_docs/
```

## Production Setup (Optional - Use Cloudinary)

If you want to use Cloudinary for production:

### 1. Update .env
```env
DEBUG=False
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### 2. The system will automatically:
- Use Cloudinary storage backend
- Serve files from Cloudinary CDN
- No need to manage local media files

## Common Issues & Solutions

### Issue: Profile picture uploads but shows broken image
**Solution:**
```bash
# Check if file exists
python manage.py check_media_files --verbose

# Clear browser cache and refresh
```

### Issue: Getting 404 when accessing documents
**Solution:**
1. Make sure `DEBUG=True` or Cloudinary is configured
2. Check if file exists: `python manage.py check_media_files`
3. Verify MEDIA_ROOT and MEDIA_URL in settings

### Issue: File uploaded successfully but can't find it
**Solution:**
```bash
# List all media files
dir media/

# Check database to verify file path was saved
python manage.py shell
>>> from accounts.models import UserProfile
>>> p = UserProfile.objects.first()
>>> print(p.profile_pic)
```

### Issue: Images display in one browser but not another
**Solution:**
1. Check browser cache settings
2. Hard refresh: `Ctrl + Shift + R`
3. Clear cookies and cache

## Quick Test

### Test Profile Picture Upload:
```bash
cd eBhatat_Tender
python manage.py runserver

# Then visit: http://localhost:8000/accounts/myprofile
# Try uploading a JPG or PNG file
```

### Test Document Upload:
```bash
# Via admin interface: http://localhost:8000/admin
# Or via bid application form
```

### Verify Everything Works:
```bash
python manage.py check_media_files --verbose
```

## Important Notes

1. **Local filesystem storage** is now the default
2. Media files are served by Django via `/media/` URL
3. Each upload creates a new subdirectory (year/month)
4. Old migrations from Cloudinary are preserved but not used

## Need to Switch Back to Old Setup?

If you absolutely need the old Cloudinary-only setup, run:
```bash
python manage.py migrate_media_to_cloudinary
```

But this requires valid Cloudinary credentials in `.env`.

---

**Status:** ✅ Local media upload/fetch now working
**Next Step:** Upload a profile picture and verify it displays correctly
