from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Sum, Q
from tenders.models import Tenderss
from bids.models import TenderApplication
from accounts.models import UserProfile, AdminRequest, Category, Department, Notification
from funding.models import Funding, FundingApplication
from .models import ActionLog, Notice, ImportantEvent
from public.models import Enquiry
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from accounts.utils import send_ebharat_email
from django.contrib.sites.shortcuts import get_current_site
import calendar
import json
from .services import get_dashboard_stats, calculate_delta
from .utils import generate_system_report_pdf

# Create your views here.
# Renders the base administrative template for the core admin
@staff_member_required
def coreadmin_dashboard_base(request):
    return render(request, 'coreadmin_base.html')

# No longer needed here as it's moved to services.py

# Renders the main administrative dashboard with system-wide analytics
@staff_member_required
def coreadmin_dashboard(request):
    # --- STATISTICS ---
    stats = get_dashboard_stats()
    
    # Audit Logs (specific to dashboard view)
    recent_activity = ActionLog.objects.order_by('-timestamp')[:5]
    
    # Sidebar Badges
    pending_funding_count = FundingApplication.objects.filter(status='pending').count()
    pending_admin_req_count = AdminRequest.objects.filter(status='pending').count()


    # --- COMBINED PENDING LIST ---
    combined_pending = []
    for u in UserProfile.objects.filter(status='pending').exclude(user__is_superuser=True).exclude(user__is_staff=True).order_by('-created_at')[:5]:
        combined_pending.append({'type': 'user', 'obj': u, 'date': u.created_at})
    for a in TenderApplication.objects.filter(status='pending').order_by('-applied_at')[:5]:
        combined_pending.append({'type': 'bid', 'obj': a, 'date': a.applied_at})
    for f in FundingApplication.objects.filter(status='pending').order_by('-applied_at')[:5]:
        combined_pending.append({'type': 'funding', 'obj': f, 'date': f.applied_at})
    for r in AdminRequest.objects.filter(status='pending').order_by('-created_at')[:5]:
        combined_pending.append({'type': 'admin_req', 'obj': r, 'date': r.created_at})
    
    combined_pending.sort(key=lambda x: x['date'], reverse=True)

    # --- RECENT TENDERS ---
    recent_tenders_list = Tenderss.objects.order_by('-created_at')[:5]
    
    context = {
        'page_title': 'Dashboard',
        **stats,
        'recent_activity': recent_activity,
        'combined_pending': combined_pending,
        'recent_tenders': recent_tenders_list,
        'pending_funding_count': pending_funding_count,
        'pending_admin_req_count': pending_admin_req_count,
    }
    
    # Add absolute deltas for UI arrows
    for key in list(context.keys()):
        if key.endswith('_delta'):
            context[f"{key}_abs"] = abs(context[key])

    return render(request, 'deshbord.html', context)

# --- APPROVAL SYSTEM VIEWS ---

# Renders a list of users awaiting profile verification
@staff_member_required
def user_approvals(request):
    pending_users = UserProfile.objects.filter(status='pending').exclude(user__is_superuser=True).exclude(user__is_staff=True).order_by('-created_at')
    approved_users = UserProfile.objects.filter(status='approved').order_by('-created_at')[:20]
    return render(request, 'approvals.html', {
        'page_title': 'User Approvals',
        'pending_users': pending_users,
        'approved_users': approved_users,
        'type': 'users'
    })

# Renders a list of tender bid applications awaiting administrative approval
@staff_member_required
def application_approvals(request):
    pending_apps = TenderApplication.objects.filter(status='pending').order_by('-applied_at')
    approved_apps = TenderApplication.objects.filter(status='approved').order_by('-applied_at')[:20]
    return render(request, 'approvals.html', {
        'page_title': 'Tender Approvals',
        'pending_apps': pending_apps,
        'approved_apps': approved_apps,
        'type': 'applications'
    })

