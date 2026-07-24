from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.models import User

def update_user_profile(request, profile):
    """
    Standard service to update UserProfile and User model fields.
    Handles profile details and password changes.
    """
    # 1. Update Profile Fields (Conditional to avoid nullifying fields not in form)
    if 'full_name' in request.POST:
        profile.full_name = request.POST.get('full_name')
    if 'mobile' in request.POST:
        profile.mobile = request.POST.get('mobile')
    if 'address' in request.POST:
        profile.address = request.POST.get('address')
    if 'gov_id_type' in request.POST:
        profile.gov_id_type = request.POST.get('gov_id_type')
    if 'gov_id_number' in request.POST:
        profile.gov_id_number = request.POST.get('gov_id_number')
    
    # Optional fields or fields that might not be in all forms
    designation = request.POST.get('designation')
    if designation and not profile.designation:
        profile.designation = designation

    if request.FILES.get('profile_pic'):
        profile.profile_pic = request.FILES.get('profile_pic')
    if request.FILES.get('gov_id_upload'):
        profile.gov_id_upload = request.FILES.get('gov_id_upload')

    # Role lock
    if not profile.role:
        role = request.POST.get('role')
        if role:
            profile.role = role

    profile.status = "pending"
    profile.save()

    # 2. Update User Model Consistency
    user = User.objects.get(id=request.user.id)
    user_changed = False

    if 'full_name' in request.POST:
        new_name = request.POST.get('full_name')
        if new_name and new_name != user.first_name:
            user.first_name = new_name
            user_changed = True

    if 'email' in request.POST:
        new_email = request.POST.get('email')
        if new_email and new_email != user.email:
            if User.objects.filter(email=new_email).exclude(id=user.id).exists():
                messages.error(request, f"The email '{new_email}' is already registered to another account.")
                return False
            user.email = new_email
            user_changed = True
    
    if user_changed:
        user.save()

    # 3. Password Change Logic
    old_pw = request.POST.get("old_password")
    new_pw = request.POST.get("new_password")
    conf_pw = request.POST.get("confirm_password")

    if old_pw or new_pw or conf_pw:
        if not old_pw or not new_pw or not conf_pw:
            messages.error(request, "To change password, please fill in all password fields.")
            return False
        
        if not request.user.check_password(old_pw):
            messages.error(request, "Incorrect current password.")
            return False
        
        if new_pw != conf_pw:
            messages.error(request, "New passwords do not match.")
            return False
        
        if len(new_pw) < 8:
            messages.error(request, "New password must be at least 8 characters long.")
            return False

        request.user.set_password(new_pw)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, "Password changed successfully!")

    messages.success(request, "Profile updated successfully.")
    return True

def handle_user_onboarding(request, profile):
    """
    Handles the initial profile completion for new users.
    """
    profile.full_name = request.POST.get('full_name')
    profile.role = request.POST.get('role')
    profile.mobile = request.POST.get('mobile')
    profile.address = request.POST.get('address')
    profile.gov_id_type = request.POST.get('gov_id_type')
    profile.gov_id_number = request.POST.get('gov_id_number')
    
    if request.FILES.get('profile_pic'):
        profile.profile_pic = request.FILES.get('profile_pic')
    if request.FILES.get('gov_id_upload'):
        profile.gov_id_upload = request.FILES.get('gov_id_upload')
        
    profile.status = 'pending'
    profile.save()

    # Update username if changed
    new_username = request.POST.get('username')
    if new_username and new_username != request.user.username:
        if not User.objects.filter(username=new_username).exists():
            request.user.username = new_username
            request.user.save()
        else:
            messages.error(request, f"Username '{new_username}' is already taken.")
            return False
    
    # Hande password for social login users completing profile
    if not request.user.has_usable_password():
        pw = request.POST.get('password')
        conf_pw = request.POST.get('confirm_password')
        if pw and conf_pw:
            if pw == conf_pw:
                request.user.set_password(pw)
                request.user.save()
                update_session_auth_hash(request, request.user)
            else:
                messages.error(request, "Passwords do not match.")
                return False

    # Update email and first_name if changed
    user = User.objects.get(id=request.user.id)
    user_changed = False

    if profile.full_name and profile.full_name != user.first_name:
        user.first_name = profile.full_name
        user_changed = True

    new_email = request.POST.get('email')
    if new_email and new_email != user.email:
        if not User.objects.filter(email=new_email).exclude(id=user.id).exists():
            user.email = new_email
            user_changed = True
        else:
            messages.error(request, f"Email '{new_email}' is already taken.")
            return False

    if user_changed:
        user.save()

    return True
