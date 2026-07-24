from django.contrib import messages
from django.shortcuts import redirect, render
from accounts.models import UserProfile, Notification
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from .utils import send_ebharat_email
from django.contrib.sites.shortcuts import get_current_site
from .services import update_user_profile, handle_user_onboarding

# ==============================================================================
# AUTHENTICATION & NOTIFICATION VIEWS
# ==============================================================================

# Handles user login with support for both username and email
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("user_name")
        password = request.POST.get("password")

        # Allow login with email as well
        if username and '@' in username:
            try:
                user_obj = User.objects.get(email=username)
                username = user_obj.username
            except User.DoesNotExist:
                pass

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect("coreadmin:deshbord")
            return redirect("public:home")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("accounts:login")
    return render(request, "login.html")

# Marks all unread notifications for the logged-in user as read
@login_required
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', '/'))

# Deletes all notifications for the logged-in user
@login_required
def clear_notifications(request):
    Notification.objects.filter(user=request.user).delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))

# Renders a list of all notifications for the logged-in user
# Renders a list of all notifications for the logged-in user with filtering
@login_required
def view_all_notifications(request):
    status_filter = request.GET.get('status', 'all')
    notifications = Notification.objects.filter(user=request.user)

    if status_filter == 'read':
        notifications = notifications.filter(is_read=True)
    elif status_filter == 'unread':
        notifications = notifications.filter(is_read=False)

    all_notifications = notifications.order_by('-created_at')
    return render(request, "all_notifications.html", {
        "all_notifications": all_notifications,
        "current_status": status_filter
    })


# ==============================================================================
# PROFILE MANAGEMENT VIEWS
# ==============================================================================

# Handles the updating of user profile information and password
@login_required
def updateProfile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        if update_user_profile(request, profile):
            return redirect("accounts:updateProfile")
        return redirect("accounts:updateProfile")

    if profile.role == 'bidder':
        return redirect("bids:vendor_profile_update")
    elif profile.role == 'creator':
        return redirect("tenders:updateProfile")
    
    # Fallback if no role is set yet
    template_name = 'vendorsProfileupdate.html' if profile.role == 'creator' else 'bidersProfileupdate.html'
    return render(request, template_name, {'profile': profile})

# Log out the current user and redirect to login page
def logout_view(request):
    logout(request)
    return redirect("accounts:login")
# =======================
# PROFILE VIEW
# =======================
# Renders and handles personal KYC profile management
@login_required
def my_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # 🚩 Mandatory Onboarding Check (skip for superusers)
    if not request.user.is_superuser:
        if not profile.mobile or not profile.address or not profile.role:
            return redirect('accounts:complete_profile')

    if request.method == "POST":
        if update_user_profile(request, profile):
            return redirect('accounts:myprofile')
        return redirect('accounts:myprofile')

    # 🔹 After admin approval → auto redirect
    if profile.status == "approved":
        if profile.role == "creator":
            return redirect("tenders:dashboard")
        elif profile.role == "bidder":
            return redirect("bids:bids_dashboard")

    return render(request, "myprofile.html", {"profile": profile})

# Renders and handles the initial profile completion for new users
@login_required
def complete_profile(request):
    if request.user.is_superuser:
        return redirect('coreadmin:base')
        
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # If already completed, don't show this page again
    if profile.mobile and profile.address and profile.role:
        return redirect('accounts:myprofile')
        
    if request.method == "POST":
        if handle_user_onboarding(request, profile):
            messages.success(request, "Profile submitted for verification!")
            return redirect('accounts:myprofile')
        return redirect('accounts:complete_profile')
        
    return render(request, "complete_profile.html", {"profile": profile})

# ==============================================================================
# REGISTRATION VIEWS
# ==============================================================================
# AJAX view to check if a username is already taken
def check_username(request):
    username = request.GET.get('username', None)
    if username:
        taken = User.objects.filter(username=username).exists()
        return JsonResponse({'taken': taken})
    return JsonResponse({'taken': False})

# AJAX view to check if an email is already registered
def check_email(request):
    email = request.GET.get('email', None)
    if email:
        taken = User.objects.filter(email=email).exists()
        return JsonResponse({'taken': taken})
    return JsonResponse({'taken': False})

# Handles new user registration, including welcome email dispatch
def register(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Password match check
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("accounts:register")

        # Username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("accounts:register")

        # Email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("accounts:register")

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name
        )

        # 🔹 Update auto-created profile with registration data
        profile = user.userprofile
        profile.full_name = full_name
        profile.mobile = mobile
        profile.save()

        user.save()

        # 📧 Send Welcome Email
        try:
            current_site = get_current_site(request)
            send_ebharat_email(
                subject="Welcome to eBharat Tender Portal",
                template_name="welcome_email.html",
                context={
                    "full_name": full_name,
                    "username": username,
                    "email": email,
                    "mobile": mobile,
                    "domain": current_site.domain,
                },
                recipient_list=[email]
            )
        except Exception as e:
            # Log error but don't break registration
            print(f"Email failed: {e}")

        return redirect("accounts:login")

    return render(request, "register.html")