# Approves a user's pending profile and assigns their role
@staff_member_required
def approve_user(request, profile_id):
    if request.method == 'POST':
        profile = get_object_or_404(UserProfile, id=profile_id)
        role = request.POST.get('role')
        remark = request.POST.get('remark', '')
        
        profile.status = 'approved'
        if role:
            profile.role = role
        profile.admin_remark = remark
        profile.save()
        
        # Also create a notification
        Notification.objects.create(
            user=profile.user,
            message=f"Your account has been approved as {profile.get_role_display()}."
        )
        
        ActionLog.objects.create(
            admin_user=request.user,
            action_type="USER_APPROVAL",
            target_user=profile.user,
            description=f"Approved user {profile.user.username} with role {profile.get_role_display() or 'None'}." + (f" Remark: {remark}" if remark else "")
        )
        messages.success(request, f"User {profile.user.username} approved successfully.")

        # 📧 Send Status Email
        try:
            current_site = get_current_site(request)
            send_ebharat_email(
                subject="Account Approved",
                template_name="status_update_notification.html",
                context={
                    "user_name": profile.user.first_name or profile.user.username,
                    "activity_name": "Account Registration",
                    "item_name": f"Verification as {profile.get_role_display()}",
                    "status": "approved",
                    "remark": remark,
                    "domain": current_site.domain,
                },
                recipient_list=[profile.user.email]
            )
        except Exception as e:
            print(f"User Approval Email failed: {e}")
    return redirect('coreadmin:user_approvals')

# Rejects a user's pending profile with an administrative remark
@staff_member_required
def reject_user(request, profile_id):
    if request.method == 'POST':
        profile = get_object_or_404(UserProfile, id=profile_id)
        remark = request.POST.get('remark', '')
        
        profile.status = 'rejected'
        profile.admin_remark = remark
        profile.save()
        
        ActionLog.objects.create(
            admin_user=request.user,
            action_type="USER_REJECTION",
            target_user=profile.user,
            description=f"Rejected user {profile.user.username}." + (f" Remark: {remark}" if remark else "")
        )
        messages.warning(request, f"User {profile.user.username} rejected.")

        # 📧 Send Status Email
        try:
            current_site = get_current_site(request)
            send_ebharat_email(
                subject="Account Verification Status Update",
                template_name="status_update_notification.html",
                context={
                    "user_name": profile.user.first_name or profile.user.username,
                    "activity_name": "Account Registration",
                    "item_name": "Profile Verification",
                    "status": "rejected",
                    "remark": remark,
                    "domain": current_site.domain,
                },
                recipient_list=[profile.user.email]
            )
        except Exception as e:
            print(f"User Rejection Email failed: {e}")
    return redirect('coreadmin:user_approvals')

# Approves a specific tender bid application
@staff_member_required
def approve_application(request, app_id):
    if request.method == 'POST':
        application = get_object_or_404(TenderApplication, id=app_id)
        remark = request.POST.get('remark', '')
        
        application.status = 'approved'
        application.remark = remark
        application.save()
        
        messages.success(request, f"Application for {application.tender.title} approved.")

        # 📧 Send Status Email
        try:
            current_site = get_current_site(request)
            send_ebharat_email(
                subject=f"Bid Approved - {application.tender.title}",
                template_name="status_update_notification.html",
                context={
                    "user_name": application.user.first_name or application.user.username,
                    "activity_name": "Tender Bid Application",
                    "item_name": application.tender.title,
                    "status": "approved",
                    "remark": remark,
                    "domain": current_site.domain,
                },
                recipient_list=[application.user.email]
            )
        except Exception as e:
            print(f"Bid Approval Email failed: {e}")
    return redirect('coreadmin:application_approvals')

