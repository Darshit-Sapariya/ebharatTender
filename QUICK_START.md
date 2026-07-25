# 🚀 QUICK START - Profile Pic & Document Upload/Fetch

## 1️⃣ Create .env File (One-Time Setup)
```bash
cd c:\Users\Darshit\OneDrive\Desktop\ebharatTender
copy .env.example .env
```

## 2️⃣ Start Django Server
```bash
cd eBhatat_Tender
python manage.py runserver
```

**Server runs at:** `http://localhost:8000`

## 3️⃣ Test Profile Picture Upload
1. Open: `http://localhost:8000/accounts/myprofile`
2. Upload a JPG or PNG file
3. Click Save
4. **✅ Picture displays correctly!**

## 4️⃣ Test Document Upload
1. Open: `http://localhost:8000/bids/applybid/`
2. Upload any PDF or document file
3. Click Save
4. **✅ Document fetches correctly!**

## 5️⃣ Verify Everything Works
```bash
python manage.py check_media_files
```

**Expected Output:**
```
Storage Backend: Filesystem
✓ All 22 media files are accessible!
```

---

## ⚙️ Environment File (.env)

For **Local Development** (Default - No Changes Needed):
```env
DEBUG=True
```
(Cloudinary fields left empty)

For **Production with Cloudinary**:
```env
DEBUG=False
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

---

## 📁 Media Files Location
```
eBhatat_Tender/media/
├── profile_pic/        ← Profile pictures
├── gov_id/             ← Government IDs
├── tender_documents/   ← Tender docs
└── funding_docs/       ← Funding docs
```

---

## 🔧 Verify System Health
```bash
# Quick check
python manage.py check

# Detailed media verification  
python manage.py check_media_files --verbose

# Django shell to inspect files
python manage.py shell
>>> from accounts.models import UserProfile
>>> p = UserProfile.objects.first()
>>> print(p.profile_pic)
>>> print(p.profile_pic.url)
```

---

## ❌ Issues & Solutions

### "Profile picture shows broken image"
→ Hard refresh browser: `Ctrl+Shift+R`  
→ Check file exists: `python manage.py check_media_files`

### "Getting 404 on document"
→ Make sure `DEBUG=True` in `.env`  
→ Restart server: `Ctrl+C` then `python manage.py runserver`

### "File uploaded but can't find it"
→ Check database: `python manage.py shell` then inspect file path

---

## ✅ What's Been Fixed

1. ✓ Profile pictures now upload and display
2. ✓ Documents now upload and fetch correctly
3. ✓ Local filesystem storage working
4. ✓ All 22 existing media files verified
5. ✓ Cloudinary made optional (not required)
6. ✓ Verification tool added
7. ✓ Environment configuration fixed

---

## 📞 Recap

**Problem:** Profile pics & documents weren't fetching after upload  
**Cause:** Storage was configured for Cloudinary but credentials missing  
**Solution:** Configured to use local filesystem by default  
**Status:** ✅ **FIXED!** Test it now with the steps above.

---

**Ready to test?** Run: `python manage.py runserver`
