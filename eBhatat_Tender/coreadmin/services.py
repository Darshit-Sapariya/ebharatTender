from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from tenders.models import Tenderss
from bids.models import TenderApplication
from accounts.models import UserProfile, AdminRequest
from funding.models import FundingApplication
from .models import ActionLog

def calculate_delta(current, previous):
    """
    Standard percentage change calculation between current and previous values.
    """
    if previous == 0:
        return 100 if current > 0 else 0
    return round(((current - previous) / previous) * 100)

def get_dashboard_stats():
    """
    Consolidated service to fetch and calculate all dashboard metrics.
    """
    now = timezone.now()
    prev_30_days = now - timedelta(days=30)
    
    # Total Tenders
    total_tenders = Tenderss.objects.count()
    prev_total_tenders = Tenderss.objects.filter(created_at__lt=prev_30_days).count()
    tenders_delta = calculate_delta(total_tenders, prev_total_tenders)
    active_tenders = Tenderss.objects.filter(status='open').count()
    
    # Total Disbursed (Awarded Bid Amounts)
    total_awarded_val = TenderApplication.objects.filter(status='awarded').aggregate(total=Sum('bid_amount'))['total'] or 0
    prev_awarded_val = TenderApplication.objects.filter(status='awarded', applied_at__lt=prev_30_days).aggregate(total=Sum('bid_amount'))['total'] or 0
    disbursed_delta = calculate_delta(float(total_awarded_val), float(prev_awarded_val))
    
    # Pending Reviews
    pending_user_approvals = UserProfile.objects.filter(status='pending').exclude(user__is_superuser=True).exclude(user__is_staff=True).count()
    pending_app_approvals = TenderApplication.objects.filter(status='pending').count()
    total_pending = pending_user_approvals + pending_app_approvals
    
    prev_pending_users = UserProfile.objects.filter(status='pending', created_at__lt=prev_30_days).exclude(user__is_superuser=True).exclude(user__is_staff=True).count()
    prev_pending_apps = TenderApplication.objects.filter(status='pending', applied_at__lt=prev_30_days).count()
    prev_total_pending = prev_pending_users + prev_pending_apps
    pending_delta = calculate_delta(total_pending, prev_total_pending)
    
    # Registered Vendors
    total_vendors = UserProfile.objects.filter(role='bidder').count()
    prev_total_vendors = UserProfile.objects.filter(role='bidder', created_at__lt=prev_30_days).count()
    vendors_delta = calculate_delta(total_vendors, prev_total_vendors)
    
    # Contracts Executed
    contracts_executed = Tenderss.objects.filter(status='awarded').count()
    prev_contracts_executed = Tenderss.objects.filter(status='awarded', created_at__lt=prev_30_days).count()
    contracts_delta = calculate_delta(contracts_executed, prev_contracts_executed)
    
    # Bids this month
    bids_this_month = TenderApplication.objects.filter(applied_at__month=now.month, applied_at__year=now.year).count()
    
    # EMD Escrow (Paid EMD for open tenders)
    emd_escrow = TenderApplication.objects.filter(tender__status='open', payment_status='paid').aggregate(total=Sum('tender__emd_amount'))['total'] or 0
    prev_emd_escrow = TenderApplication.objects.filter(tender__status='open', payment_status='paid', applied_at__lt=prev_30_days).aggregate(total=Sum('tender__emd_amount'))['total'] or 0
    emd_delta = calculate_delta(float(emd_escrow), float(prev_emd_escrow))
    active_holds = Tenderss.objects.filter(status='open').count() 
    
    # Approval Rate
    total_apps = TenderApplication.objects.count()
    approved_apps = TenderApplication.objects.filter(status='approved').count()
    approval_rate = round((approved_apps / total_apps * 100)) if total_apps > 0 else 0
    
    prev_total_apps = TenderApplication.objects.filter(applied_at__lt=prev_30_days).count()
    prev_approved_apps = TenderApplication.objects.filter(status='approved', applied_at__lt=prev_30_days).count()
    prev_approval_rate = round((prev_approved_apps / prev_total_apps * 100)) if prev_total_apps > 0 else 0
    approval_delta = calculate_delta(approval_rate, prev_approval_rate)
    
    # Audit Logs Today
    today = timezone.localdate()
    yesterday = today - timedelta(days=1)
    audit_logs_today = ActionLog.objects.filter(timestamp__date=today).count()
    prev_audit_logs_today = ActionLog.objects.filter(timestamp__date=yesterday).count()
    audit_delta = calculate_delta(audit_logs_today, prev_audit_logs_today)
    
    return {
        'total_tenders': total_tenders,
        'tenders_delta': tenders_delta,
        'active_tenders': active_tenders,
        'total_vendors': total_vendors,
        'vendors_delta': vendors_delta,
        'total_awarded_val': total_awarded_val,
        'disbursed_delta': disbursed_delta,
        'total_pending': total_pending,
        'pending_delta': pending_delta,
        'pending_user_approvals': pending_user_approvals,
        'pending_app_approvals': pending_app_approvals,
        'bids_this_month': bids_this_month,
        'contracts_executed': contracts_executed,
        'contracts_delta': contracts_delta,
        'emd_escrow': emd_escrow,
        'emd_delta': emd_delta,
        'active_holds': active_holds,
        'approval_rate': approval_rate,
        'approval_delta': approval_delta,
        'audit_logs_today': audit_logs_today,
        'audit_delta': audit_delta,
    }