# Rejects a tender bid application and initiates payment refund if applicable
@staff_member_required
def reject_application(request, app_id):
    if request.method == 'POST':
        application = get_object_or_404(TenderApplication, id=app_id)
        remark = request.POST.get('remark', '')
        
        application.status = 'rejected'
        application.remark = remark
        
        # PROMPT: reject bit = return payment
        if application.payment_status == 'paid':
            application.payment_status = 'refunded'
            messages.info(request, f"Payment for {application.company_name} has been marked for refund.")
            
        application.save()
        
        ActionLog.objects.create(
            admin_user=request.user,
            action_type="BID_REJECTION",
            description=f"Rejected bid from {application.company_name} for tender {application.tender.tender_id}. Payment Status: {application.payment_status}"
        )
        
        messages.warning(request, f"Application for {application.tender.title} rejected.")

        # 📧 Send Status Email
        try:
            current_site = get_current_site(request)
            send_ebharat_email(
                subject=f"Bid Application Status Update - {application.tender.title}",
                template_name="status_update_notification.html",
                context={
                    "user_name": application.user.first_name or application.user.username,
                    "activity_name": "Tender Bid Application",
                    "item_name": application.tender.title,
                    "status": "rejected",
                    "remark": remark,
                    "domain": current_site.domain,
                },
                recipient_list=[application.user.email]
            )
        except Exception as e:
            print(f"Bid Rejection Email failed: {e}")
    return redirect('coreadmin:application_approvals')

# Renders a list of funding applications awaiting administrative approval
@staff_member_required
def funding_approvals(request):
    pending_apps = FundingApplication.objects.filter(status='pending').order_by('-applied_at')
    approved_apps = FundingApplication.objects.filter(status='approved').order_by('-applied_at')[:20]
    return render(request, 'approvals.html', {
        'page_title': 'Funding Approvals',
        'pending_funding': pending_apps,
        'approved_funding': approved_apps,
        'type': 'funding'
    })

# Approves a funding application and generates an award PDF for the bidder
@staff_member_required
def approve_funding_app(request, app_id):
    if request.method == 'POST':
        app = get_object_or_404(FundingApplication, id=app_id)
        remark = request.POST.get('remark', '')
        
        app.status = 'approved'
        app.admin_remark = remark
        app.save()
        
        Notification.objects.create(
            user=app.bidder,
            message=f"Your Funding Application for {app.funding.title} has been APPROVED."
        )
        
        messages.success(request, f"Funding application from {app.bidder.username} approved.")

        # 📧 Send Status Email + PDF Attach
        try:
            from funding.utils import generate_funding_award_pdf
            pdf_content = generate_funding_award_pdf(app)
            pdf_attachment = {
                'filename': f'eBharat_Funding_Approval_{app.id}.pdf',
                'content': pdf_content,
                'mimetype': 'application/pdf'
            }
            
            from django.utils import timezone
            current_site = get_current_site(request)
            send_ebharat_email(
                subject=f"Funding Approved - {app.funding.title}",
                template_name="funding_awarded.html",
                context={
                    "bidder_name": app.bidder.first_name or app.bidder.username,
                    "funding_title": app.funding.title,
                    "amount_requested": app.amount_requested,
                    "tender_title": app.tender.title,
                    "tender_id": app.tender.tender_id,
                    "approval_date": timezone.now().strftime("%d %B %Y"),
                    "domain": current_site.domain,
                },
                recipient_list=[app.bidder.email],
                attachments=[pdf_attachment]
            )
        except Exception as e:
            print(f"Funding Approval Email failed: {e}")
    return redirect('coreadmin:funding_approvals')

# Rejects a funding application with an administrative remark
@staff_member_required
def reject_funding_app(request, app_id):
    if request.method == 'POST':
        app = get_object_or_404(FundingApplication, id=app_id)
        remark = request.POST.get('remark', '')
        
        app.status = 'rejected'
        app.admin_remark = remark
        app.save()
        
        Notification.objects.create(
            user=app.bidder,
            message=f"Your Funding Application for {app.funding.title} has been REJECTED."
        )
        
        messages.warning(request, f"Funding application from {app.bidder.username} rejected.")

        # 📧 Send Status Email
        try:
            current_site = get_current_site(request)
            send_ebharat_email(
                subject=f"Funding Application Status Update - {app.funding.title}",
                template_name="status_update_notification.html",
                context={
                    "user_name": app.bidder.first_name or app.bidder.username,
                    "activity_name": "Funding Application",
                    "item_name": app.funding.title,
                    "status": "rejected",
                    "remark": remark,
                    "domain": current_site.domain,
                },
                recipient_list=[app.bidder.email]
            )
        except Exception as e:
            print(f"Funding Rejection Email failed: {e}")
    return redirect('coreadmin:funding_approvals')

