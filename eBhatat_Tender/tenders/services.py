from django.utils import timezone
from .models import Tenderss

def auto_close_expired_tenders():
    """
    Finds all 'open' tenders where the closing date has passed and marks them as 'closed'.
    """
    today = timezone.now().date()
    updated_count = Tenderss.objects.filter(
        closing_date__lt=today, 
        status='open'
    ).update(status='closed')
    return updated_count

def mask_id(value):
    """
    Utility to mask sensitive ID numbers (e.g., GST, Gov ID).
    Shows only the last 4 characters.
    """
    if not value: return ""
    val = str(value)
    mask_count = max(7, len(val) - 4)
    return "*" * mask_count + val[-4:]
