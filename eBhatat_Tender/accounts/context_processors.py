from .models import Notification, UserProfile, AdminRequest

def notifications(request):
    """
    Context processor to add notifications and administrative pending counts 
    to all templates globally.
    """
    if request.user.is_authenticated:
        user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
        unread_count = user_notifications.filter(is_read=False).count()

        # Dashboard Sidebar Badges (calculated once per request)
        stats = {
            'notifications': user_notifications,
            'unread_count': unread_count,
            'pending_enquiries_count': 0,
            'pending_user_approvals': 0,
            'pending_admin_req_count': 0,
            'pending_app_approvals': 0,
            'pending_funding_count': 0,
        }

        if request.user.is_staff:
            try:
                # 1. Enquiries
                from public.models import Enquiry
                stats['pending_enquiries_count'] = Enquiry.objects.filter(status='pending').count()
                
                # 2. User/Profile Approvals
                stats['pending_user_approvals'] = UserProfile.objects.filter(status='pending').exclude(user__is_superuser=True).exclude(user__is_staff=True).count()
                
                # 3. Tender Requests
                stats['pending_admin_req_count'] = AdminRequest.objects.filter(status='pending').count()
                
                # 4. Bid Applications
                from bids.models import TenderApplication
                stats['pending_app_approvals'] = TenderApplication.objects.filter(status='pending').count()
                
                # 5. Funding Applications
                from funding.models import FundingApplication
                stats['pending_funding_count'] = FundingApplication.objects.filter(status='pending').count()
                
            except Exception:
                pass

        return stats

    return {
        'notifications': [],
        'unread_count': 0,
        'pending_enquiries_count': 0,
        'pending_user_approvals': 0,
        'pending_admin_req_count': 0,
        'pending_app_approvals': 0,
        'pending_funding_count': 0,
    }