# --- USER LIST MANAGEMENT ---

# Displays a manageable list of all registered users, filterable by role
@staff_member_required
def user_list(request):
    role = request.GET.get('role', 'all')
    if role == 'bidder':
        profiles = UserProfile.objects.filter(role='bidder')
    elif role == 'creator':
        profiles = UserProfile.objects.filter(role='creator')
    else:
        profiles = UserProfile.objects.all()
    
    return render(request, 'user_list.html', {
        'page_title': 'User Management',
        'profiles': profiles,
        'current_role': role
    })

# Allows superusers to create new internal staff accounts (is_staff=True)
@user_passes_test(lambda u: u.is_superuser)
def create_staff(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_staff = True
            user.first_name = full_name # Use first_name for the full name instead of profile
            user.save()
            
            ActionLog.objects.create(
                admin_user=request.user,
                action_type="STAFF_CREATION",
                target_user=user,
                description=f"Created staff account for {full_name} ({username})."
            )
            
            messages.success(request, f"Staff account for {full_name} created successfully.")

            # 📧 Send Welcome/Staff Creation Email
            try:
                current_site = get_current_site(request)
                send_ebharat_email(
                    subject="Your Staff Account has been Created",
                    template_name="welcome_email.html",
                    context={
                        "full_name": full_name,
                        "username": username,
                        "email": email,
                        "mobile": "N/A", # Staff creation doesn't capture mobile by default
                        "domain": current_site.domain,
                    },
                    recipient_list=[email]
                )
            except Exception as e:
                print(f"Staff Email failed: {e}")
            return redirect('coreadmin:user_list')
            
    return render(request, 'create_staff.html', {'page_title': 'Create Staff Account'})

# --- TENDER LIST MANAGEMENT ---

# Renders a comprehensive directory of all tenders and their award statuses
@staff_member_required
def tender_list(request):
    all_tenders = Tenderss.objects.all().order_by('-created_at')
    
    # We want to show which tender who public and how many bid who awards
    tenders_data = []
    for tender in all_tenders:
        applications = tender.applications.all()
        bid_count = applications.count()
        awardee = applications.filter(status='awarded').first()
        tenders_data.append({
            'obj': tender,
            'bid_count': bid_count,
            'applications': applications,
            'awardee': awardee,
            # We also pass formatted awardee name for quick reference
            'awardee_name': awardee.company_name if awardee else "None",
            'publisher': tender.created_by.username # WHO publish
        })
    
    return render(request, 'tender_list.html', {
        'page_title': 'Tender Directory',
        'tenders': tenders_data
    })

# Displays all bid applications for a specific tender, including awardee if any
@staff_member_required
def tender_bidders(request, tender_id):
    tender = get_object_or_404(Tenderss, id=tender_id)
    applications = tender.applications.all().order_by('-applied_at')
    
    return render(request, 'tender_bidders.html', {
        'page_title': f'Bidders for TND-{tender.id:04d}',
        'tender': tender,
        'applications': applications,
        'bid_count': applications.count(),
        'awardee': applications.filter(status='awarded').first()
    })

# --- FUNDING MANAGEMENT ---

# Manages the list of available funding schemes
@login_required
def funding_list(request):
    fundings = Funding.objects.all().order_by('-created_at')
    return render(request, 'funding_list.html', {'page_title': 'Manage Funding Schemes', 'fundings': fundings})

# Allows creators to define and publish new funding schemes linked to tenders
@login_required
def create_funding(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        max_amount = request.POST.get('max_amount')
        interest_rate = request.POST.get('interest_rate')
        tender_id = request.POST.get('tender_id')
        
        tender = None
        if tender_id:
            try:
                tender = Tenderss.objects.get(id=tender_id)
            except Tenderss.DoesNotExist:
                messages.error(request, "Selected Tender does not exist.")
                return redirect('coreadmin:create_funding')
                
        Funding.objects.create(
            title=title,
            description=description,
            max_amount=max_amount,
            interest_rate=interest_rate,
            tender=tender
        )
        messages.success(request, f"Funding scheme '{title}' created successfully.")
        return redirect('coreadmin:funding_list')
        
    tenders = Tenderss.objects.filter(status='open')
    return render(request, 'create_funding.html', {'page_title': 'Create Funding Scheme', 'tenders': tenders})

# --- ADMIN REQUESTS (Department/Category Approval) ---

# Displays pending administrative requests for department or category permissions
@staff_member_required
def admin_request_approvals(request):
    pending_requests = AdminRequest.objects.filter(status='pending').order_by('-created_at')
    approved_requests = AdminRequest.objects.filter(status='approved').order_by('-created_at')[:10]
    return render(request, 'approvals.html', {
        'page_title': 'Administrative Requests',
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'type': 'admin_requests'
    })

# Approves an administrative request for department/category creation
@staff_member_required
def approve_admin_request(request, request_id):
    if request.method == 'POST':
        admin_req = get_object_or_404(AdminRequest, id=request_id)
        remark = request.POST.get('remark', '')
        
        # Actually create the Department/Category if they don't exist
        Department.objects.get_or_create(name=admin_req.department_name)
        Category.objects.get_or_create(name=admin_req.category_name)
        
        admin_req.status = 'approved'
        admin_req.admin_remark = remark
        admin_req.save()
        
        Notification.objects.create(
            user=admin_req.user,
            message=f"Your request for {admin_req.department_name} department has been approved."
        )
        
        ActionLog.objects.create(
            admin_user=request.user,
            action_type="DEPARTMENT_APPROVAL",
            target_user=admin_req.user,
            target_department=admin_req.department_name,
            description=f"Approved department creation for {admin_req.department_name} / {admin_req.category_name}." + (f" Remark: {remark}" if remark else "")
        )
        messages.success(request, f"Request for {admin_req.department_name} approved.")

        # 📧 Send Status Email
        try:
            current_site = get_current_site(request)
            send_ebharat_email(
                subject="Administrative Request Approved",
                template_name="status_update_notification.html",
                context={
                    "user_name": admin_req.user.first_name or admin_req.user.username,
                    "activity_name": "Department/Category Creation Request",
                    "item_name": f"{admin_req.department_name} / {admin_req.category_name}",
                    "status": "approved",
                    "remark": remark,
                    "domain": current_site.domain,
                },
                recipient_list=[admin_req.user.email]
            )
        except Exception as e:
            print(f"Admin Req Approval Email failed: {e}")
    return redirect('coreadmin:admin_request_approvals')

# Rejects an administrative request with an official remark
@staff_member_required
def reject_admin_request(request, request_id):
    if request.method == 'POST':
        admin_req = get_object_or_404(AdminRequest, id=request_id)
        remark = request.POST.get('remark', '')
        
        admin_req.status = 'rejected'
        admin_req.admin_remark = remark
        admin_req.save()
        
        ActionLog.objects.create(
            admin_user=request.user,
            action_type="DEPARTMENT_REJECTION",
            target_user=admin_req.user,
            target_department=admin_req.department_name,
            description=f"Rejected department creation for {admin_req.department_name} / {admin_req.category_name}." + (f" Remark: {remark}" if remark else "")
        )
        messages.warning(request, f"Request for {admin_req.department_name} rejected.")

        # 📧 Send Status Email
        try:
            current_site = get_current_site(request)
            send_ebharat_email(
                subject="Administrative Request Update",
                template_name="status_update_notification.html",
                context={
                    "user_name": admin_req.user.first_name or admin_req.user.username,
                    "activity_name": "Department/Category Creation Request",
                    "item_name": f"{admin_req.department_name} / {admin_req.category_name}",
                    "status": "rejected",
                    "remark": remark,
                    "domain": current_site.domain,
                },
                recipient_list=[admin_req.user.email]
            )
        except Exception as e:
            print(f"Admin Req Rejection Email failed: {e}")
    return redirect('coreadmin:admin_request_approvals')

# Generates system-wide reports filterable by date or financial year
@staff_member_required
def system_reports(request):
    filter_type = request.GET.get('filter_type', 'all')
    date_val = request.GET.get('date')
    fy_val = request.GET.get('fy')
    
    tenders = Tenderss.objects.all()
    bids = TenderApplication.objects.all()
    
    import datetime
    
    if filter_type == 'date' and date_val:
        filter_date = datetime.datetime.strptime(date_val, '%Y-%m-%d').date()
        tenders = tenders.filter(created_at__date=filter_date)
        bids = bids.filter(applied_at__date=filter_date)
    elif filter_type == 'fy' and fy_val:
        start_year = int(fy_val)
        start_date = datetime.date(start_year, 4, 1)
        end_date = datetime.date(start_year + 1, 3, 31)
        tenders = tenders.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
        bids = bids.filter(applied_at__date__gte=start_date, applied_at__date__lte=end_date)
        
    tenders = tenders.order_by('-created_at')
    
    total_tenders = tenders.count()
    total_bids = bids.count()
    total_disbursed = bids.filter(status='awarded').aggregate(Sum('bid_amount'))['bid_amount__sum'] or 0
    
    return render(request, 'reports.html', {
        'page_title': 'System Reports',
        'tenders': tenders[:50], # Performance limit on preview
        'total_tenders': total_tenders,
        'total_bids': total_bids,
        'total_disbursed': total_disbursed,
        'filter_type': filter_type,
        'date_val': date_val,
        'fy_val': fy_val
    })

# Generates and downloads a landscape PDF system report based on current filters
# Generates and downloads a landscape PDF system report based on current filters
@staff_member_required
def download_report_pdf(request):
    filter_type = request.GET.get('filter_type', 'all')
    date_val = request.GET.get('date')
    fy_val = request.GET.get('fy')
    
    # Get full data with related fields for efficient A-Z Report Generation
    tenders = Tenderss.objects.all().prefetch_related('applications', 'applications__applicant')
    
    import datetime
    report_subtitle = "Full System Lifecycle Report"
    
    if filter_type == 'date' and date_val:
        filter_date = datetime.datetime.strptime(date_val, '%Y-%m-%d').date()
        tenders = tenders.filter(created_at__date=filter_date)
        report_subtitle = f"Period: {filter_date.strftime('%d %b %Y')}"
    elif filter_type == 'fy' and fy_val:
        start_year = int(fy_val)
        start_date = datetime.date(start_year, 4, 1)
        end_date = datetime.date(start_year + 1, 3, 31)
        tenders = tenders.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
        report_subtitle = f"Period: Financial Year {start_year}-{start_year+1}"
        
    tenders = tenders.order_by('-created_at')
    
    # Calculate scoped stats for the report
    total_tenders = tenders.count()
    from bids.models import TenderApplication
    scoped_bids = TenderApplication.objects.filter(tender__in=tenders)
    total_bids = scoped_bids.count()
    total_disbursed = scoped_bids.filter(status='awarded').aggregate(Sum('bid_amount'))['bid_amount__sum'] or 0
    
    return generate_system_report_pdf(tenders, total_tenders, total_bids, total_disbursed, report_subtitle, request.user)

# Log out the current user and redirect to login page
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out from the Control Center.")
    return redirect('accounts:login')

# Facilitates the reassignment of user roles for administrative purposes
@login_required
def allocate_user_role(request, profile_id):
    if request.method == 'POST':
        profile = get_object_or_404(UserProfile, id=profile_id)
        role = request.POST.get('role')
        if role:
            old_role = profile.get_role_display() if profile.role else 'None'
            profile.role = role
            profile.save()
            new_role = profile.get_role_display()
            
            ActionLog.objects.create(
                admin_user=request.user,
                action_type="ROLE_ALLOCATION",
                target_user=profile.user,
                description=f"Changed role from {old_role} to {new_role}."
            )
            
            Notification.objects.create(
                user=profile.user,
                message=f"Your account role has been updated to {new_role} by an Administrator."
            )

            # 📧 Send Role Update Email
            try:
                current_site = get_current_site(request)
                send_ebharat_email(
                    subject="Account Role Updated",
                    template_name="status_update_notification.html",
                    context={
                        "user_name": profile.user.first_name or profile.user.username,
                        "activity_name": "Account Profile Update",
                        "item_name": f"Role Allocation to {new_role}",
                        "status": "approved", # Role change is considered an administrative approval
                        "remark": f"Your role has been updated from {old_role} to {new_role}.",
                        "domain": current_site.domain,
                    },
                    recipient_list=[profile.user.email]
                )
            except Exception as e:
                # Log email error
                pass

            messages.success(request, f"Role updated successfully for {profile.user.username}.")
        else:
            messages.error(request, "No valid role selected.")
    return redirect('coreadmin:user_list')

# Displays a chronological record of all administrative actions performed in the system
@login_required
def action_history(request):
    logs = ActionLog.objects.all().order_by('-timestamp')
    return render(request, 'action_history.html', {'page_title': 'System Audit Log', 'logs': logs})

# ==============================================================================
# NOTICE MANAGEMENT VIEWS
# ==============================================================================

# Renders a list of all system notices and announcements, as well as important dates
@login_required
def notice_list(request):
    notices = Notice.objects.all().order_by('-created_at')
    events = ImportantEvent.objects.all().order_by('-event_date')
    return render(request, 'manage_notices.html', {
        'page_title': 'Communication Hub', 
        'notices': notices,
        'events': events
    })

# Creates and publishes a new system-wide notice or announcement
@login_required
def create_notice(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        is_pinned = request.POST.get('is_pinned') == 'on'
        
        Notice.objects.create(
            title=title,
            description=description,
            category=category,
            is_pinned=is_pinned,
            created_by=request.user
        )
        messages.success(request, f"Notice '{title}' published successfully.")
        
        ActionLog.objects.create(
            admin_user=request.user,
            action_type="NOTICE_CREATION",
            description=f"Created a new notice: {title} ({category})"
        )
        
    return redirect('coreadmin:notice_list')

# Modifies the details of an existing system notice
@login_required
def edit_notice(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)
    if request.method == 'POST':
        notice.title = request.POST.get('title')
        notice.description = request.POST.get('description')
        notice.category = request.POST.get('category')
        notice.is_pinned = request.POST.get('is_pinned') == 'on'
        notice.save()
        
        ActionLog.objects.create(
            admin_user=request.user,
            action_type="NOTICE_UPDATED",
            description=f"Updated notice: {notice.title}"
        )
        messages.info(request, f"Notice '{notice.title}' updated.")
    return redirect('coreadmin:notice_list')

# Permanently deletes a specific system notice
@login_required
def delete_notice(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)
    title = notice.title
    notice.delete()
    
    ActionLog.objects.create(
        admin_user=request.user,
        action_type="NOTICE_DELETION",
        description=f"Deleted notice: {title}"
    )
    
    messages.warning(request, f"Notice '{title}' deleted.")
    return redirect('coreadmin:notice_list')

# --- IMPORTANT EVENT MANAGEMENT ---

@login_required
def create_event(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        e_date = request.POST.get('event_date')
        e_time = request.POST.get('event_time')
        desc = request.POST.get('description')
        e_type = request.POST.get('event_type', 'info')
        
        ImportantEvent.objects.create(
            title=title,
            event_date=e_date,
            event_time=e_time,
            description=desc,
            event_type=e_type
        )
        
        ActionLog.objects.create(
            admin_user=request.user,
            action_type="EVENT_CREATION",
            description=f"Added important date: {title} on {e_date}"
        )
        messages.success(request, f"Important date '{title}' added.")
    return redirect('coreadmin:notice_list')

@login_required
def edit_event(request, event_id):
    event = get_object_or_404(ImportantEvent, id=event_id)
    if request.method == 'POST':
        event.title = request.POST.get('title')
        event.event_date = request.POST.get('event_date')
        event.event_time = request.POST.get('event_time')
        event.description = request.POST.get('description')
        event.event_type = request.POST.get('event_type')
        event.save()
        
        ActionLog.objects.create(
            admin_user=request.user,
            action_type="EVENT_UPDATED",
            description=f"Updated event: {event.title}"
        )
        messages.info(request, f"Event '{event.title}' updated.")
    return redirect('coreadmin:notice_list')

@login_required
def delete_event(request, event_id):
    event = get_object_or_404(ImportantEvent, id=event_id)
    title = event.title
    event.delete()
    
    ActionLog.objects.create(
        admin_user=request.user,
        action_type="EVENT_DELETION",
        description=f"Deleted event: {title}"
    )
    messages.warning(request, f"Event '{title}' deleted.")
    return redirect('coreadmin:notice_list')

# --- ENQUIRY MANAGEMENT ---

@staff_member_required
def enquiry_list(request):
    enquiries = Enquiry.objects.all().order_by('-created_at')
    return render(request, 'manage_enquiries.html', {
        'page_title': 'Enquiries & Support',
        'enquiries': enquiries
    })

@staff_member_required
def reply_enquiry(request, enquiry_id):
    if request.method == 'POST':
        enquiry = get_object_or_404(Enquiry, id=enquiry_id)
        reply_message = request.POST.get('reply_message')
        
        # Send Email
        context = {
            'full_name': enquiry.full_name,
            'reply_message': reply_message,
            'original_subject': enquiry.subject,
            'original_message': enquiry.message
        }
        
        success = send_ebharat_email(
            subject=f"RE: {enquiry.subject}",
            template_name='enquiry_reply.html',
            context=context,
            recipient_list=[enquiry.email]
        )
        
        if success:
            enquiry.status = 'replied'
            enquiry.admin_reply = reply_message
            enquiry.save()
            
            ActionLog.objects.create(
                admin_user=request.user,
                action_type="ENQUIRY_REPLY",
                description=f"Replied to enquiry from {enquiry.full_name}"
            )
            messages.success(request, f"Reply sent successfully to {enquiry.email}")
        else:
            messages.error(request, "Failed to send email. Please check SMTP settings.")
            
    return redirect('coreadmin:enquiry_list')

# Renders and handles administrative profile settings and password changes
@staff_member_required
def admin_profile(request):
    from django.contrib.auth.forms import PasswordChangeForm
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_profile':
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.email = request.POST.get('email', '')
            request.user.save()
            messages.success(request, "Your profile details have been successfully updated.")
            return redirect('coreadmin:admin_profile')
            
        elif action == 'change_password':
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Your password was successfully updated.")
                return redirect('coreadmin:admin_profile')
            else:
                for error_list in form.errors.values():
                    for error in error_list:
                        messages.error(request, error)
                    
    else:
        form = PasswordChangeForm(request.user)
        
    return render(request, 'admin_profile.html', {
        'page_title': 'Profile Settings',
        'password_form': form,
    })

# Displays a specialized list of Earnest Money Deposit (EMD) payments and refunds
@staff_member_required
def emd_escrow_list(request):
    applications = TenderApplication.objects.filter(payment_status__in=['paid', 'refunded']).select_related('tender', 'applicant').order_by('-applied_at')
    
    active_escrow = applications.filter(payment_status='paid', tender__status='open').aggregate(total=Sum('tender__emd_amount'))['total'] or 0
    total_refunded = applications.filter(payment_status='refunded').aggregate(total=Sum('tender__emd_amount'))['total'] or 0
    total_collected = applications.filter(payment_status='paid').aggregate(total=Sum('tender__emd_amount'))['total'] or 0
    
    return render(request, 'emd_escrow.html', {
        'page_title': 'EMD Escrow Management',
        'applications': applications,
        'active_escrow': active_escrow,
        'total_refunded': total_refunded,
        'total_collected': total_collected
    })

